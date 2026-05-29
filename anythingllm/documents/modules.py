import requests , json
from pathlib import Path
import dotenv , os

dotenv.load_dotenv()
ANYTHING_LLM_API = os.getenv("ANYTHING_LLM_API")
UPLOAD_LOGS = os.getenv("UPLOAD_LOGS", "false").lower() == "true"
if UPLOAD_LOGS:
    LOG_FILE = os.getenv("LOG_FILE", "upload_logs.txt")
    LOG_FILE_PATH = Path(LOG_FILE)

headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {ANYTHING_LLM_API}"
}

MIME_MAP = {
    ".pdf":  "application/pdf",
    ".txt":  "text/plain",
    ".md":   "text/markdown",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".csv":  "text/csv",
    ".json": "application/json",
}

def checkMimeType(mine_type : str) -> bool:
    return mine_type in list(MIME_MAP.values())

def getMineType(file_path: Path) -> str:
    return MIME_MAP.get(file_path.suffix.lower(), "application/octet-stream")

def getMetadata(file_path: Path) -> dict:
    metadata = {}
    metadata["file-name"] = file_path.stem
    metadata["year"] = file_path.parent.name
    metadata["department"] = file_path.parent.parent.name
    metadata["category"] = file_path.parent.parent.parent.name
    return metadata

def getFileUploadData(file_path: Path) -> dict:
    metadata = getMetadata(file_path)
    data={
        "addToWorkspaces": "string",                 
        "metadata": json.dumps({                     
            "file-name": metadata["file-name"],
            "department": metadata["department"],
            "category" : metadata["category"],
            "year" : metadata["year"],
        })
    }
    return data

def uploadFile(url:str , input_file: str):
    file_path = Path(input_file)

    if file_path.exists() == False:
        print(f"File not found: {input_file}")
        return -1

    mime_type = getMineType(file_path)
    
    if not checkMimeType(mime_type):
        print(f"Unsupported file type: {file_path.suffix}")
        return -1

    data = getFileUploadData(file_path)

    try:
        with open(file_path, "rb") as fh:
            response = requests.post(
                url,
                headers=headers,
                files={"file": (file_path.name, fh, mime_type)},
                data=data
            )
        
        if UPLOAD_LOGS:
            with LOG_FILE_PATH.open("a") as file:
                file.write("File Upload Module\n")
                file.write(f"{response.status_code} - {file_path}\n")

        if response.status_code == 200:
            print(f"{input_file} uploaded successfully.")
            return 0
        else:
            print(f"Error {response.status_code}: {response.text}")
            return -1
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        
    return -1

def getFiles(folder_path:Path) -> list:
    files = []

    for input_file in folder_path.rglob("*"):
        if not input_file.is_file():
            continue
        else:
            mime_type = getMineType(input_file)
    
            if checkMimeType(mime_type):
                files.append(input_file)
    
    return files

def uploadFilesInFolder(url: str, input_folder: str):
    folder_path = Path(input_folder)
    
    if not folder_path.is_dir():
        print(f"Folder not found: {input_folder}")
        return -1

    files = getFiles(folder_path)

    for file in files:
        result = uploadFile(url, str(file))
        if result != 0:
            print(f"Failed to upload: {file}")

    return 0

