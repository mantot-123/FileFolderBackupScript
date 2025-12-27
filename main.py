import sys
import argparse

from google_auth_oauthlib.flow import google
import google_drive_manager
from backup_config import BackupConfig
from local_backup_manager import LocalBackupManager
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        prog="File Backup Script",
        description="File Backup Script || by mantot_123 || github.com/mantot-123"
    )
    parser.add_argument("-s", "--source_path", help="Specifies the source directory. Required.")
    parser.add_argument("-d", "--dest_path", help="Specifies the destination directory where the file should be backed up. Required.")
    parser.add_argument("-t", "--target_file", help="Specifies the target file located in the source directory to backup. If not specified, the script will backup the whole source directory.")
    parser.add_argument("-b", "--backup_name", help="Sets a custom name for the backed up file. If blank, the script will automatically name it.")
    parser.add_argument("-c", "--compress", help="Sets a flag to compress or not compress the file after copying. 0 - DON'T COMPRESS, 1 = COMPRESS. Default value will be 0.")
    parser.add_argument(
        "--cloud",
        nargs="*",
        choices=["google_drive"],
        help=f"Specify a list of cloud providers to upload the file to after backup."
    )
    
    args = parser.parse_args()

    if len(sys.argv) < 1:
        parser.print_help()
        return

    source_path = "" if not args.source_path else args.source_path
    dest_path = "" if not args.dest_path else args.dest_path
    target_file = "" if not args.target_file else args.target_file
    backup_name = "" if not args.backup_name else args.backup_name

    compress_backup = "" if not args.compress else args.compress
    compress_backup = "0" if compress_backup != "1" else "1"

    cloud = args.cloud

    if not source_path:
        raise ValueError("ERROR: Please specify a source directory")

    if not dest_path:
        raise ValueError("ERROR: Please specify a destination directory")

    config: BackupConfig = BackupConfig(source_path, dest_path, target_file, backup_name, compress_backup, cloud)
    manager: LocalBackupManager = LocalBackupManager(config)

    print("Performing backup...")
    backup = manager.perform_backup()

    if backup != None:
        if "google_drive" in cloud:
            creds = google_drive_manager.authorise()
            google_drive_manager.upload(creds, backup)
            print("Backing up to Google Drive...")

        if "onedrive" in cloud:
            pass
        
        if "dropbox" in cloud:
            pass

        print(f"Backup successfully created. The output file is located locally at: {str(backup)}")
    else:
        print("Backup failed. Please check that the source file exists and try again")

if __name__ == "__main__":
    main()