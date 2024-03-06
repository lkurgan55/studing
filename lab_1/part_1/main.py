from bs4 import BeautifulSoup
import requests
from time import sleep

url = 'https://lb.ua/politics/newsfeed'
params = {
    'page': 0
}

date = '15 лютого'

while True: # find news by date
    r = requests.get(url, params)
    soup = BeautifulSoup(r.content, 'html.parser')

    dates = {
        date.text.split(', ')[1].lower()
        for date in soup.findAll('li', {'class': 'caption list-item-caption'})
    }

    if date in dates:
        break

    params['page'] += 1

# lenta = soup.find('ul', {'class': 'lenta'})
# lenta = lenta.find_all('li')
# news = []
# save_news = False

# for item in lenta:
#     if 'adv-block' in item['class']:
#         continue

#     if 'caption' in item['class']:
#         if date in item.text.lower():
#             save_news = True # start saving new for the date
#         elif save_news:
#             break
#         continue

#     if save_news:
#         new_url = item.find('div', {'class': 'title'}).findChild("a")['href']
#         print(new_url)
#         # news.append(
#         #
#         # )

def parse_new(url: str = 'https://lb.ua/news/2024/02/15/598655_iermak_obgovoriv_iz_radnikom.html'):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    print(soup)
    article = soup.find('h1', {'itemprop': 'headline'}).text
    header = soup.find('div', {'itemprop': 'description'}).find('p').text
    all_text = soup.find('div', {'itemprop': 'articleBody'}).text
    return {
        "article": article,
        "link": url,
        "header": header,
        "text": 'all_text',
        "header_ner": [
            [
                "Україна",
                "LOC"
            ]
        ],
        "text_ner": [
            [
                "України",
                "LOC"
            ]
        ]
    }

print(parse_new())