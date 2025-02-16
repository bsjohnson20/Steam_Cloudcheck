
import sys
# Just works. Don't know why
sys.path.append('.')

import steam_app_api
from colorama import Fore, Back, Style

def test_fetch_app_list():
    api = steam_app_api.SteamAppAPI()
    response = api.fetch_app_list()
    assert response.status_code == 200
    
def test_get_game_details():
    api = steam_app_api.SteamAppAPI()
    app_id = 728880
    game_data = api.get_game_details(app_id)
    assert game_data
    
def test_cloud_support_true():
    api = steam_app_api.SteamAppAPI()
    app_id = 728880
    cloud = api.game_has_cloud(app_id)
    assert cloud == True
    
def test_cloud_support_false():
    api = steam_app_api.SteamAppAPI()
    app_id = 728881
    cloud = api.game_has_cloud(app_id)
    assert cloud == False

