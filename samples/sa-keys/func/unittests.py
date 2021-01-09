# Create environment variables: PROJECT_ID, GCP_SA, GOOGLE_APPLICATION_CREDENTIALS
# GOOGLE_APPLICATION_CREDENTIALS contains the SA key with roles in infra/func-sa-roles.yaml

import json
import sys
import unittest
from random import randrange

from google.cloud import firestore

from func.main import get_or_init_config
from func.main import key_SA_regex
from func.main import key_abort_level
from func.main import key_cloud_run_subpath
from func.main import key_cloud_run_url
from func.main import key_cloud_run_verb
from func.main import key_payload
from func.main import key_projectid_regex
from func.main import key_secret_project_id
from func.main import verify_config

FAKE_PROJECT = 'fake_project'
CLOUD_RUN_URL = 'https://cloud-run-test-url'


class FuncTests(unittest.TestCase):

    # executed prior to each test
    def setUp(self):
        self.firestore_client = firestore.Client()
        self.SA = "good-sa"

    # executed after each test
    def tearDown(self):
        pass

    def test_init_config(self):
        collection = f"unittests-{randrange(sys.maxsize)}"
        config_doc_id = 'config'
        config, config_doc_path = get_or_init_config(collection, config_doc_id)
        self.assertIsNotNone(config)
        self.assertIsNotNone(config_doc_path)
        delete_collection(self.firestore_client.collection(collection), 1)

    def test_verify_config(self):
        # dependency injection for cloud function's config
        subpath = "gen-sa-keys-add-secrets/delete-keys-days-old/90"
        verb = "PUT"

        def get_config_mock():
            return {
                       key_SA_regex: f"^{self.SA}@{FAKE_PROJECT}\.iam\.gserviceaccount\.com$",
                       key_projectid_regex: f"^{FAKE_PROJECT}$",
                       key_cloud_run_url: CLOUD_RUN_URL,
                       key_cloud_run_verb: verb,
                       key_cloud_run_subpath: subpath,
                       key_secret_project_id: FAKE_PROJECT
                   }, \
                   "func/unittests"

        result = verify_config(f"{self.SA}@{FAKE_PROJECT}.iam.gserviceaccount.com",
                               FAKE_PROJECT,
                               get_config_func=get_config_mock)
        self.assertIsNotNone(result)
        print(json.dumps(result))
        self.assertEqual(0, result[key_abort_level])
        self.assertEqual(CLOUD_RUN_URL, result[key_payload][key_cloud_run_url])
        self.assertEqual(FAKE_PROJECT, result[key_payload][key_secret_project_id])
        self.assertEqual(verb, result[key_payload][key_cloud_run_verb])
        self.assertEqual(subpath, result[key_payload][key_cloud_run_subpath])

    def test_verify_config_missing_fields(self):
        # dependency injection for cloud function's config
        subpath = "gen-sa-keys-add-secrets/delete-keys-days-old/90"
        verb = "PUT"

        def get_config_missing_url():
            return {
                       key_SA_regex: f"^{self.SA}@{FAKE_PROJECT}\.iam\.gserviceaccount\.com$",
                       key_projectid_regex: f"^{FAKE_PROJECT}$",
                       key_cloud_run_verb: verb,
                       key_cloud_run_subpath: subpath,
                       key_secret_project_id: FAKE_PROJECT
                   }, \
                   "func/unittests"

        result = verify_config(f"{self.SA}@{FAKE_PROJECT}.iam.gserviceaccount.com",
                               FAKE_PROJECT,
                               get_config_func=get_config_missing_url)
        self.assertIsNotNone(result)
        print(json.dumps(result))
        self.assertNotEqual(0, result[key_abort_level])

        def get_config_missing_verb():
            return {
                       key_SA_regex: f"^{self.SA}@{FAKE_PROJECT}\.iam\.gserviceaccount\.com$",
                       key_projectid_regex: f"^{FAKE_PROJECT}$",
                       key_cloud_run_url: CLOUD_RUN_URL,
                       key_cloud_run_subpath: subpath,
                       key_secret_project_id: FAKE_PROJECT
                   }, \
                   "func/unittests"

        result = verify_config(f"{self.SA}@{FAKE_PROJECT}.iam.gserviceaccount.com",
                               FAKE_PROJECT,
                               get_config_func=get_config_missing_verb)
        self.assertIsNotNone(result)
        print(json.dumps(result))
        self.assertNotEqual(0, result[key_abort_level])

        def get_config_missing_subpath():
            return {
                       key_SA_regex: f"^{self.SA}@{FAKE_PROJECT}\.iam\.gserviceaccount\.com$",
                       key_projectid_regex: f"^{FAKE_PROJECT}$",
                       key_cloud_run_url: CLOUD_RUN_URL,
                       key_cloud_run_verb: verb,
                       key_secret_project_id: FAKE_PROJECT
                   }, \
                   "func/unittests"

        result = verify_config(f"{self.SA}@{FAKE_PROJECT}.iam.gserviceaccount.com",
                               FAKE_PROJECT,
                               get_config_func=get_config_missing_subpath)
        self.assertIsNotNone(result)
        print(json.dumps(result))
        self.assertNotEqual(0, result[key_abort_level])

        def get_config_missing_regex():
            return {
                       key_SA_regex: f"^{self.SA}@{FAKE_PROJECT}\.iam\.gserviceaccount\.com$",
                       key_cloud_run_subpath: subpath,
                       key_cloud_run_url: CLOUD_RUN_URL,
                       key_cloud_run_verb: verb,
                       key_secret_project_id: FAKE_PROJECT
                   }, \
                   "func/unittests"

        result = verify_config(f"{self.SA}@{FAKE_PROJECT}.iam.gserviceaccount.com",
                               FAKE_PROJECT,
                               get_config_func=get_config_missing_regex)
        self.assertIsNotNone(result)
        print(json.dumps(result))
        self.assertNotEqual(0, result[key_abort_level])

        def get_config_missing_secret():
            return {
                       key_SA_regex: f"^{self.SA}@{FAKE_PROJECT}\.iam\.gserviceaccount\.com$",
                       key_cloud_run_subpath: subpath,
                       key_cloud_run_url: CLOUD_RUN_URL,
                       key_cloud_run_verb: verb,
                       key_projectid_regex: f"^{FAKE_PROJECT}$"
                   }, \
                   "func/unittests"

        result = verify_config(f"{self.SA}@{FAKE_PROJECT}.iam.gserviceaccount.com",
                               FAKE_PROJECT,
                               get_config_func=get_config_missing_secret)
        self.assertIsNotNone(result)
        print(json.dumps(result))
        self.assertNotEqual(0, result[key_abort_level])


def delete_collection(coll_ref, batch_size):
    docs = coll_ref.limit(batch_size).stream()
    deleted = 0

    for doc in docs:
        print(f'Deleting doc {doc.id} => {doc.to_dict()}')
        doc.reference.delete()
        deleted = deleted + 1

    if deleted >= batch_size:
        return delete_collection(coll_ref, batch_size)
