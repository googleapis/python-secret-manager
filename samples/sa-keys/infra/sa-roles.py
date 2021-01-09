"""
Create service account and bind predefined roles; enable cloud APIs;
"""
SA_PREFIX = 'sa/'
APIS_PREFIX = 'apis/'


def GenerateConfig(context):
    project_id = context.env['project']
    service_account = context.properties['service-account']

    resources = [
        {
            'name': SA_PREFIX + service_account,
            'type': 'iam.v1.serviceAccount',
            'properties': {
                'accountId': service_account,
                'serviceAccount': {
                    'description': context.properties['service-account-desc'],
                    'displayName': service_account,
                },
                'projectId': project_id
            }
        }
    ]
    roles = context.properties["roles"]
    for role in roles:
        resources.append(
            {
                'name': role,
                'type': 'gcp-types/cloudresourcemanager-v1:virtual.projects.iamMemberBinding',
                'properties': {
                    'resource': project_id,
                    'role': role,  # predefined IAM role
                    'member': 'serviceAccount:$(ref.' + SA_PREFIX + service_account + '.email)'
                },
                'metadata': {
                    'dependsOn': [SA_PREFIX + service_account]
                }
            }
        )

    apis = context.properties["apis"]
    for api in apis:
        resources.append(
            {
                'name': APIS_PREFIX + api,
                'type': 'deploymentmanager.v2.virtual.enableService',
                'properties': {
                    'consumerId': 'project:' + context.env['project'],
                    'serviceName': api + ".googleapis.com"
                }
            }
        )

    return {'resources': resources}
