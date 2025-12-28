import os
import logging
import shutil
import zipfile
import datetime
import google_drive_manager

from backup_config import BackupConfig
from pathlib import Path

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class LocalBackupManager:
    def __init__(self, config: BackupConfig):
        self.config = config
        self.output_backup_name = self.name_backup()
        self.setup_logging()

    def setup_logging(self):
        # logging.basicConfig(filename=f"logs/[LOG]-{self.output_backup_name}.log", level=logging.DEBUG)
        file_handler = logging.FileHandler(f"logs/[LOG]-{self.output_backup_name}.log")
        file_handler.setLevel(logging.DEBUG)

        cli_handler = logging.StreamHandler()
        cli_handler.setLevel(logging.DEBUG)

        logger.addHandler(file_handler)
        logger.addHandler(cli_handler)

    def perform_backup(self) -> Path:
        compress_path = None
        backup_path = self.copy_file()

        if backup_path == None:
            target_path = os.path.join(self.config.source_path, self.config.selected_file)
            logger.error(f"Failed to backup {target_path}. Please check that the source file/directory exists, is named correctly and try again.")
            return None

        is_compressed = False
        if self.config.compress_backup == "1" and backup_path != None:
            compress_path = self.compress_backup(backup_path)
            is_compressed = True

        if self.config.cloud_providers:
            if is_compressed:
                self.upload_to_cloud(compress_path)
            else:
                self.upload_to_cloud(backup_path)

        logger.info(f"Backup successfully created. The output file is located locally at: {str(backup_path)}")
        return backup_path
   
    def upload_to_cloud(self, output_path):
        current_service = ""
        try:
            if "google_drive" in self.config.cloud_providers:
                current_service = "Google Drive"
                logger.info(f"Backing up output file/folder to Google Drive: {output_path}")
                creds = google_drive_manager.authorise()
                google_drive_manager.upload(creds, output_path)

            if "onedrive" in self.config.cloud_providers:
                # TODO ONEDRIVE BACKUP HERE
                pass
            
            if "dropbox" in self.config.cloud_providers:
                # TODO DROPBOX BACKUP HERE
                pass

            if "amazon_s3" in self.config.cloud_providers:
                # TODO AMAZON S3 BACKUP HERE
                pass

        except Exception as e:
            error_msg = f"Error while syncing output file {output_path} to cloud service {current_service}: {e}"
            logger.error(error_msg)

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
            error_msg = f"Source directory {self.config.source_path} does not exist"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        file_check = self.config.check_file_existence()
        if file_check == -1:
            error_msg = f"Target file {self.config.selected_file} in parent directory {self.config.source_path} does not exist"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        if src_path_check == 0: # check if the source directory is specified
            # if not specified, assume that the target file we want to backup 
            # is in the current directory the script is running
            full_path = Path(self.config.selected_file)
        else:
            full_path = Path(os.path.join(self.config.source_path, self.config.selected_file))

        dest_path_check = self.config.check_dest_path()

        # destination directory does not exist, automatically create one
        if dest_path_check == -1:
            try:
                os.makedirs(self.config.destination_path)
            except Exception as e:
                error_msg = f"An error occurred while attempting to create the destination directory: {e}"
                logger.error(error_msg)
                return None

        # copy operation here
        new_dest_path = None
        try:
            # when using the shutil copy methods and providing it the "dest",
            # it expects the destination directory and the name the file should be after it's copied

            if file_check == 0: # run if we are backing up an entire directory
                backup_name = self.output_backup_name
                new_dest_path = os.path.join(self.config.destination_path, backup_name)
                shutil.copytree(full_path, new_dest_path)
                new_path = new_dest_path
            else: # run if we are trying to backup a file
                new_name = self.output_backup_name
                new_dest_path = os.path.join(self.config.destination_path, new_name)
                # shutil.copyfile(full_path, new_dest_path) # don't use this, it does not keep original metadata
                shutil.copy2(full_path, new_dest_path) # this one keeps all the original metadata
                new_path = new_dest_path
        except Exception as e:
            error_msg = f"An error occurred while attempting to copy the file to the directory {self.config.destination_path}: {e}"
            logger.error(error_msg)

            self.delete_copy(new_dest_path) # discards the file/directory in process in case of an error
            return None

        success_msg = f"Successfully copied {full_path} to the new directory: {new_path}"
        logger.info(success_msg)
        return new_path

    # TODO
    def delete_copy(self, path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.isfile(path):
            os.remove(path)

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
                logger.info(f"Creating ZIP file: {zip_name}...")
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

                        logger.info(f"Successfully added to ZIP: {file_path}")
                else:
                    zip_file.write(backup_path, os.path.basename(backup_path))
                    logger.info(f"Successfully added file to ZIP: {backup_path}")

            # deletes the original file/directory after compression
            if os.path.isdir(backup_path):
                shutil.rmtree(backup_path)
            elif os.path.isfile(backup_path):
                os.remove(backup_path)

            logger.info("Compression successful!")
            return Path(zip_name)
        except Exception as e:
            message = f"Compression failed: {e}"
            logger.error(message)
            return None