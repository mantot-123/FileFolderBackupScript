import logging
import sys
import argparse

from google_auth_oauthlib.flow import google
from backup_config import BackupConfig
from local_backup_manager import LocalBackupManager
from pathlib import Path

# cli argument parsing method
def get_cmd_parser():
    parser = argparse.ArgumentParser(
        prog="File Backup Script",
        description="File Backup Script || by mantot_123 || github.com/mantot-123")
    
    # valid command line arguments here
    parser.add_argument("-s", "--source_path", 
        help="Specifies the source directory. Required.", 
        default="",
        nargs="?")
    parser.add_argument("-d", "--dest_path", 
        help="Specifies the destination directory where the file should be backed up. Required.", 
        default="",
        nargs="?")
    parser.add_argument("-t", "--target_file", 
        help="Specifies the target file located in the source directory to backup. If not specified, the script will backup the whole source directory.", 
        default="",
        nargs="?")
    parser.add_argument("-b", "--backup_name", 
        help="Sets a custom name for the backed up file. If blank, the script will automatically name it.", 
        default="",
        nargs="?")
    parser.add_argument("-c", "--compress", 
        help="Sets a flag to compress or not compress the file after copying. 0 - DON'T COMPRESS, 1 = COMPRESS. Default value will be 0.", 
        default="0")
    parser.add_argument(
        "--cloud",
        nargs="*",
        choices=["google_drive"],
        help=f"Specify a list of cloud providers to upload the file to after backup.")
    
    args = parser.parse_args()
    return (parser, args)

def main():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    parser = get_cmd_parser()[0]
    args = get_cmd_parser()[1]

    if len(sys.argv) <= 1:
        parser.print_help()
        return

    source_path = args.source_path
    dest_path = args.dest_path
    target_file = args.target_file
    backup_name = args.backup_name
    compress_backup = args.compress
    cloud = args.cloud

    if not source_path:
        raise ValueError("ERROR: Please specify a source directory")

    if not dest_path:
        raise ValueError("ERROR: Please specify a destination directory")

    config: BackupConfig = BackupConfig(source_path, dest_path, target_file, backup_name, compress_backup, cloud)
    manager: LocalBackupManager = LocalBackupManager(config)

    print("Performing backup...")
    backup = manager.perform_backup()


if __name__ == "__main__":
    main()