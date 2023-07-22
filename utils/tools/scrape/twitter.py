import datetime, locale, dateutil.parser
import time
import bs4
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.common.exceptions as SeleniumExceptions

from utils.tools.wiki import WikiString
from utils.tools.fetch import Webdriver
from utils.tools.localize import Lang

class Tweet():
    url: str

    def __init__(self, url: str, wait: float = 0.5) -> None:
        driver = Webdriver.get()

        driver.get(url)
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "article")))
            WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located)
            time.sleep(wait)
        except SeleniumExceptions.TimeoutException:
            raise Exception(Lang.value("common.error_message.webdriver_timeout"))
        
        
        self.url = WikiString.remove_url_params(url)
        
        article_html: str
        photo_html: str
        try:
            tweet_article = driver.find_element(by=By.XPATH, value="//article[@data-testid='tweet']")

            # username / id
            self.username = tweet_article.find_element(by=By.XPATH, value="//div[@data-testid='User-Name']/div[1]").text
            self.id = tweet_article.find_element(by=By.XPATH, value="//div[@data-testid='User-Name']/div[2]").text

            article_html = tweet_article.find_element(by=By.XPATH, value="//div[@data-testid='tweetText']").get_attribute('innerHTML')
            photo_html = tweet_article.find_element(by=By.XPATH, value="//div[@data-testid='tweetPhoto']").get_attribute('innerHTML')

        except SeleniumExceptions.NoSuchElementException:
            raise Exception(Lang.value("common.error_message.webdriver_notfound"))
        
        # tweet text
        self.text = ""
        soup: bs4.BeautifulSoup = bs4.BeautifulSoup(article_html, "html.parser")
        for element in soup.select("span,img"):
            if element.name == "span":
                self.text += element.text
            elif element.name == "img":
                self.text += element.attrs["alt"]

        # image
        self.image = []
        soup: bs4.BeautifulSoup = bs4.BeautifulSoup(photo_html, "html.parser")
        for element in soup.select("img"):
            self.image.append(element.attrs["src"])

        # date
        date = tweet_article.find_element(by=By.TAG_NAME, value="time").get_attribute("datetime")
        self.date = dateutil.parser.parse(date).astimezone(datetime.timezone(datetime.timedelta(hours=+9), 'JST'))
        