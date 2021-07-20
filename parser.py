import requests
from bs4 import BeautifulSoup

URL = "https://www.dotabuff.com/players/297342965"
HEADERS = {'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
           'accept': 'text/css,*/*;q=0.1'}


def get_html(url):
    r = requests.get(url, headers=HEADERS)
    return r


def parse(url):  # вызывать эту функцию
    html = get_html(url)
    if html.status_code == 200:

        soup = BeautifulSoup(html.text, 'html.parser')

        name_class = soup.find('div', class_="header-content-title")
        name_block = name_class.find("h1").get_text()
        name_reverse = name_block[-9::-1]
        name = name_reverse[::-1]

        time_class = soup.find('div', class_="header-content-secondary")
        time_block = time_class.find("time").get_text("title")

        win_loss_abandons_class = soup.find('div', class_="header-content-secondary")
        win_block = win_loss_abandons_class.find(class_="wins").get_text()
        loss_block = win_loss_abandons_class.find(class_="losses").get_text()
        abandons_block = win_loss_abandons_class.find(class_="abandons").get_text()

        win_ratio_class = soup.find('div', class_="header-content-secondary")
        win_ratio_block = win_ratio_class.find_all("dl")
        for elements in win_ratio_block:
            calc = 0
            if calc == 2:
                break
            else:
                calc += 1
        win_ratio = elements.get_text()
        win_ratio = win_ratio[-9::-1]
        win_ratio = win_ratio[::-1]

        results = {
            "player_name": name,
            "last_match": time_block,
            "wins": win_block,
            "losses": loss_block,
            "abandons": abandons_block,
            "win_rate": win_ratio
        }

    else:
        print('Error')

    return results


if __name__ == '__main__':
    clown = parse(URL)
    print(clown)
