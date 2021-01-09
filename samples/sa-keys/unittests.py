# Create environment variables: GCP_SA_0, GCP_SA_1, SECRET, GCP_PROJECT, GOOGLE_APPLICATION_CREDENTIALS
# GOOGLE_APPLICATION_CREDENTIALS contains the SA key with roles in infra/svc-sa-roles.yaml

import json
import os
import re
import sys
import time
import unittest
from random import randrange

from google.cloud import secretmanager

import backend
from manager import SA_REGEX
from manager import app

SHORT_DAYS = 0.000694444  # 1 minute
LONG_DAYS = 90
FAKE_PROJECT = 'fake_projectid'
FAKE_SA = f"fake-sa@{FAKE_PROJECT}.iam.gserviceaccount.com"
FAKE_KEY = '70e13990a5d2a62b35e89910e10c218a4944843f'
SECRET_NAME_PREFIX = 'hil_'


class BackendTests(unittest.TestCase):
    # executed after each test
    def tearDown(self):
        pass

    def test_audit_sa(self):
        result = backend.audit_secrets_sa(os.environ['GCP_PROJECT'], f"^{os.environ['SECRET']}$")
        self.assertIsNotNone(result)
        print(result)

    def test_audit_sa_batch(self):
        # use identical secrets to simulate multiple different secrets
        secrets = []
        count = 3
        for _ in range(count):
            secrets.append(os.environ['SECRET'])

        results = backend.audit_secrets_sa_batch(os.environ['GCP_PROJECT'], secrets)
        self.assertEqual(len(results), count)

    def test_audit_fake_sa(self):
        key_content = {'client_email': FAKE_SA, 'private_key_id': FAKE_KEY}
        payload = str.encode(json.dumps(key_content))
        secret, secret_id, sm_client = self.create_secret(payload)

        result = backend.audit_secret_sa(os.environ['GCP_PROJECT'], secret_id)
        self.assertIsNotNone(result)
        self.assertIn('delete', result[0])
        # delete the secret as it contains a non-existing service account key
        sm_client.delete_secret(request={"name": secret.name})

    def test_audit_fake_secret(self):
        secret, secret_id, sm_client = self.create_secret(b"garbage")
        result = backend.audit_secret_sa(os.environ['GCP_PROJECT'], secret_id)
        self.assertIsNotNone(result)
        sm_client.delete_secret(request={"name": secret.name})

    @staticmethod
    def create_secret(content):
        sm_client = secretmanager.SecretManagerServiceClient()
        secret_id = f"{SECRET_NAME_PREFIX}junk-{randrange(sys.maxsize)}"
        secret = sm_client.create_secret(
            request={
                "parent": f"projects/{os.environ['GCP_PROJECT']}",
                "secret_id": secret_id,
                "secret": {"replication": {"automatic": {}}},
            }
        )
        version = sm_client.add_secret_version(
            request={
                "parent": secret.name,
                "payload": {"data": content}}
        )
        return secret, secret_id, sm_client

    def test_audit_secret(self):
        result = backend.audit_secret_sa(os.environ['GCP_PROJECT'], os.environ['SECRET'])
        self.assertIsNotNone(result)


class ManagerTests(unittest.TestCase):

    # executed prior to each test
    def setUp(self):
        self.app = app.test_client()

    # executed after each test
    def tearDown(self):
        pass

    def test_audit_sa_batch(self):
        body = {
            'secret-regex': f"^{os.environ['SECRET']}$"
        }
        results = self.app.put(f"/projects/{os.environ['GCP_PROJECT']}/audit-secrets", data=json.dumps(body),
                               content_type='application/json')
        self.assertEqual(len(results.json), 1)

    def test_delete_missing_sa_keys(self):
        self.assertIsNotNone(app)
        delete_key_response = self.app.delete('/sa-keys')
        self.assertEqual(delete_key_response.status_code, 400)

    def test_delete_fake_sa_keys(self):
        self.assertIsNotNone(app)
        body = {
            'sa-key-names': f"projects/{FAKE_PROJECT}/serviceAccounts/{FAKE_SA}/keys/{FAKE_KEY}"
        }
        delete_key_response = self.app.delete('/sa-keys', data=body)
        self.assertEqual(delete_key_response.status_code, 404)

    def test_get_fake_sa_keys(self):
        get_key_response = self.app.get(f"/sa/{FAKE_SA}/keys")
        self.assertEqual(get_key_response.status_code, 404)

    def test_get_fake_sa_key_days_older(self):
        get_user_managed_key_response = self.app.get(f"/sa/{FAKE_SA}/keys-days-older/0")
        self.assertEqual(get_user_managed_key_response.status_code, 404)

    def test_gen_get_delete_sa_keys(self):
        self.assertIsNotNone(app)
        # generate a new key first
        body = {
            'secret_name_prefix': SECRET_NAME_PREFIX,
            'GCP_SAs': f"{os.environ['GCP_SA_0']}"
        }
        create_key_response = self.app.put(f"/gen-sa-keys-add-secrets/delete-keys-days-old/{LONG_DAYS}", data=body)
        self.assertEqual(create_key_response.status_code, 200)
        self.assertEqual(len(create_key_response.json), 1)

        # get the key
        get_user_managed_key_response = self.app.get(f"/sa/{os.environ['GCP_SA_0']}/keys-days-older/0")
        self.assertEqual(get_user_managed_key_response.status_code, 200)
        for key in get_user_managed_key_response.json['keys']:
            self.assertEqual(key['keyType'], 'USER_MANAGED', 'keyType is NOT USER_MANAGED')

        get_key_response = self.app.get(f"/sa/{os.environ['GCP_SA_0']}/keys")
        self.assertEqual(get_key_response.status_code, 200)

        # find the key ID then delete the key
        self.assertIn('private_key_id', create_key_response.json[0][backend.key_thread_result],
                      'response JSON array item 0 .result missing key private_key_id')
        from http import HTTPStatus
        self.assertEqual(HTTPStatus.OK, create_key_response.json[0][backend.key_thread_result_code],
                         'response JSON array item 0 .code not 200')
        private_key_id = create_key_response.json[0][backend.key_thread_result]['private_key_id']
        regex_search_result = re.search(SA_REGEX, os.environ['GCP_SA_0'])
        self.assertIsNotNone(regex_search_result, 'failed to find project ID ')
        key = f"projects/{regex_search_result.group(2)}/serviceAccounts/{os.environ['GCP_SA_0']}/keys/{private_key_id}"
        body = {
            'sa-key-names': key
        }
        delete_key_response = self.app.delete('/sa-keys', data=body)
        self.assertEqual(delete_key_response.status_code, 200, f"failed deleting key {key}")

    def test_delete_fake_sa_keys_older(self):
        self.assertIsNotNone(app)
        delete_key_response = self.app.delete(
            f"/sa/{FAKE_SA}/keys-days-older/{SHORT_DAYS}")
        self.assertEqual(delete_key_response.status_code, 404)

    def test_delete_sa_keys_days_older(self):
        self.assertIsNotNone(app)
        # generate a new key first
        body = {
            'secret_name_prefix': SECRET_NAME_PREFIX,
            'GCP_SAs': f"{os.environ['GCP_SA_0']}"
        }
        create_key_response = self.app.put(f"/gen-sa-keys-add-secrets/delete-keys-days-old/{LONG_DAYS}", data=body)
        self.assertEqual(create_key_response.status_code, 200)
        self.assertEqual(len(create_key_response.json), 1)
        time.sleep(60 * 60 * 24 * SHORT_DAYS)
        delete_key_response = self.app.delete(f"/sa/{os.environ['GCP_SA_0']}/keys-days-older/{SHORT_DAYS}")
        self.assertEqual(delete_key_response.status_code, 200)

    def test_health(self):
        self.assertIsNotNone(app)
        response = self.app.get('/health', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_gen_sa_keys_add_secrets_no_form_data(self):
        self.assertIsNotNone(app)
        response = self.app.put(f"/gen-sa-keys-add-secrets/delete-keys-days-old/{LONG_DAYS}", follow_redirects=True)
        self.assertEqual(response.status_code, 400)

    def test_gen_sa_keys_add_secrets_fake_sa(self):
        self.assertIsNotNone(app)
        body = {
            'secret_name_prefix': SECRET_NAME_PREFIX,
            'GCP_SAs': FAKE_SA
        }
        response = self.app.put(f"/gen-sa-keys-add-secrets/delete-keys-days-old/{LONG_DAYS}", data=body)
        self.assertEqual(response.status_code, 404)

    def test_gen_sa_keys_add_secrets_no_secret_project_id(self):
        self.assertIsNotNone(app)
        body = {
            'secret_name_prefix': SECRET_NAME_PREFIX,
            'GCP_SAs': FAKE_SA
        }
        response = self.app.put(f"/gen-sa-keys-add-secrets/delete-keys-days-old/{LONG_DAYS}", data=body)
        self.assertEqual(response.status_code, 404)

    # test generate new keys for the service accounts and delete keys older than 1 minute
    def test_gen_sa_keys_add_secrets(self):
        self.assertIsNotNone(app)
        body = {
            'secret_name_prefix': SECRET_NAME_PREFIX,
            'GCP_SAs': f"{os.environ['GCP_SA_0']},{os.environ['GCP_SA_1']}"
        }
        response = self.app.put(f"/gen-sa-keys-add-secrets/delete-keys-days-old/{SHORT_DAYS}", data=body)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)


if __name__ == "__main__":
    unittest.main()
