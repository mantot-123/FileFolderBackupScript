import argparse
from backup_config import BackupConfig
from backup_manager import BackupManager
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
    
    args = parser.parse_args()

    source_path = "" if not args.source_path else args.source_path
    dest_path = "" if not args.dest_path else args.dest_path
    target_file = "" if not args.target_file else args.target_file
    backup_name = "" if not args.backup_name else args.backup_name
    
    compress_backup = "" if not args.compress else args.compress
    compress_backup = "0" if compress_backup != "1" else "1"

    if not source_path:
        raise ValueError("ERROR: Please specify a source directory")

    if not dest_path:
        raise ValueError("ERROR: Please specify a destination directory")

    config: BackupConfig = BackupConfig(source_path, dest_path, target_file, backup_name, compress_backup)
    manager: BackupManager = BackupManager(config)

    print("Performing backup...")
    backup = manager.perform_backup()

    if backup != None:
        print(f"Backup successfully created. The output file is located at: {str(backup)}")
    else:
        print("Backup failed. Please check that the source file exists and try again")

if __name__ == "__main__":
    main()