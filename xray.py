import configparser
import json

import requests
from gql.transport.aiohttp import AIOHTTPTransport
from gql import Client, gql

config = configparser.ConfigParser()
config.read('config.ini')
XRAY = config['XRay']
XRAY_BASE_URL = XRAY['xray_base_url']

auth_data = {"client_id": XRAY['xray_client_id'], "client_secret": XRAY['xray_client_secret']}


class Xray:
    def __init__(self, project_key):
        self.project_key = project_key
        response = requests.post(f"{XRAY_BASE_URL}/authenticate", data=auth_data)
        self.auth_token = response.json()
        self.header = {'Authorization': f'Bearer {self.auth_token}'}

        transport = AIOHTTPTransport(
            url=f"{XRAY_BASE_URL}/graphql",
            headers=self.header
        )
        # Create a GraphQL client using the selected transport
        self.client = Client(transport=transport, fetch_schema_from_transport=True)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            print("Exception has occurred check logs - Intended action has failed")

    def create_folder(self, folder_name):
        self.get_project_settings()
        query = gql("""mutation ($projectId: String!, $path: String!){
        createFolder(
            projectId: $projectId,
            path:  $path
        ) {
            folder {
                name
                path
                testsCount
            }
            warnings
        }
        }""")
        params = {"projectId": self.project_id, "path": folder_name}
        try:
            self.client.execute(query, variable_values=params)
        except:
            f"Folder {folder_name} failed to create"

    def get_project_settings(self):

        query = gql("""
        query{
                getProjectSettings (projectIdOrKey: "%s") {
                projectId,
            }
            }
        """ % self.project_key
                    )
        result = self.client.execute(query)
        self.project_id = result['getProjectSettings']['projectId']

    def create_test_cases(self, payload):
        response = requests.post(f"{XRAY_BASE_URL}/import/test/bulk", headers=self.header, json=json.loads(payload))
        content = json.loads(response.content.decode('UTF-8'))
        print(
            f"Job ID is {content['jobId']} check status with https://xray.cloud.getxray.app/api/v1/import/test/bulk/{content['jobId']}/status")
        print(f"curl --location --request GET 'https://xray.cloud.getxray.app/api/v1/import/test/bulk/{content['jobId']}/status' \
                                                        \ --header f'Authorization: Bearer {self.auth_token}'")
        return content['jobId'], self.auth_token

