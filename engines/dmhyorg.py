# -*- coding: utf-8 -*-
#VERSION: 1.0
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


class dmhyorg(object):
    url = "https://share.dmhy.org"
    name = "DMHYORG"
    supported_categories={"all":'0','anime':'2','music':'4','games':'9','tv':'6','pictures':'3'}

    class DMHYHTMLParser(HTMLParser):
        def __init__(self,res,url):
            try:
                super().__init__()
            except:
                HTMLParser.__init__(self)
            self.in_topic_list = False
            self.in_topic_body = False
            self.engine_url = url
            self.results = res
            self.curr = None
            self.curr_name = ""
            self.td_counter = -1
            self.span_counter = -1

        def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
            attrs_dict = dict(attrs)

            if tag == 'table' and attrs_dict.get('id') == "topic_list":
                self.in_topic_list = True

            if tag == "tbody" and self.in_topic_list:
                self.in_topic_body = True

            if tag == "a" and self.in_topic_body:
                self.start_a(attrs)

        def start_a(self,attrs: list[tuple[str, str | None]]):
            params = dict(attrs)
            if params.get('href') and params['href'].startswith("/topics/view/"):
                hit = {'desc_link': self.engine_url + params['href'], 'engine_url': self.engine_url}
                self.curr = hit
                self.in_topic_title = True
                self.td_counter +=1
            elif params.get('href') and params['href'].startswith("magnet:?xt="):
                self.curr['link'] = params['href']


        def end_td(self):
            if self.td_counter >-1 and self.td_counter < 6:
                self.td_counter +=1
            elif self.td_counter ==6:
                self.curr['name'] = self.curr_name
                self.results.append(self.curr)
                self.td_counter = -1
                self.curr = None
                self.curr_name=''



        def handle_data(self, data: str) -> None:

            if self.td_counter >=0 and self.td_counter < 6:
                if self.td_counter == 0:
                    if not data.endswith("條評論"):
                        self.curr_name = f"{self.curr_name} {data.strip()}"
                if self.td_counter == 2:
                    self.curr['size'] = data.strip()
                if self.td_counter == 3:
                    self.curr['seeds'] = int(data) if data.isdigit() else 0
                if self.td_counter == 4:
                    self.curr['leech'] = int(data) if data.isdigit() else 0

        def handle_endtag(self, tag: str) -> None:
            if tag == 'td':
                self.end_td()
            if tag == "tbody":
                self.in_topic_body = False
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
            url = f"{self.url}/topics/list/page/{page}?keyword={what}&sort_id={self.supported_categories[cat]}&order=date-desc"
            results = []
            resp = retrieve_url(url)
            parser = self.DMHYHTMLParser(results,url)
            parser.feed(resp)
            for res in results:
                prettyPrinter(res)
            if len(results)<80:
                break
            page +=1


