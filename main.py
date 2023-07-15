import os
from dotenv import load_dotenv
from utils.core import Core
from utils.debug import DebugMain

load_dotenv()

debug = False

if debug:
    DebugMain.main()
else:
    gui = Core()