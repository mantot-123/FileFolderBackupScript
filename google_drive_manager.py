import logging
import mimetypes
import os.path

from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive"]

logger = logging.getLogger()

def authorise():
	creds = None
	# The file token.json stores the user's access and refresh tokens, and is
	# created automatically when the authorization flow completes for the first
	# time.
	if os.path.exists("token.json"):
		creds = Credentials.from_authorized_user_file("token.json", SCOPES)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				"client_secrets_GoogleDrive.json", SCOPES
			)
			creds = flow.run_local_server(port=0)
		# Save the credentials for the next run
		with open("token.json", "w") as token:
			token.write(creds.to_json())
	return creds

def upload(creds, backup_path):
	try:
		service = build("drive", "v3", credentials=creds)
		mimetype = mimetypes.guess_type(backup_path) # get file's mimetype
		
		# set file metadata for the output file (the file that is uploaded to google drive)
		file_metadata = {
			"name": os.path.basename(backup_path),
			"mimeType": mimetype
		}

		media = MediaFileUpload(backup_path, resumable=True)

		logger.info(f"Uploading file {file_metadata['name']} to Google Drive...")

		output = (
			service.files()
			.create(body=file_metadata, media_body=media, fields="id, name")
			.execute()
		)

		logger.info(f"Upload successful!")
		return output
	except HttpError as error:
		# handle API error
		logger.info(f"An error occurred while uploading the file: {error}")
		