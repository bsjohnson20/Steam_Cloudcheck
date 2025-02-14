import requests, json, os, time, logging
import InquirerPy
from requests import Response



import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('main')
logger.setLevel(logging.INFO)

# only show info
log = logging.getLogger('urllib3')
log.setLevel(logging.INFO)

class SteamAppAPI():
    def __init__(self):
        self.app_id_path = "applist.json"
        self.appIDs = {}
    
        self.logger = self.setup_logger()
    
        if os.path.exists(self.app_id_path):
            with open(self.app_id_path, 'r') as f:
                self.appIDs = json.load(f)
                self.logger.debug("Loaded app list from file")
        else:
            self.fetch_app_list()
            self.write_app_list()
            self.debug("Wrote app list to file")
    
    def info(self, message):
        self.logger.info(message)
    
    def error(self, message):
        self.logger.error(message)
    
    def debug(self, message):
        self.logger.debug(message)
    
    def setup_logger(self):
        logger = logging.getLogger('main')
        logger.setLevel(logging.INFO)
        logger.debug("Logger setup done")
        
        return logger
    
    def write_app_list(self):
        self.debug("Writing app list to file")
        with open('applist.json', 'w') as f:
            json.dump(self.allSteamApps, f)        
    
    def fetch_app_list(self) -> Response:
        self.debug("Fetching app list")
        url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
        response = requests.get(url)
        if response.status_code == 200:
            self.info("Successfully fetched app list")
            self.allSteamApps = response.json()
        else:
            self.error(f"Failed to fetch app list: {response.status_code}")
        return response
    def get_game_details(self,app_id) -> dict:
        self.debug(f"Fetching details for app {app_id}")
        url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"
        response = requests.get(url)
        data = response.json()

        if data[str(app_id)]['success']:
            game_data = data[str(app_id)]['data']
            return game_data
        else:
            return 'details not found'

if __name__ == "__main__":
    app = SteamAppAPI()
    