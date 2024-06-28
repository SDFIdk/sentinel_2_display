import os
import re
import subprocess

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