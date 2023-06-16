import requests

from config.constants import WARFRAME_MODS_URL

mod_list = {}

for mod in requests.get(url=WARFRAME_MODS_URL).json():
    if "wikiaThumbnail" in mod:
        mod_list[mod["name"].lower()] = mod["wikiaThumbnail"]
