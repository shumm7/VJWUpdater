import tkinter, os, datetime, math
import tkinter.simpledialog
from tkinter import messagebox
from tkinter import ttk
from tkinter import simpledialog
from utils.misc import JSON, Log, String, Fetch, Misc, ApiData
from utils.api import API
from utils.wiki import Wiki
from utils.vlr import VLR, VLR_Event

from utils.cogs.cache import Cache
from utils.cogs.update import Update
from utils.cogs.wikitext import Wikitext
from utils.cogs.list import List
from utils.cogs.esports import Esports

class Core():
    root: tkinter.Tk
    wiki: Wiki
    force: bool = False

    cache: Cache
    update: Update
    wikitext: Wikitext
    list: List
    esports: Esports

    def __init__(self, root: tkinter.Tk, wiki: Wiki) -> None:
        self.root = root
        self.wiki = wiki

        self.cache = Cache(self.root, self.wiki)
        self.update = Update(self.root, self.wiki, self.force)
        self.wikitext = Wikitext(self.root, self.wiki, self.force)
        self.list = List(self.root, self.wiki, self.force)
        self.esports = Esports(self.root, self.wiki, self.force)
