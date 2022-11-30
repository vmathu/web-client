import requests
from bs4 import BeautifulSoup

def get_file_links(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    links = soup.find_all("a")
    file_links = [url+link['href']
                  for link in links if link['href'].endswith('pdf')]
    return file_links