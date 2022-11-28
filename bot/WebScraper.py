import requests
from bs4 import BeautifulSoup
import re

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.30 Safari/537.36" ,
            "Content-type": "application/json",}


class Webscraper:
    
    def __init__(self, url):
        self.url = url
        self.website = requests.get(self.url, headers = headers)
        self.soup = BeautifulSoup(self.website.content, 'html.parser')

    def status(self) -> int:
        """ retuns the status of the website """
        return self.website.status_code
    
    def scrape(self,class_) -> dict:
        """ scrape the website drop-down list as per 'id' """
        s = self.soup.find('ul', class_ = class_) # nav menu menu-treemenu
        _s = s.find_all('a',href = True)
        return {a.find('span').text: self.url+a['href'] if not re.search(r"((http(s)?:\/\/))",a['href']) else a['href'] for a in _s if a.find('span')}

