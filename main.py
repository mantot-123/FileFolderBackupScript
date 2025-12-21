import configparser
from backup_config import BackupConfig
from backup_manager import BackupManager
from pathlib import Path

def load_config_file():
    config_path = Path("config.ini")

    # if the config file currently does not exist, automatically create it with blank keys 
    # (except the compress flag)
    if not config_path.is_file():
        config = configparser.ConfigParser()
        config['DEFAULT'] = {
            'SOURCE_PATH': '',
            'DESTINATION_PATH': '',
            'TARGET_FILE': '',
            'BACKUP_NAME': '',
            'COMPRESS_BACKUP': '0'
        }
        with open("config.ini", "w") as config_file:
            config.write(config_file)

    config = configparser.ConfigParser()
    config.read("config.ini")
    return config

def main():
    config_file = load_config_file()

    source_path = config_file["DEFAULT"]["SOURCE_PATH"].strip()
    dest_path = config_file["DEFAULT"]["DESTINATION_PATH"].strip()
    target_file = config_file["DEFAULT"]["TARGET_FILE"].strip()
    backup_name = config_file["DEFAULT"]["BACKUP_NAME"].strip()
    compress_backup = config_file["DEFAULT"]["COMPRESS_BACKUP"].strip()
    compress_backup = "0" if compress_backup != "1" else "1"
    compress_backup_str = "YES" if compress_backup == "1" else "NO"

    config_keys_empty = not source_path and not dest_path and not target_file

    if config_keys_empty:
        print("The configuration file (config.ini) currently does not have a source path, destination path and the target file to back up. Please fill out these details in the config file and try again.")
        return

    print("Source Path:", source_path)
    print("Destination Path:", dest_path)
    print("Target File:", target_file)
    print("Backup Name:", backup_name)
    print("Compress output file:", compress_backup_str)

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