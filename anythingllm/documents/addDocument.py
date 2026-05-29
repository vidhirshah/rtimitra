from documents.modules import uploadFile
from pathlib import Path
import json
import dotenv , os

dotenv.load_dotenv()
ANYTHING_LLM_API = os.getenv("ANYTHING_LLM_API")
BASE_URL = os.getenv("BASE_URL")

upload_folder = input("Enter the Anything LLM folder name to upload the document: ")
path = "document/upload/"
url = BASE_URL + path + upload_folder

input_file = input("Enter the file path to upload: ")

response = uploadFile(url,input_file)
print(response)
