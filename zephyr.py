import configparser
import json

import requests

config = configparser.ConfigParser()
config.read('config.ini')
ZAPI = config['Zephyr Scale']
ZAPI_SECRET_KEY = ZAPI['zapi_secret_key']
ZAPI_BASE_URL = ZAPI['zapi_base_url']
headers = {"Authorization": ZAPI_SECRET_KEY}


def get_test_cases():
    response = requests.get(f"{ZAPI_BASE_URL}/testcases?maxResults=3000", headers=headers)
    test_cases = json.loads(response.content.decode('UTF-8'))
    return test_cases['values']


def get_test_case_steps(key):
    response = requests.get(f"{ZAPI_BASE_URL}/testcases/{key}/teststeps", headers=headers)
    test_steps = json.loads(response.content.decode('UTF-8'))
    try:
        steps = test_steps['values']
    except:
        response = requests.get(f"{ZAPI_BASE_URL}/testcases/{key}/testscript", headers=headers)
        test_steps = json.loads(response.content.decode('UTF-8'))
        return test_steps
    return steps


def get_folder_name(id):
    response = requests.get(f"{ZAPI_BASE_URL}/folders/{id}", headers=headers)
    folder_details = json.loads(response.content.decode('UTF-8'))
    return folder_details['name']
