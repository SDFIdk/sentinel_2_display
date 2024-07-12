import os
import re
import subprocess
import shutil

class Utils:

    def extract_utm(file_path):
        """
        Extracts the UTM designator from a given file path.

        Parameters:
        - file_path (str): The path to the file.

        Returns:
        - str: The AA component of the folder name.
        """

        base_dir = os.path.basename(os.path.dirname(file_path))
        
        match = re.match(r'T(\d{2})[A-Z]{3}', base_dir)
        
        if match:
            return match.group(1)
        else:
            raise ValueError(f"{file_path} does not match UTM pattern")

    def run_gdal_calc(command):
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"An error occurred: {e}")

    def safer_remove(path):
        """Attempt to remove a file or directory with retries for locked files."""
        max_retries = 5
        retry_delay = 1  # one second

        for _ in range(max_retries):
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                elif os.path.isfile(path):
                    os.remove(path)
                break
            except Exception as e:
                print(f"# Warning: failed to delete {path} due to {e}")
                time.sleep(retry_delay)
        else:
            print(f"# Error: could not delete {path} after {max_retries} retries.")