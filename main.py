import configparser
import json
import re

from xray import Xray
from zephyr import get_test_cases, get_test_case_steps, get_folder_name

config = configparser.ConfigParser()
config.read('config.ini')
CLEANR = re.compile('(<.*?>)')


def get_folder_list(test_cases):
    folders = []
    for i in test_cases:
        try:
            folders.append(get_folder_name(i['folder']['id']))
        except:
            folders.append('Generic')

    folders = list(dict.fromkeys(folders))

    return folders


def create_folders(test_cases):
    folders = get_folder_list(test_cases)
    with Xray(project_key=config['Params']['project']) as x:
        for i in folders:
            Xray.create_folder(x, i)


def main():
    test_case_list = []
    test_cases = get_test_cases()
    create_folders(test_cases)
    for i in test_cases:
        steps = get_test_case_steps(i['key'])
        try:
            folder_name = get_folder_name(i['folder']['id'])
        except:
            folder_name = 'Generic'
        summary = re.sub(CLEANR, '', i['name'])
        if 'type' in steps and steps['type'] == 'bdd':
            test_case_xray = {
                                 "testtype": "Cucumber",
                                 "fields": {
                                     "summary": summary,
                                     "project": {"key": "PD"}
                                 },
                                 "gherkin_def": steps['text'],
                                 "xray_test_repository_folder": folder_name
                             },
        else:
            steps_object = []
            for s in steps:
                try:
                    if s['inline']['description']:
                        action = re.sub(CLEANR, '', s['inline']['description']).replace('"', "").replace("&nbsp;",
                                                                                                         "").replace(
                            "&amp;", "")
                    else:
                        action = "No action in migration"
                except:
                    action = "No action in migration"

                try:
                    if s['inline']['testData']:
                        data = s['inline']['testData']
                    else:
                        data = "No data in migration"
                except:
                    data = "No data in migration"

                try:
                    if s['inline']['expectedResult']:
                        result = re.sub(CLEANR, '', s['inline']['expectedResult']).replace('"', "").replace("&nbsp;",
                                                                                                            "").replace(
                            "&amp;", "")
                    else:
                        result = "No expected in migration"
                except:
                    result = "No expected in migration"

                steps_object.append({
                    "action": action,
                    "data": data,
                    "result": result,
                }, )
            test_case_xray = {
                                 "testtype": "Manual",
                                 "fields": {
                                     "summary": summary,
                                     "project": {"key": "PD"}
                                 },
                                 "steps": steps_object,
                                 "xray_test_repository_folder": folder_name
                             },
        test_case_list.append(test_case_xray[0])
        if len(test_case_list) == 999:
            payload = json.dumps(test_case_list)
            Xray(project_key=config['Params']['project']).create_test_cases(payload)

            test_case_list.clear()
    payload = json.dumps(test_case_list)
    Xray(project_key=config['Params']['project']).create_test_cases(payload)
