# File Backup Script
Credit:
* mantot_123

## About
A Python-based script to backup files and directories locally and upload them to other cloud services. It currently only has support for Google Drive, however, support for other cloud services is planned for future releases.

### Features (current)
* **Local and cloud backups** - Automatically backs up files and folders locally, with also an option to upload to multiple cloud services
* **Compression** - Compress backups into ZIP files for easier storage and transfer


### Features (planned)
* **Add support for more cloud services:**
    * Microsoft OneDrive
    * Dropbox
    * Amazon S3
* A watch feature to automatically back up the file/directory if it detects that its contents have changed


## Setup

1.) Clone/download this repository

2.) Install dependencies
```
pip install -r requirements.txt
```

3.) For Google Drive support, you'll need to:
* Create a new Google Cloud project
* Enable the Google Drive API
* Create a new credential, specifically an OAuth 2.0 Client ID, in the "APIs and Services" section of the Google Cloud dashboard
* Download the credentials and save it as `client_secrets_GoogleDrive.json` in the script's directory



## Usage
```
py .\main.py -s <source_path> -d <destination_path> [options]
```

### Required arguments
| Argument | Short | Description | Required |
|----------|-------|-------------|----------|
| `--source_path` | `-s` | Specifies the source directory. Required. | Yes |
| `--dest_path` | `-d` | Specifies the destination directory where the file should be backed up. Required. | Yes |


### Optional arguments
| Argument | Short | Description | Required |
|----------|-------|-------------|----------|
| `--target_file` | `-t` | Specifies the target file in the source directory to backup. If not specified, the script will backup the whole source directory. | No |
| `--backup_name` | `-b` | Sets a custom name for the backed up file. If not specified, the script will automatically name it. | No |
| `--compress` | `-c` | Compression flag: `0` = no compression, `1` = compress | No (default: "0") |
| `--cloud` | | List of cloud providers to upload to (e.g., `google_drive`) | No |