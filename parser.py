import requests
from bs4 import BeautifulSoup

HEADERS = {'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
           'accept': 'text/css,*/*;q=0.1'}


def get_html(url):
    ur = 'https://www.dotabuff.com/'
    slice = url[0:25:]
    if ur == slice:
        r = requests.get(url, headers=HEADERS)
        return r
    else:
        return None


def parse(url):  # вызывать эту функцию
    html = get_html(url)
    if html is not None:

        if html.status_code == 200:

            soup = BeautifulSoup(html.text, 'html.parser')

            name_class = soup.find('div', class_="header-content-title")
            name_block = name_class.find("h1").get_text()
            name_reverse = name_block[-9::-1]
            name = name_reverse[::-1]

            stats_block = soup.find('div', class_="header-content-secondary").get_text(separator="\n").split(sep="\n")

            time_block = stats_block[0]
            win_block = stats_block[2]
            loss_block = stats_block[4]
            abandons_block = stats_block[6]
            win_ratio = stats_block[8]

            profile_quality = soup.find('div', class_="profile-quality").get_text(separator="\n").split(sep='\n')

            profile_qual = profile_quality[0]
            ts_data_overview = profile_quality[1]
            ts_recent_text = profile_quality[2]
            ts_recent_score = profile_quality[3]
            ts_total_text = profile_quality[4]
            ts_total_score = profile_quality[5]
            ts_plus_text = profile_quality[6]
            ts_plus_score = "DotaBuff Plus subscription not purchased"
            if len(profile_quality) == 8:
                ts_plus_score = profile_quality[7]

            results = {
                "player_name": name,
                "last_match": time_block,
                "wins": win_block,
                "losses": loss_block,
                "abandons": abandons_block,
                "win_rate": win_ratio,
                "ts_recent_text": ts_recent_text,
                "ts_recent_score": ts_recent_score,
                "ts_total_text": ts_total_text,
                "ts_total_score": ts_total_score,
                "ts_plus_text": ts_plus_text,
                "ts_plus_score": ts_plus_score,
                "profile-qual": profile_qual,
                "ts_data_overview": ts_data_overview
            }

            return results
        else:
            return 1

    else:
        return None

