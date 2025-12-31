import os
import time
import logging
import sys
import argparse
import threading

from google_auth_oauthlib.flow import google
from backup_config import BackupConfig
from local_backup_manager import LocalBackupManager
from pathlib import Path

from watchdog.observers import Observer 
from watchdog.events import FileSystemEventHandler

# Worker to detect file and directory changes
# Automatically runs the backup subroutine upon detecting a change
class LocalBackupWorker(FileSystemEventHandler):
    def __init__(self, observer, logger, config):
        self.observer = observer
        self.logger = logger
        self.config = config
        self.debounce_timer = None
        self.debounce_delay = 2  # in seconds

    def on_any_event(self, event):
        # check if the event happened was triggered by a directory
        if event.is_directory:
            self.logger.info(f"Content changed in directory: {self.config.source_path}")
        else:
            self.logger.info(f"Content changed in file: {event.src_path}")

        # when a directory that has multiple files is copied,
        # the watchdog monitors every single file in the directory that gets copied,
        # so the watchdog ends up spamming multiple backups for each file copy
        # so for each detection, make sure to add a debounce timer that resets when it detects another event

        # cancel the pending backup
        if self.debounce_timer:
            self.debounce_timer.cancel()
        
        self.debounce_timer = threading.Timer(self.debounce_delay, self.run_backup)
        self.debounce_timer.start()

    def run_backup(self):
        self.logger.info("Starting backup...")
        try:
            manager = LocalBackupManager(self.config)
            manager.perform_backup()
        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
        finally:
            self.debounce_timer = None # stop the debounce timer once the backup has finished


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
    parser.add_argument("-w", "--watchdog", 
        help="EXPERIMENTAL. Sets a flag to EITHER run the backup straight away and exit (0) OR continuously scan the specified directory/file for any changes and run the backup everytime it detects one. (1)", 
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
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(levelname)s] %(message)s"
    )

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
    watchdog = args.watchdog

    if not source_path:
        raise ValueError("ERROR: Please specify a source directory")

    if not dest_path:
        raise ValueError("ERROR: Please specify a destination directory")

    config = BackupConfig(source_path, dest_path, target_file, backup_name, compress_backup, cloud)

    if watchdog == "1":
        observer = Observer()
        handler = LocalBackupWorker(observer, logger, config)

        # main event handler, use recursive=True to monitor all subdirectories
        # runs on a separate background thread
        observer.schedule(handler, source_path, recursive=True)
        observer.start()

        try:
            logger.info("Main backup thread started.")
            while True:
                time.sleep(1) # small delay to avoid CPU overloading - gives it some time to free up resources
        except KeyboardInterrupt:
            logger.info("Terminating...")
            observer.stop()
        observer.join()
    else:
        manager = LocalBackupManager(config)
        manager.perform_backup()



if __name__ == "__main__":
    main()