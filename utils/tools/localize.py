import os
from utils.tools.config import Config
from utils.tools.json import JSON
from utils.tools.assets import Assets

class Lang:
    def get_current_language() -> str:
        return Config.read()["lang"]
    
    def value(key: str, lang: str = None) -> str:
        if lang==None:
            lang = Lang.get_current_language()

        if os.path.exists(Assets.path(f"assets/lang/{lang}.json")):
            localize = JSON.read(Assets.path(f"assets/lang/{lang}.json"))
            keys = key.split(".")

            for k in keys:
                localize = localize.get(k, f"{lang}.{key}")
                if type(localize)==str:
                    return localize

            return f"{lang}.{key}"
        else:
            return f"{lang}.{key}"
        
