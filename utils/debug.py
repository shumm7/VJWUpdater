from utils.vlr import VLR, VLR_Event
from utils.misc import JSON, Log
from utils.api import API
from utils.wiki import Wiki
from utils.gui import Gui
from utils.misc import JSON, Log, String, Fetch, Misc, ApiData
import os

class DebugMain:
    def main():
        event = VLR_Event("1652", "champions-tour-2023-pacific-ascension/group-stage")

        print(event.get_data())