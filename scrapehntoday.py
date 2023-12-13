import datetime
import os
import pprint
from bs4 import BeautifulSoup
import requests


def get_soup(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return None


def get_links_and_subtext(soup):
    if soup:
        links = soup.select('.titleline>a')
        subtext = soup.select('.subtext')
        print(f"Links found: {len(links)}")
        print(f"Subtexts found: {len(subtext)}")
        return links, subtext
    return [], []


def sort_stories_by_votes(hn_list):
    return sorted(hn_list, key=lambda k: k['votes'], reverse=True)


def create_custom_hn(links, subtext):
    hn = []
    for idx, item in enumerate(links):
        title = item.getText()
        href = item.get('href', None)
        vote = subtext[idx].select('.score')
        if len(vote):
            points = int(vote[0].getText().replace(' points', ''))
            if points > 99:
                hn.append({'title': title, 'link': href, 'votes': points})
    return sort_stories_by_votes(hn)


def get_filename():
    today = datetime.date.today()
    return f"{today}_hn.txt"


def file_exists(filename):
    return os.path.isfile(filename)


def read_previous_links(filename):
    previous_links = set()
    try:
        with open(filename, 'r') as file:
            for line in file:
                if line.startswith('URL:'):
                    previous_links.add(line.strip().split(' ')[1])
    except FileNotFoundError:
        pass
    return previous_links


def main():
    filename = get_filename()
    if file_exists(filename):
        print("A file for today has already been created. Try again tomorrow.")
        return

    soup = get_soup('https://news.ycombinator.com/')
    soup2 = get_soup('https://news.ycombinator.com/news?p=2')
    links, subtext = get_links_and_subtext(soup)
    links2, subtext2 = get_links_and_subtext(soup2)
    mega_links = links + links2
    mega_subtext = subtext + subtext2
    articles = create_custom_hn(mega_links, mega_subtext)

    yesterday_filename = f"{
        datetime.date.today() - datetime.timedelta(days=1)}_hn.txt"
    previous_links = read_previous_links(yesterday_filename)

    with open(filename, 'w') as file:
        for article in articles:
            if article['link'] not in previous_links:
                file.write(f"Title: {article['title']}\nURL: {
                           article['link']}\n\n: {article['votes']}\n\n")

    pprint.pprint(articles)


if __name__ == '__main__':
    main()
