from documents.modules import uploadFilesInFolder
from pathlib import Path
import json
import dotenv , os

dotenv.load_dotenv()
ANYTHING_LLM_API = os.getenv("ANYTHING_LLM_API")
BASE_URL = os.getenv("BASE_URL")

upload_folder = input("Enter the Anything LLM folder name to upload the document: ")
path = "document/upload/"
url = BASE_URL + path + upload_folder

input_folder = input("Enter the folder path to upload: ")

response = uploadFilesInFolder(url, input_folder)

if response == 0:
    print("All files uploaded successfully.")
else:
    print("Some files failed to upload.")