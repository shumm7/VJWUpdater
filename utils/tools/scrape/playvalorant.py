import requests
import bs4
import datetime, locale
import time
import re
import urllib.parse

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.common.exceptions as SeleniumExceptions

from utils.tools.wiki import WikiString
from utils.tools.fetch import Webdriver
from utils.tools.localize import Lang

class PlayValorant():
    url: str
    soup: bs4.BeautifulSoup

    locale: str
    title: str
    date: datetime
    category: str
    thumbnail: str
    author: str
    author_role: str
    author_description: str
    tags: list

    def __init__(self, url: str, dateformat: str = None):
        self.url = url

        res = requests.get(self.url)
        res.raise_for_status()
        soup: bs4.BeautifulSoup = bs4.BeautifulSoup(res.text, "html.parser")

        # locale
        o = urllib.parse.urlparse(url).path.split("/")
        self.locale = o[1]

        # dateformat
        if dateformat==None:
            if self.locale in ["ja-jp", "zh-tw", "ar-ae"]: # yy/mm/dd
                dateformat = "%y/%m/%d"
            elif self.locale in ["ko-kr"]: # yy. mm. dd.
                dateformat = "%y. %m. %d."
            elif self.locale in ["en-us"]: # mm/dd/yy
                dateformat = "%m/%d/%y"
            elif self.locale in ["en-gb", "es-es", "fr-fr", "it-it", "es-mx", "id-id", "pt-br", "th-th", "vi-vn"]: #dd/mm/yy
                dateformat = "%d/%m/%y"
            elif self.locale == ["de-de", "pl-pl", "ru-ru", "tr-tr"]: # dd.mm.yy
                dateformat = "%d.%m.%y"

        # title
        self.title = soup.select_one('*[class*="NewsArticleContent-module--title--"] > span').get_text()

        # date
        self.date = datetime.datetime.strptime(soup.select_one('*[class*="copy-02 NewsArticleContent-module--date--"]').get_text(), dateformat)
        if self.locale=="th-th":
            self.date -= datetime.datetime(year=543) # タイ(仏暦)
 
        # category
        self.category = soup.select_one('*[class*="copy-02 NewsArticleContent-module--category--"]').get_text()

        # thumbnail
        style = soup.select_one('div[class*="NewsArticleHero-module--heroBackground--"]').get("style")
        match: re.Match = re.search(r'background-image\:[\s]*url\(\"(.+)\"\)', style, re.DOTALL)
        self.thumbnail = WikiString.remove_url_params(match.group(1))

        # author
        box = soup.select_one('div[class*="NewsArticleContent-module--authorsWrapper--"]')
        self.author = box.select_one('*[class*="heading-05 ArticleAuthorDetail-module--authorTitle--"]').get_text()
        self.author_role = box.select_one('*[class*="copy-02 ArticleAuthorDetail-module--authorRole--"]').get_text()
        self.author_description = box.select_one('*[class*="copy-02 ArticleAuthorDetail-module--authorDescription--"]').get_text()

        # tags
        self.tags = []
        tags = soup.select_one('div[class*="NewsArticleContent-module--tags--"] ul')
        for li in tags.select('li[class*="Tags-module--tagItem--"]'):
            self.tags.append(li.get_text())
    

class ValorantEsports():
    url: str

    title: str
    subtitle: str
    date_raw: str
    thumbnail: str
    author: str = None
    author_role: str = None

    def __init__(self, url: str, wait: float = 0.5) -> None:
        driver = Webdriver.get()

        driver.get(url)
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "article div.e62dc")))
            WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located)
            time.sleep(wait)
        except SeleniumExceptions.TimeoutException:
            raise Exception(Lang.value("common.error_message.webdriver_timeout"))

        try:
            self.url = url
            self.title = driver.find_element(by=By.CSS_SELECTOR, value='div.b7728 h1').text
            self.subtitle = driver.find_element(by=By.CSS_SELECTOR, value='div.b7728 h2').text
            self.thumbnail = WikiString.remove_url_params(driver.find_element(by=By.CSS_SELECTOR, value='div.aea50 img').get_attribute("src"))

            #default_locale = locale.getlocale(locale.LC_TIME)
            self.date_raw = driver.find_element(by=By.CSS_SELECTOR, value='div._0436d div:first-child').text.strip()

            try:
                self.author = driver.find_element(by=By.CSS_SELECTOR, value='div._67595 div._350d9').text
                self.author_role = driver.find_element(by=By.CSS_SELECTOR, value='div._67595 div:not(._350d9)').text
            except SeleniumExceptions.NoSuchElementException:
                pass
        except SeleniumExceptions.NoSuchElementException:
            raise Exception(Lang.value("common.error_message.webdriver_notfound"))
    
    def date(self, _locale: str = "ja-JP", _dateformat = "%Y年%m月%d日") -> datetime:
        locale.setlocale(locale.LC_TIME, _locale.replace("-", "_")+".UTF-8")
        date =  datetime.datetime.strptime(self.date_raw, _dateformat)
        locale.setlocale(locale.LC_TIME, (None,None))
        return date
