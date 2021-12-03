import json
import requests
import re


MODS_URL = "https://raw.githubusercontent.com/WFCD/warframe-items/development/data/json/Mods.json"
r = requests.get(url=MODS_URL)
# mod_data = r.json()
mod_data = {}

mod_list = {}

for mod in mod_data:

    if "wikiaThumbnail" in mod:
        mod_list[mod["name"].lower()] = mod["wikiaThumbnail"]

    elif mod["name"] == "Cunning Drift":
        mod_list[
            mod["name"].lower()
        ] = "https://vignette.wikia.nocookie.net/warframe/images/9/9c/Cunning_drift.png/revision/latest"

