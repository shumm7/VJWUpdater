import subprocess
from utils.tools.json import JSON
from utils.tools.assets import Assets

package = JSON.read(Assets.path("assets/package.json"))

version = package.get("version", "")
name = package.get("name", "")
copyright = package.get("copyright", "")

cmd: str = f"flet pack main.py --name \"{name}\" --icon assets/icon.ico --add-data \"assets;assets\" --product-name \"{name}\" --product-version \"{version}\" --copyright \"{copyright}\" --file-version \"{version}\""

subprocess.run(cmd)