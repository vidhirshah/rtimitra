import requests
import dotenv , os
from pathlib import Path

dotenv.load_dotenv()
BASE_URL = os.getenv("BASE_URL")
ANYTHING_LLM_API = os.getenv("ANYTHING_LLM_API")
UPLOAD_LOGS = os.getenv("UPLOAD_LOGS", "false").lower() == "true"
if UPLOAD_LOGS:
    LOG_FILE = os.getenv("LOG_FILE", "upload_logs.txt")
    LOG_FILE_PATH = Path(LOG_FILE)

headers = {
    "accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {ANYTHING_LLM_API}"
}

def createWorkspace(name:str) -> int | None:
    path = "workspace/new"
    url = BASE_URL + path
    payload = {
        "name": name
    }

    try:
        response = requests.post(url, headers=headers, json=payload , timeout=10)

        if UPLOAD_LOGS:
            with LOG_FILE_PATH.open("a") as file:
                file.write("Create Workspace Module\n")
                file.write(f"{response.status_code}\n")

        if response.status_code == 200:
            workspace = response.json()["workspace"]
            workspace_details = {
                "id": workspace["id"],
                "name": workspace["name"],
                "slug": workspace["slug"],
            }
           
            if UPLOAD_LOGS:
                with LOG_FILE_PATH.open("a") as file:
                    file.write("Workspace created\n")
                    file.write(f"{workspace_details}\n")

            return workspace_details
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def listWorkspaces() -> list | None:
    path = "workspaces"
    url = BASE_URL + path

    try:
        workspaces = []
        response = requests.get(url, headers=headers, timeout=10)

        if UPLOAD_LOGS:
            with LOG_FILE_PATH.open("a") as file:
                file.write("List Workspaces Module\n")
                file.write(f"{response.status_code}\n")

        if response.status_code == 200:
            for i in response.json()["workspaces"]:
                workspace = {
                    "id": i["id"],
                    "name": i["name"],
                    "slug": i["slug"],
                }
                workspaces.append(workspace)

            if UPLOAD_LOGS:
                with LOG_FILE_PATH.open("a") as file:
                    file.write("List of WorkSpaces\n")
                    for i in workspaces:
                        file.write(f"{i}\n")

            return workspaces
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def getWorkspaceDetailsBySlug(slug:str) -> dict | None:
    path = "workspaces"
    url = BASE_URL + path

    try:
        workspaces = []
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            for workspace in response.json()["workspaces"]:
                if workspace["slug"] == slug:
                    return workspace
                
            return None
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def getWorkspaceIdBySlug(slug:str) -> dict | None:
    workspaces = listWorkspaces()

    if workspaces is not None:
        for workspace in workspaces:
            if workspace["slug"] == slug:
                return workspace["id"]
    
    return None

def deleteWorkspace(slug:str) -> bool:
    path = "workspace/"
    url = BASE_URL + path + slug

    try:
        response = requests.delete(url, headers=headers, timeout=10)

        if UPLOAD_LOGS:
            with LOG_FILE_PATH.open("a") as file:
                file.write("Delete Workspace Module\n")
                file.write(f"{response.status_code}\n")

        if response.status_code == 200:
            if UPLOAD_LOGS:
                with LOG_FILE_PATH.open("a") as file:
                    file.write(f"{slug} Workspace deleted successfully\n")
            return True
        else:
            print(f"Error {response.status_code}: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return False