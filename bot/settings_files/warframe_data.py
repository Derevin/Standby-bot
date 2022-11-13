import requests

MODS_URL = (
    "https://raw.githubusercontent.com/WFCD/warframe-items/master/data/json/Mods.json"
)
r = requests.get(url=MODS_URL)
mod_data = r.json()

mod_list = {}

for mod in mod_data:

    if "wikiaThumbnail" in mod:
        mod_list[mod["name"].lower()] = mod["wikiaThumbnail"]
