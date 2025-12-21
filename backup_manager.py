import os
import time
import shutil
import zipfile
import datetime
from backup_config import BackupConfig
from pathlib import Path

class BackupManager:
    def __init__(self, config: BackupConfig):
        self.config = config

    def perform_backup(self) -> Path:
        backup_path = self.copy_file()

        if self.config.compress_backup == "1" and backup_path != None:
            compress = self.compress_backup(backup_path)
        return backup_path
   
    # returns a timestamp in the following format:
    # <backup_date>-<24h_formatted_time>
    def add_timestamp(self) -> str:
        datetime_full = datetime.datetime.now()

        date = datetime_full.strftime("%d-%b-%Y")
        time = datetime_full.strftime("%H.%M")
        millisecs = None

        timestamp_str = f"{date}-{time}"
        return timestamp_str

    # rename the backed up file to what is specified in the config file (the "BACKUP_NAME" key)
    # or automatically rename it with the convention
    # <original_filename>-BACKUP-<full_timestamp>
    def name_backup(self) -> str:
        backup_name = self.config.backup_name

        # run if the backup filename is not specified
        if self.config.check_backup_name() == 0:
            orig_path = os.path.splitext(self.config.selected_file)
            orig_fname = orig_path[0]
            f_ext = orig_path[1]
            backup_name = f"{orig_fname}-BACKUP-{self.add_timestamp()}{f_ext}"

        return backup_name

    # create a copy of the file/folder and moves that into the destination directory
    def copy_file(self) -> Path:
        full_path = Path(os.path.join(self.config.source_path, self.config.selected_file))

        if self.config.check_file_existence() == 0:
            full_path = Path(self.config.source_path)
        elif self.config.check_file_existence() == -1: # file does not exist
            return None

        # destination directory does not exist, automatically create one
        if self.config.check_dest_path() == -1:
            os.makedirs(self.check)

        copy_path = shutil.copy(full_path, self.config.destination_path)

        if self.config.check_file_existence() == 0:
            file_ext = os.path.splitext(full_path)[1]
            new_name = self.name_backup() + file_ext
        else:
            new_name = self.name_backup()

        new_path = os.path.join(self.config.destination_path, new_name)

        os.rename(copy_path, new_path)
        return copy_path

    # (optionally, in the config file) compress the output file/folder into a ZIP file
    def compress_backup(self, backup_path) -> bool:
        return True