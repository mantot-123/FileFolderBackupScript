import os
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
    0 - path/file name not specified (shown by asterisk)
    1 - path/file exists
    -1 - path/file does NOT exist
    '''
    def check_file_existence(self) -> int:
        # -- checks if the file name is specified --
        if self.selected_file.strip() == "":
            return 0

        # -- check if the source directory exists --
        full_path_str = os.path.join(Path(self.source_path), self.selected_file)
        full_path_obj = Path(full_path_str)
        if os.path.isfile(full_path_obj):
            return 1
        
        return -1
    
    def check_source_path(self) -> int:
        # -- checks if the source directory is specified --
        if self.source_path.strip() == "":
            return 0
        
        # -- check if the source directory exists --
        if os.path.isdir(self.source_path):
            return 1
        
        return -1
    
    def check_dest_path(self) -> int:
        # -- checks if the destination directory is specified --
        if self.destination_path.strip() == "":
            return 0

        # -- check if the destination directory already exists --
        if os.path.isdir(self.destination_path):
            return 1
        
        return -1
    
    # check if the backup filename is specified in the config file
    def check_backup_name(self) -> bool:
        if self.backup_name == "":
            return False
        return True