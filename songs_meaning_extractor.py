# This is a simple scraper.

__author__ = "Daniel Fernandes Rey"
import sys
import argparse
import requests
import re
import urllib.parse
from bs4 import BeautifulSoup


class Meanings():
    """
    Given a band's name, this class extract a list of songs and their meaning.
    The meaning of the song is the highest rated comment on the page of the song.
    """

    def __init__(self, file_name=None, band_name=None, number_of_songs=None):
        """

        :param file_name: (str): Name of the output file which the comments will be saved.
        :param band_name: (str): Name of the band.
        :param number_of_songs: (str): Number of songs to be retrieved.
        """
        self.file_name = file_name
        self.band_name = band_name
        self.number_of_songs = number_of_songs
        self.initial_url = 'http://songmeanings.com/query/'

    def _get_band_songs_list(self):
        """
        Get the correct band and links to their songs.
        :return: (dict): A dict containing links to the songs and the name of the song.
        """

        params = (
            ('query', self.band_name.lower()),
            ('type', 'artists'),
        )

        response = requests.get(self.initial_url, params=params)
        soup = BeautifulSoup(response.text, "lxml")
        link_band = soup.find("a", href=True, text=self.band_name)['href']

        # Depending on the band's name, the songmeaning.com website returns a page with multiple matchs.
        # So, it's important to get the correct band page.
        # Ex: Band name: 'Cream' returns a page with multiple matchs, so, we get the direct link to the Cream page.

        if link_band:
            absolute_url = urllib.parse.urljoin(self.initial_url, link_band)
            response = requests.get(absolute_url)

        soup = BeautifulSoup(response.text, "lxml")
        links_songs = {}

        for link in soup.find_all('a', href=True):

            url = link['href']
            if '/songs/view/' in url:

                if url not in links_songs:
                    song_name = link.get('title')
                    links_songs[url] = song_name

        return links_songs

    def extract(self):
        """
        Create a file with the name of the songs and the highest rate comment of the song.
        :param (str) band_name: Name of the band.
        """

        links_songs = self._get_band_songs_list()

        items = list(links_songs.items())
        items = items[:self.number_of_songs]

        with open(self.file_name, "a", encoding="utf-8") as f:
            for i in range(len(items)):
                item = items[i]
                url = item[0]
                sog_name = item[1]
                song_name = sog_name.replace(" lyrics", "")
                relative_url = url
                absolute_url = urllib.parse.urljoin(self.initial_url, relative_url)
                highest_comment = self._extract_highest_comment(absolute_url)
                f.write(song_name + "\n")
                f.write(highest_comment + "\n")
                f.write("-" * 30 + "\n")

    def _extract_highest_comment(self, url):
        """
        This method is responsible for the extraction and cleaning of the meaning of the song.
        The highest rated comment is between two 'div' elements. The first 'div' is inside a ul element.
        Since the second 'div' has a lot of blank spaces before the start of the 'div', using regex
        makes the cleaning a lot easier.
        :param (str) url: The url of the song meaning page.
        :return: (str) The highest rated comment cleaned, i.e., stripped of all html tags.
        """
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "lxml")
        divs_info = soup.find("ul", attrs={"class": "comments-list"})
        highest_comment = str(divs_info.find("div", attrs={"class": "text"}))
        result = re.search(r'.*<div class=\"sign\">', highest_comment)
        if result:
            highest_comment = highest_comment[:result.start()]
        clean_comment = BeautifulSoup(highest_comment, "lxml").text
        clean_comment = clean_comment.replace("General Comment", "").lstrip()
        if clean_comment == "None":
            clean_comment = "There are no comments for this song."
        return clean_comment


def main():
    parser = argparse.ArgumentParser(
        description='Obtain the highest rate comment of a song from the band passed as argument.'
                    '\nExample: python songs_meaning_extractor.py --band led zeppelin',
        usage="--band 'name of the name' \n or --band 'name of the band --number_of_songs 10'")

    parser.add_argument('--band', help='Band name', type=str, nargs="+")
    parser.add_argument('--number_of_songs', help='number of songs', type=int, default=None)
    args = parser.parse_args()
    band_name = ' '.join(args.band)
    numbebr_of_songs = args.number_of_songs
    output_file_name = "{}_{}.txt".format(band_name.replace(" ", "_"), "output")
    meaning = Meanings(output_file_name, band_name.title(), numbebr_of_songs)
    meaning.extract()


if __name__ == "__main__":
    main()
