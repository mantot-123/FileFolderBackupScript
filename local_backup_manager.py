import os
import logging
import shutil
import zipfile
import datetime
from backup_config import BackupConfig
from pathlib import Path

class LocalBackupManager:
    def __init__(self, config: BackupConfig):
        self.config = config
        self.set_backup_name = self.name_backup()
        logging.basicConfig(filename=f"logs/[LOG]-{self.set_backup_name}.log", level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def perform_backup(self) -> Path:
        backup_path = self.copy_file()

        if self.config.compress_backup == "1" and backup_path != None:
            compress_path = self.compress_backup(backup_path)
            return compress_path

        return backup_path
   
    # returns a timestamp in the following format:
    # <backup_date>-<24h_formatted_time>
    def add_timestamp(self) -> str:
        datetime_full = datetime.datetime.now()

        date = datetime_full.strftime("%d-%b-%Y")
        time = datetime_full.strftime("%H.%M")
        millisecs = datetime_full.strftime("%f")[:-3]

        timestamp_str = f"{date} {time}.{millisecs}"
        return timestamp_str

    # rename the backed up file to what is specified in the config file (the "BACKUP_NAME" key)
    # or automatically rename it with the convention
    # <original_filename>-BACKUP-<full_timestamp>
    def name_backup(self) -> str:
        name = self.config.backup_name

        if not self.config.check_backup_name():
            if self.config.check_file_existence() != 0:
                orig_path = os.path.splitext(self.config.selected_file)
                orig_fname = orig_path[0]
                f_ext = orig_path[1]
                name = f"{orig_fname}-BACKUP-{self.add_timestamp()}{f_ext}"
            else:
                dir_name = os.path.basename(self.config.source_path)
                name = f"{dir_name}-BACKUP-{self.add_timestamp()}"

        return name

    # create a copy of the file/folder and moves that into the destination directory
    def copy_file(self) -> Path:
        # check source path and target file's existence
        src_path_check = self.config.check_source_path()
        if src_path_check == -1:
            self.logger.error("Source directory does not exist")
            raise FileNotFoundError("Error: Source path does not exist")

        file_check = self.config.check_file_existence()
        if file_check == -1:
            self.logger.error("Target file does not exist")
            raise FileNotFoundError("Error: Target file does not exist")

        if src_path_check == 0:
            full_path = Path(self.config.selected_file)
        else:
            full_path = Path(os.path.join(self.config.source_path, self.config.selected_file))

        dest_path_check = self.config.check_dest_path()
        # destination directory does not exist, automatically create one
        if dest_path_check == -1:
            try:
                os.makedirs(self.config.destination_path)
            except Exception as e:
                self.logger.error(f"An error occurred while attempting to create the destination directory: {e}")
                return None

        # copy operation here
        try:
            # when using the shutil copy methods and providing it the "dest",
            # it expects the destination directory and the name the file should be after it's copied
            if file_check == 0: # run if we are backing up an entire directory
                backup_name = self.set_backup_name
                dest_dir_path = os.path.join(self.config.destination_path, backup_name)
                shutil.copytree(full_path, dest_dir_path)
                new_path = dest_dir_path
            else: # run if we are trying to backup a file
                new_name = self.set_backup_name
                dest_file_path = os.path.join(self.config.destination_path, new_name)
                shutil.copy2(full_path, dest_file_path)
                new_path = dest_file_path
        except Exception as e:
            self.logger.error(f"An error occurred while attempting to copy the file to the directory {self.config.destination_path}: {e}")
            return None

        self.logger.info(f"Successfully copied {full_path} to the new directory: {new_path}")
        return new_path

    def discard_copy(self):
        pass

    # (optionally, in the config file) compress the output file/folder into a ZIP file
    def compress_backup(self, backup_path) -> Path:
        zip_name = f"{backup_path}.zip"

        # if it's a file, then create strip away the backed up file's extension from the zip's name
        if os.path.isfile(backup_path):
            p = os.path.splitext(backup_path)
            prefix = p[0]
            zip_name = f"{prefix}.zip"

        try:
            with zipfile.ZipFile(zip_name, "w") as zip_file:
                self.logger.info(f"ZIP file: {zip_name}")
                if os.path.isdir(backup_path):
                    base_dir = os.path.basename(backup_path)
                    # os.walk() - array of tuples
                    for root, dirs, files in os.walk(backup_path):
                        for f in files:
                            file_path = os.path.join(root, f)
                            arcdir = os.path.join(base_dir, os.path.relpath(file_path, backup_path))
                            zip_file.write(file_path, arcdir)

                        # consider all of the empty subdirectories
                        if not files and not dirs:
                            # name of the empty folder we want to insert to the archive
                            arcdir = os.path.join(base_dir, os.path.relpath(root, backup_path)) + "/"
                            # zip_file.writestr(base_dir, arcdir) # doesn't add the empty directories
                            zip_file.writestr(arcdir, "") 

                        self.logger.info(f"Successfully added to ZIP: {file_path}")
                else:
                    zip_file.write(backup_path, os.path.basename(backup_path))
                    self.logger.info(f"Successfully added file to ZIP: {backup_path}")

            # deletes the original file/directory after compression
            if os.path.isdir(backup_path):
                shutil.rmtree(backup_path)
            elif os.path.isfile(backup_path):
                os.remove(backup_path)

            self.logger.info("Compression successful!")
            return Path(zip_name)
        except Exception as e:
            message = f"Compression failed: {e}"
            self.logger.error(message)
            raise Exception(message)