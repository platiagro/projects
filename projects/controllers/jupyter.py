from os import getenv
import json
import requests

ENDPOINT = getenv("JUPYTER_ENDPOINT", "server.anonymous:80/notebook/anonymous/server")

URL_CONTENTS = ENDPOINT + "/api/contents/{}"

URL_WORKSPACES = ENDPOINT + "/lab/api/workspaces/lab"

COOKIES = dict(_xsrf='token')

HEADERS = {'content-type': 'application/json', 'X-XSRFToken': 'token'}

def get_full_file_path(folderPath, fileName):
    if folderPath == "":
        fullFilePath = fileName
    else:
        fullFilePath = folderPath + "/" + fileName

    return fullFilePath

def get_file(folderPath, name):
    fullFilePath = get_full_file_path(folderPath, name)

    r = requests.get(url = URL_CONTENTS.format(fullFilePath))

    if r.status_code != requests.codes.ok:
        return
        
    return r.json()

def create_new_file(folderPath, name, isFolder, content=None):

    if content is not None:
        content = json.loads(content.decode("utf-8"))

    fullFilePath = get_full_file_path(folderPath, name)

    fileType = "directory" if isFolder is True else "notebook"

    payload = {'type': fileType, 'content': content}

    r = requests.put(
        url = URL_CONTENTS.format(fullFilePath), 
        cookies=COOKIES, 
        headers=HEADERS, 
        data=json.dumps(payload)
    )

    if r.status_code != requests.codes.created:
        return

    return r.json()


def set_workspace(path, inferenceFileName, trainingFileName):
    r = requests.get(url = URL_WORKSPACES)

    if r.status_code != requests.codes.ok:
        return

    inference = "notebook:{}/{}".format(path, inferenceFileName)
    training = "notebook:{}/{}".format(path, trainingFileName)

    resp = r.json()
    data = resp["data"]
    data[inference] = {
        "data": {
            "path": "{}/{}".format(path, inferenceFileName),
            "factory": "Notebook"
        }
    }
    data[training] = {
        "data": {
            "path": "{}/{}".format(path, trainingFileName),
            "factory": "Notebook"
        }
    }

    file_browser_filebrowser = data["file-browser-filebrowser:cwd"]
    file_browser_filebrowser["path"] = path

    layout_restorer = data["layout-restorer:data"]
    main = layout_restorer["main"]
    main["current"] = inference
    dock = main["dock"]
    dock["widgets"] = [inference, training]

    r = requests.put(
        url = URL_WORKSPACES, 
        cookies=COOKIES, 
        headers=HEADERS, 
        data=json.dumps(resp)
    )

    return