import InquirerPy.inquirer
import requests, json, os, time, logging
import InquirerPy
from requests import Response

from steamFileParser import SteamInstalledParser
from steam_app_api import SteamAppAPI

from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
logger = logging.getLogger('main')
import sys
from colorama import Fore, Back, Style

def progressbar(it, prefix="", size=60, out=sys.stdout): # Python3.6+
    count = len(it)
    start = time.time() # time estimate start
    def show(j):
        x = int(size*j/count)
        # time estimate calculation and string
        remaining = ((time.time() - start) / j) * (count - j)        
        mins, sec = divmod(remaining, 60) # limited to minutes
        time_str = f"{int(mins):02}:{sec:03.1f}"
        print(f"{prefix}[{u'█'*x}{('.'*(size-x))}] {j}/{count} Est wait {time_str}", end='\r', file=out, flush=True)
    show(0.1) # avoid div/0 
    for i, item in enumerate(it):
        yield item
        show(i+1)
    print("\n", flush=True, file=out)

class main(SteamInstalledParser, SteamAppAPI):
    def __init__(self):
        SteamInstalledParser.__init__(self)
        SteamAppAPI.__init__(self)
    
        self.banner()
        
        self.user_input()
        self.parse_vdf()
        
        # fetch app list
        self.fetch_app_list()
        self.gameNames = dict([(x['appid'], x['name']) for x in self.allSteamApps['applist']['apps'] if x['appid'] in self.gameIDs])
        
        # replace appids without name with "Unknown"
        for i in self.gameIDs:
            if i not in self.gameNames:
                self.gameNames[i] = "Unknown"
        
        logger.debug(self.gameNames)
        # Display prompt 
        action = InquirerPy.inquirer.select(
        message="Select an action:",
        choices=[
            "1. Check specific gameID",
            "2. Check all games in library (vdf)",
            Choice(value=None, name="Exit"),
        ],
        default=None,
        )
        action.execute()
        # print((action.result_value))
    
        match action.result_value:
            case "1. Check specific gameID":
                self.user_single_input()
            case "2. Check all games in library (vdf)":
                self.check_cloud()
            case _:
                self.logger.info("Goodbye")
    
    # Provide input for one gameID
    def user_single_input(self):
        action = InquirerPy.inquirer.text(
            message="Enter gameID:",
            default="",
            validate=InquirerPy.validator.NumberValidator(message="Invalid input"),
        ).execute()
        # Print GameID and green cloud if supported, else red cloud
        print(f"GameID {Fore.GREEN}{self.gameNames[int(action)]}{Style.RESET_ALL}: {Fore.GREEN if self.game_has_cloud(action) else Fore.RED}Cloud{Style.RESET_ALL}.")
        
    
    def game_has_cloud(self,app_id):
        js = self.get_game_details(app_id)
        if js == 'details not found':
            # print("details not found")
            return False
        try:
            categories = {category['id']: category['description'] for category in js['categories']}
            categories[23]
            return True

        except KeyError:
            # print("Key Error")
            return False
    
    def formatter(self, gameList, item):
        # Example output: GameID <blue>3490390_Sandustry Demo: <green>Cloud .
        return f"GameID {Fore.CYAN}{item}_{self.gameNames[int(item)]}{Style.RESET_ALL}: {Fore.GREEN if gameList[item] else Fore.RED}Cloud{Style.RESET_ALL}."
    
    def setup_gameNames(self):
        self.gameNames = dict([(x['appid'], x['name']) for x in self.allSteamApps['applist']['apps'] if x['appid'] in self.gameIDs])
    
    def sortCloudList(self, supported: dict) -> dict:
        # Start with cloud supported then non cloud supported
        # Ideally print Cloud supported + unknown game > cloud not supported + unknown game
        supported = {k: v for k, v in sorted(supported.items(), key=lambda item: item[1], reverse=True)}
        return supported
    
    
    def check_cloud(self):
        # check if supported.txt exists
        if os.path.exists("supported.txt"):
            force = InquirerPy.inquirer.confirm(
                message="supported.txt already exists. Do you want to overwrite it or view?",
                default=True,
            ).execute()
            if not force:
                with open("supported.txt", "r") as f:
                    data = f.read()
                    supported = json.loads(data)
                    logger.debug(supported.keys())

                    # update gameIDs with supported
                    self.gameIDs.union(supported.keys())
                    
                    self.setup_gameNames()
                    
                    
                    for item in supported.keys():
                        if int(item) not in self.gameNames.keys():
                            logger.debug(f"Item: {item}, not in self.gameNames, {self.gameNames}")
                            self.gameNames[int(item)] = "Unknown"
                            
                    supported = self.sortCloudList(supported)
                    
                    logger.debug(f"###############\n##############\nKEY asdasdsas {supported},\n######,{self.gameNames}")

                    logger.debug(f"Supported {supported}")
                    for item in supported:
                        print(self.formatter(supported, item))
                return
        
        supported = {}
        for game in progressbar(self.gameIDs):
            if self.game_has_cloud(game):
                supported[game] = True
            else:
                supported[game] = False
        self.gameIDs.union(supported.keys())
        self.setup_gameNames()
                    
        for item in supported.keys():
            if int(item) not in self.gameNames.keys():
                logger.debug(f"Item: {item}, not in self.gameNames, {self.gameNames}")
                self.gameNames[int(item)] = "Unknown"

        for item in supported:
            print(self.formatter(supported, item)) 
        
        with open("supported.txt", "w") as f:
            json.dump(supported, f)
            
    
    def banner(self):
        self.logger.info("Welcome to SteamFileParser")
        print(
            """ :::::::: ::::::::::: ::::::::::     :::     ::::    ::::         ::::::::  :::        ::::::::  :::    ::: :::::::::        :::::::::     :::     :::::::::   ::::::::  :::::::::: :::::::::  
:+:    :+:    :+:     :+:          :+: :+:   +:+:+: :+:+:+       :+:    :+: :+:       :+:    :+: :+:    :+: :+:    :+:       :+:    :+:  :+: :+:   :+:    :+: :+:    :+: :+:        :+:    :+: 
+:+           +:+     +:+         +:+   +:+  +:+ +:+:+ +:+       +:+        +:+       +:+    +:+ +:+    +:+ +:+    +:+       +:+    +:+ +:+   +:+  +:+    +:+ +:+        +:+        +:+    +:+ 
+#++:++#++    +#+     +#++:++#   +#++:++#++: +#+  +:+  +#+       +#+        +#+       +#+    +:+ +#+    +:+ +#+    +:+       +#++:++#+ +#++:++#++: +#++:++#:  +#++:++#++ +#++:++#   +#++:++#:  
       +#+    +#+     +#+        +#+     +#+ +#+       +#+       +#+        +#+       +#+    +#+ +#+    +#+ +#+    +#+       +#+       +#+     +#+ +#+    +#+        +#+ +#+        +#+    +#+ 
#+#    #+#    #+#     #+#        #+#     #+# #+#       #+#       #+#    #+# #+#       #+#    #+# #+#    #+# #+#    #+#       #+#       #+#     #+# #+#    #+# #+#    #+# #+#        #+#    #+# 
 ########     ###     ########## ###     ### ###       ###        ########  ########## ########   ########  #########        ###       ###     ### ###    ###  ########  ########## ###    ###
 # """)
    
    

if __name__ == "__main__":
    main()