import os
from dotenv import load_dotenv
from utils.misc import JSON, Log
from utils.api import API
from utils.wiki import Wiki
from utils.gui import Gui
from utils.debug import DebugMain

load_dotenv()

debug = False

if debug:
    DebugMain.main()
else:
    wiki = Wiki(id=os.getenv("BOT_ID"), password=os.getenv("BOT_PASSWORD"), url="https://valorantjp.miraheze.org/w/api.php")
    gui = Gui(wiki)

    gui.root.mainloop()