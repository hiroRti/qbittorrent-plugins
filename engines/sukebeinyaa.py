# -*- coding: utf-8 -*-
# VERSION: 1.0
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

try:
    from HTMLParser import HTMLParser
except ImportError:
    from html.parser import HTMLParser
from helpers import retrieve_url
from novaprinter import prettyPrinter


class sukebeinyaa(object):
    url = "https://sukebei.nyaa.si"
    name = "sukebeinyaa"
    supported_categories = {"all": '0_0', 'anime': '1_1','games': '1_3', 'tv': '2_2', 'pictures': '1_5'}

    class NYAAHTMLParser(HTMLParser):
        def __init__(self, res, url):
            try:
                super().__init__()
            except:
                HTMLParser.__init__(self)
            self.in_topic_list = False
            self.engine_url = url
            self.results = res
            self.curr = None
            self.td_counter = -1
            self.span_counter = -1

        def handle_starttag(self, tag, attrs):
            attrs_dict = dict(attrs)

            if tag == 'table' and attrs_dict.get('class') == "table table-bordered table-hover table-striped torrent-list":
                self.in_topic_list = True

            if tag == "a" and self.in_topic_list:
                self.start_a(attrs)

        def start_a(self, attrs):
            params = dict(attrs)
            if params.get('href') and params['href'].startswith("/view/"):
                hit = {'desc_link': self.engine_url + params['href'], 'engine_url': self.engine_url}
                self.curr = hit
                self.curr['name'] = params.get('title')
                self.td_counter += 1
            elif params.get('href') and params['href'].startswith("magnet"):
                self.curr['link'] = params['href']

        def end_td(self):
            if -1 < self.td_counter < 6:
                self.td_counter += 1
            elif self.td_counter == 6:
                self.results.append(self.curr)
                self.td_counter = -1
                self.curr = None

        def handle_data(self, data):
            data = data.strip()
            if 0 <= self.td_counter < 7:
                if self.td_counter == 2:
                    self.curr['size'] = data
                elif self.td_counter == 4:
                    self.curr['seeds'] = int(data) if data.isdigit() else 0
                elif self.td_counter == 5:
                    self.curr['leech'] = int(data) if data.isdigit() else 0

        def handle_endtag(self, tag):
            if tag == 'td':
                self.end_td()
            if tag == "table":
                self.in_topic_list = False

    def search(self, what, cat='all'):
        """
        Here you can do what you want to get the result from the search engine website.
        Everytime you parse a result line, store it in a dictionary
        and call the prettyPrint(your_dict) function.

        `what` is a string with the search tokens, already escaped (e.g. "Ubuntu+Linux")
        `cat` is the name of a search category in ('all', 'movies', 'tv', 'music', 'games', 'anime', 'software', 'pictures', 'books')
        """
        page = 1
        while True:
            search_url = f"{self.url}/?f=0&c={self.supported_categories[cat]}&q={what}&p={page}"
            results = []
            resp = retrieve_url(search_url)
            parser = self.NYAAHTMLParser(results, self.url)
            parser.feed(resp)
            for res in results:
                prettyPrinter(res)
            if len(results) < 75:
                break
            page += 1