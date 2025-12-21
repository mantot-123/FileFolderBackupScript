import os
import time
import shutil
import re
from pathlib import Path

class BackupConfig:
    def __init__(self, source_path, destination_path, selected_file, backup_name, compress_backup):
        self.source_path = source_path.strip()
        self.destination_path = destination_path.strip()
        self.selected_file = selected_file.strip()
        self.backup_name = backup_name.strip()
        self.compress_backup = compress_backup.strip()

    '''
    path and file check flags:
    0 - path/file not specified
    1 - path/file exists
    -1 - path/file does NOT exist
    '''
    def check_file_existence(self) -> int:
        # -- checks if the file name is specified --
        if self.selected_file.strip() == "":
            return 0

        # -- check if the source path exists --
        full_path_str = os.path.join(Path(self.source_path), self.selected_file)
        full_path_obj = Path(full_path_str)
        if full_path_obj.is_file():
            return 1
        
        return -1
    
    def check_source_path(self) -> int:
        # -- checks if the source path is specified --
        if self.source_path.strip() == "":
            return 0
        
        # -- check if the source path exists --
        if os.path.exists(self.source_path):
            return 1
        
        return -1
    
    def check_dest_path(self) -> int:
        # -- checks if the destination path is specified --
        if self.destination_path.strip() == "":
            return 0

        # -- check if the destination path already exists --
        if os.path.exists(self.destination_path):
            return 1
        
        return -1
    
    # check if the backup filename is specified in the config file
    def check_backup_name(self) -> int:
        if self.backup_name == "":
            return 0
        return 1