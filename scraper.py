import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_news_data():
    url = "https://news.ycombinator.com/"
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return pd.DataFrame(columns=["Baslik", "Link"])

    soup = BeautifulSoup(response.text, 'html.parser')
    
    titles = []
    links = []
    
    items = soup.find_all('span', class_='titleline')
    for item in items[:15]:
        a_tag = item.find('a')
        if a_tag:
            titles.append(a_tag.text)
            links.append(a_tag.get('href'))
            
    df = pd.DataFrame({
        "Baslik": titles,
        "Link": links
    })
    
    return df