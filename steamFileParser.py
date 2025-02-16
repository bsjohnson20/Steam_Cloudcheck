# parses a passed file and returns maps games installed
import os, re

import platform

from InquirerPy import inquirer, prompt
from InquirerPy.validator import PathValidator

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('main')


# To be inherited by main class with logger
class SteamInstalledParser:
    def get_user_input(self):
        pass
    def __init__(self, file=''):
        self.vdf = file
    
    def user_input(self):
        """
        Prompts user to enter path to steam's libraryfolders.vdf file
        
        Validates file exists
        """
        home_path = "~/.steam/debian-installation/steamapps/libraryfolders.vdf" if os.name == "posix" else "C:\Program Files (x86)\Steam\config\libraryfolders.vdf"
        src_path = inquirer.filepath(
            message="Enter path to steam's libraryfolders.vdf:",
            default=home_path,
            validate=PathValidator(is_file=True, message="Input is not a file"),
            only_files=True,
        ).execute()
        self.vdf = src_path

        
    def parse_vdf(self):
        self.debug(f"Parsing vdf {self.vdf}")
        
        # convert relative path to absolute path
        # Not sure on windows
        if platform.system() == "Windows":
            self.vdf = os.path.abspath(self.vdf)
        else:
            self.vdf = os.path.expanduser(self.vdf)
        
        with open(self.vdf, 'r') as f:
            data = f.read()
            matches = re.findall(r"[0-9]+\".+\"[0-9]+", data)
            # print(matches)
            self.gameIDs= set([int(x.split('\"')[0]) for x in matches])
            logger.debug(f"Found {len(self.gameIDs)} games")
            return self.gameIDs
            
            
if __name__ == "__main__":
    parser = SteamInstalledParser()
            