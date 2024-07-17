import os
import zipfile
import shutil
from constants.constants import Constants

class SAFE_handler:
    """
    Functions that take the place of unzip_files.py and move_and_clean_jp2.py
    """
    
    def unzip_files(zip_folder, garbage_collect):
        for root, _, files in os.walk(zip_folder):
            for file in files:

                if file.endswith('.zip'):
                    file_path = os.path.join(root, file)
                    extract_path = os.path.splitext(file_path)[0]

                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        zip_ref.extractall(extract_path)

                    if garbage_collect: os.remove(file_path)

                    # Create a .done file with the same name as the output dir
                    with open(f'{extract_path}.done', 'w') as done_file:
                        done_file.write('Extraction complete')

    def find_files(root_folder, pattern):
        """
        Find files in a directory tree matching the given pattern.
        this is just a glob...
        """
        for root, _, files in os.walk(root_folder):
            for name in files:
                if name.endswith(pattern):
                    yield os.path.join(root, name)

    def move_files(source_dir, target_dir, file_patterns):
        """
        Move files to a new dir, overwriting if necessary.
        """
        for band_name in file_patterns:
            for filepath in SAFE_handler.find_files(source_dir, band_name):

                new_filepath = os.path.join(target_dir, band_name)
                shutil.move(filepath, new_filepath)

    def process_dir(safe_dir, date_dir):
        """
        Process each .done file in the download dir.
        """
        done_files = list(SAFE_handler.find_files(safe_dir, ".done"))

        tile_ids = []
        for done_file in done_files:
            safe_file = os.path.basename(done_file).replace(".done", "")
            
            tile_id = f"{safe_file.split('_')[5][1:]}" #tile_id section of std sentinel-2 safe filename

            unzipped_safe = os.path.join(safe_dir, safe_file)
            tile_dir = os.path.join(date_dir, tile_id)
            os.makedirs(tile_dir, exist_ok=True)

            SAFE_handler.move_files(unzipped_safe, tile_dir, Constants.get_s2_granules())
            if not tile_dir in tile_ids: tile_ids.append(tile_dir)

            #a dead end? These files are never used
            processed_file = done_file.replace(".done", ".processed")
            os.replace(done_file, processed_file)

            mark_file_path = os.path.join(date_dir, f"{tile_id}.mark")
            open(mark_file_path, 'a').close()

        return tile_ids