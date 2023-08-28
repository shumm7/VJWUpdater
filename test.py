import time
import bs4
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Chrome
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


from selenium.webdriver.firefox.service import Service as GeckoService
from webdriver_manager.firefox import GeckoDriverManager

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
#driver = webdriver.Firefox(service=GeckoService(GeckoDriverManager().install()))

driver.get("url here")

WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "article")))
WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located)

tweet_article = driver.find_element(by=By.XPATH, value="//article[@data-testid='tweet']")

print(tweet_article.find_element(by=By.XPATH, value="//div[@data-testid='User-Name']/div[1]").text)
print(tweet_article.find_element(by=By.XPATH, value="//div[@data-testid='User-Name']/div[2]").text)

article_html = tweet_article.find_element(by=By.XPATH, value="//div[@data-testid='tweetText']").get_attribute('innerHTML')
soup: bs4.BeautifulSoup = bs4.BeautifulSoup(article_html, "html.parser")

text = ""
for element in soup.select("span,img"):
    if element.name == "span":
        text += element.text
    elif element.name == "img":
        text += element.attrs["alt"]

print(text)
driver.quit()