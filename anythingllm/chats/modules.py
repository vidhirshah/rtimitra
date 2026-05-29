import requests
import dotenv , os
from pathlib import Path
from workspaces.modules import getWorkspaceDetailsBySlug

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

def getThreadDetails(workspace_slug:str , thread_name:str) -> dict | None:
    workspace_details = getWorkspaceDetailsBySlug(workspace_slug)
    if workspace_details is None:
        print(f"Workspace with slug '{workspace_slug}' not found.")
        return None
    threads = workspace_details.get("threads", [])
    thread_slug = thread_name.lower().replace(" ", "-")
    for thread in threads:
        if thread["slug"] == thread_slug:
            return thread
    return None

def createThreads(workspace_slug:str , thread_name:str ) -> list | None:
    is_thread_present = getThreadDetails(workspace_slug , thread_name)
    if is_thread_present is not None:
        print(f"Thread with name '{thread_name}' already exists in workspace '{workspace_slug}'.")
        return None
    
    path = f"workspace/{workspace_slug}/thread/new"
    url = BASE_URL + path
    payload = {
    "userId": 1,
    "name": thread_name,
    "slug": thread_name.lower().replace(" ", "-")
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if UPLOAD_LOGS:
            with LOG_FILE_PATH.open("a") as file:
                file.write("Create Thread Module\n")
                file.write(f"{response.status_code}\n")

        if response.status_code == 200:
            thread = response.json()["thread"]
            thread_details = {
                "id": thread["id"],
                "name": thread["name"],
                "slug": thread["slug"],
                "workspace_id": thread["workspace_id"]
            }
           
            if UPLOAD_LOGS:
                with LOG_FILE_PATH.open("a") as file:
                    file.write("Thread created\n")
                    file.write(f"{thread_details}\n")

            return thread_details
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    return None

def deleteThread(workspace_slug:str , thread_name:str) -> bool:
    is_thread = getThreadDetails(workspace_slug , thread_name)
    if is_thread is None:
        print(f"Thread with name '{thread_name}' not found in workspace '{workspace_slug}'.")
        return False
    
    thread_slug = thread_name.lower().replace(" ", "-")
    path = f"workspace/{workspace_slug}/thread/{thread_slug}"
    url = BASE_URL + path

    try:
        response = requests.delete(url, headers=headers)
        if UPLOAD_LOGS:
            with LOG_FILE_PATH.open("a") as file:
                file.write("Delete Thread Module\n")
                file.write(f"{response.status_code}\n")

        if response.status_code == 200:
            if UPLOAD_LOGS:
                with LOG_FILE_PATH.open("a") as file:
                    file.write(f"Thread Deleted\n")
                    file.write(f"{workspace_slug} - {thread_slug}\n")

            return True
        else:
            print(f"Error {response.status_code}: {response.text}")
            return False
    except requests.exceptions.RequestException as e:   
        print(f"Request failed: {e}")
    return False

def queryThreads(workspace_slug:str , thread_name:str , question:str) -> str | None:
    is_thread_present = getThreadDetails(workspace_slug , thread_name)
    if not is_thread_present:
        createThreads(workspace_slug , thread_name)
    
    thread_slug = thread_name.lower().replace(" ", "-")
    path = f"workspace/{workspace_slug}/thread/{thread_slug}/chat"
    url = BASE_URL + path
    payload = {
    "message": question,
    "mode": "query",
    "userId": 1,
    "reset": False
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if UPLOAD_LOGS:
            with LOG_FILE_PATH.open("a") as file:
                file.write("Query Thread Module\n")
                file.write(f"{response.status_code}\n")

        if response.status_code == 200:
            answer = response.json()["textResponse"]
            if UPLOAD_LOGS:
                with LOG_FILE_PATH.open("a") as file:
                    file.write(f"{question} - {answer}\n")

            return answer
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    return None