import re
import sys
import logging
import argparse
from urllib.parse import urlparse
from itertools import zip_longest

import requests
from termcolor import colored
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO,
                    format='%(name)s: %(levelname)s: %(message)s')
LOGGER = logging.getLogger('lyrics.py')

BASE_URL = urlparse('https://letras.mus.br')


def _scrape_page(target: str) -> BeautifulSoup:
    try:
        r = requests.get(target, timeout=15)
        r.raise_for_status()
    except Exception as err:
        LOGGER.error(f'{err}')
        sys.exit()

    soup = BeautifulSoup(r.content, 'html.parser')
    return soup


def _url_lyric(artist: str, song: str) -> str:
    artist = artist.lower().replace(' ', '-')
    song = song.lower().replace(' ', '-')
    url = BASE_URL._replace(path=f'{artist}/{song}/traducao.html')
    return url.geturl()


def _url_album(artist: str, album: str) -> str:
    artist = artist.lower().replace(' ', '-')
    search_url = BASE_URL._replace(path=f'{artist}/discografia').geturl()
    soup = _scrape_page(search_url)
    search_album = soup.find('a', string=re.compile(album, re.IGNORECASE))

    # Verify if the album exists.
    if search_album is None:
        LOGGER.error(f'Album "{album}" not found on {search_url}')
        sys.exit()
    else:
        url = BASE_URL._replace(path=search_album['href'])
        return url.geturl()


def _black_white(text: str, *attrs: str) -> str:
    return colored(text, 'white', attrs=('reverse',) + attrs)


def parse_lyric(artist: str, song: str) -> dict[str, str]:
    soup = _scrape_page(_url_lyric(artist, song))
    artist_name = soup.find(class_='cnt-head_title').find('span').text.strip()
    # Original lyric with song name.
    lyric = [
        text.get_text('\n', strip=True)
        for text in soup.find(class_='cnt-trad_l').find_all(['p', 'h3'])
    ]
    # Translated lyric with song name.
    translation = [
        text.get_text('\n', strip=True)
        for text in soup.find(class_='cnt-trad_r').find_all(['p', 'h3'])
    ]
    # Get song name.
    song_name = lyric.pop(0)
    translated_name = translation.pop(0)
    return {
        'artist': artist_name,
        'song': song_name,
        'translated': translated_name,
        'lyric': '\n\n'.join(lyric),
        'translation': '\n\n'.join(translation),
    }


def parse_album(artist: str, album: str) -> list[str]:
    # Implement later, this will get the _url_album() and return a list
    # with all the songs of the album and the parse_lyric() will parser
    # the lyric for each song to save to db.
    pass


def print_lyric(artist: str,
                song_name: str,
                translated_name: str,
                lyric: str,
                translation: str,
                translate: bool) -> None:
    by = artist.title()
    title = song_name
    if translate:
        by = _black_white(by, 'bold', 'underline')
        title = f'{song_name}\n{_black_white(translated_name, "bold")}'
        lyric_lines = lyric.splitlines()
        translation_lines = translation.splitlines()
        lines = zip_longest(lyric_lines, translation_lines, fillvalue='')
        lyric = '\n'.join([
            (f'{line[0]}\n{_black_white(line[1], "bold")}')
            for line in lines
        ])

    print(by)
    print(title, end='\n\n')
    print(lyric)


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Lyric of your favorite song directly on your terminal'
    )
    parser.version = '1.0.0'
    parser.add_argument('artist',
                        help='artist or band name')

    parser.add_argument('song',
                        help='song name')

    parser.add_argument('-t',
                        '--translate',
                        action='store_true',
                        help='translate the lyric')

    parser.add_argument('-v',
                        '--version',
                        action='version')
    return parser.parse_args()


def main() -> None:
    args = get_args()
    lyric_info = parse_lyric(args.artist, args.song)
    print_lyric(lyric_info['artist'],
                lyric_info['song'],
                lyric_info['translated'],
                lyric_info['lyric'],
                lyric_info['translation'],
                args.translate)


if __name__ == '__main__':
    main()
