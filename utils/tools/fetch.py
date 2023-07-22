import flet as ft
import urllib.error
import urllib.request
import urllib.parse

from utils.tools.config import Config

from selenium import webdriver
from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.firefox.service import Service as GeckoService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.chrome.service import Service as BraveService

class Fetch:
    def download(url, dst_path):
        with urllib.request.urlopen(url, timeout=10) as web_file:
            data = web_file.read()
            with open(dst_path, mode='wb') as local_file:
                local_file.write(data)

class Webdriver():
    def get():
        try:
            browser = Config.read_key("webdriver")
            if browser=="chrome":
                return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
            elif browser == "firefox":
                return webdriver.Firefox(service=GeckoService(GeckoDriverManager().install()))
            elif browser == "edge":
                return webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))
            elif browser == "brave":
                return webdriver.Chrome(service=BraveService(ChromeDriverManager(chrome_type=ChromeType.BRAVE).install()))
        except:
            return None
    

