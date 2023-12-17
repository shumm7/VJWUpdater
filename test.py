from utils.tools.json import JSON
from utils.tools.fetch import Fetch
from utils.tools.api import API

agents = JSON.read("api/agents.json")
str = ""

for agent in agents:
    for ability in agent["abilities"]:
        agent_name = agent["displayName"]["en-US"]
        name: str = ability["displayName"]["en-US"]
        name_jp: str = ability["displayName"]["ja-JP"]
        description = ability["description"]["ja-JP"]
        keys = {"Ability1": "Q",  "Ability2": "E", "Grenade": "C", "Ultimate": "X"}
        key = keys.get(ability["slot"], "")

        str += f"	[\"{name.lower()}\"] = " + "{ " + f"name=\"{name_jp}\", [\"name-latin\"]=\"{name}\", link=\"{name_jp}\", icon=\"{name} Icon.png\", description=\"{description}\", key=\"{key}\", agent=\"{agent_name}\"" + " },\n"  
        str += f"	[\"{name_jp.lower()}\"] = \"{name.lower()}\",\n"

with open("abilities.txt", "w") as f:
    f.write(str)