import shutil
import datetime
from tqdm import tqdm
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

source_directory = ''
backup_directory = ''

current_date = datetime.datetime.now().strftime("%Y-%m-%d")
prev_week_date = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")

def backup_directory_recursive(source, destination):
    for root, _, files in os.walk(source):
        relative_path = os.path.relpath(root, source)
        dest_path = os.path.join(destination, relative_path)

        if not os.path.exists(dest_path):
            os.makedirs(dest_path)

        for file in files:
            source_file = os.path.join(root, file)
            destination_file = os.path.join(dest_path, file)

            try:
                shutil.copy2(source_file, destination_file)
            except (shutil.SameFileError, FileNotFoundError, PermissionError) as e:
                print(f"Error: {e}")

def backup_with_progress(source, destination):
    if not os.path.exists(destination):
        os.makedirs(destination)

    with tqdm(unit="file", dynamic_ncols=True) as pbar, ThreadPoolExecutor(max_workers=4) as executor:
        future = executor.submit(backup_directory_recursive, source, destination)
        future.add_done_callback(lambda x: pbar.update())

def delete_prev_backup(prev_backup):
    try:
        shutil.rmtree(prev_backup)
        print(f'Previous backup deleted: {prev_backup}')
    except Exception as e:
        print(f'Failed to delete previous backup: {e}')

try:
    backup_with_progress(source_directory, f'{backup_directory}/{current_date}')
    print(f'Backup completed on {current_date}')

    # Delete the backup from the previous week
    prev_backup_path = f'{backup_directory}/{prev_week_date}'
    delete_prev_backup(prev_backup_path)

except Exception as e:
    print(f'Backup failed: {e}')
