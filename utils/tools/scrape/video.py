import requests
import bs4
import datetime, locale
import time
import re
import urllib.parse
import dateutil.parser
from googleapiclient.discovery import build

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.common.exceptions as SeleniumExceptions

from utils.tools.wiki import WikiString
from utils.tools.fetch import Webdriver
from utils.tools.localize import Lang
from utils.tools.config import Config
from utils.tools.json import JSON

class YouTube():
    url: str
    soup: bs4.BeautifulSoup

    api_key: str = Config.read_key("youtube_api")
    api_service_name: str = 'youtube'
    api_version: str = 'v3'

    video_id: str
    date: datetime
    description: str

    channel_id: str
    channel_url: str
    channel_title: str
    channel_description: str
    channel_date: datetime
    channel_thumbnail: str

    def __init__(self, url: str, wait: float = 0.5):
        parse = urllib.parse.urlparse(url)
        print(parse)
        query = urllib.parse.parse_qs(parse.query)
        if parse.netloc=="www.youtube.com" or parse.netloc=="youtube.com":
            if parse.path == "/watch":
                self.video_id = query["v"][0]
            else:
                raise ValueError("Invalid URL.")
        elif parse.netloc == "youtu.be":
            self.video_id = parse.path[1:]
        else:
            self.video_id = url
        
        self.url = f"https://www.youtube.com/watch?v={self.video_id}"

        self.api = build(
            self.api_service_name,
            self.api_version,
            developerKey = self.api_key
        )
    
    def video(self, video_id: str = None):
        if video_id==None:
            video_id = self.video_id

        # video
        video = self.api.videos().list(
            part = 'snippet,statistics',
            id = video_id
        ).execute()

        data = video["items"][0]

        self.date = dateutil.parser.parse(data["snippet"]["publishedAt"])
        self.channel_id = data["snippet"]["channelId"]
        self.title = data["snippet"]["title"]
        self.description = data["snippet"]["description"]
        self.channel_title = data["snippet"]["channelTitle"]

        max_size = -1
        for thumbnail in data["snippet"]["thumbnails"].values():
            size = thumbnail["width"] * thumbnail["height"]

            if max_size<size:
                max_size = size
                self.thumbnail = thumbnail["url"]
    
    def channel(self, channel_id: str=None):
        if channel_id==None:
            channel_id = self.channel_id
        
        chan = self.api.channels().list(
            part = 'snippet,statistics',
            id = channel_id
        ).execute()

        data = chan["items"][0]

        self.channel_title = data["snippet"]["title"]
        self.channel_description = data["snippet"]["description"]
        self.channel_url = data["snippet"].get("customUrl")
        self.channel_date = dateutil.parser.parse(data["snippet"]["publishedAt"])

        max_size = -1
        for thumbnail in data["snippet"]["thumbnails"].values():
            size = thumbnail["width"] * thumbnail["height"]

            if max_size<size:
                max_size = size
                self.channel_thumbnail = thumbnail["url"]


