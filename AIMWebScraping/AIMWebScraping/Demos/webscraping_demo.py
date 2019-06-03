import requests
import bs4

class webscraping_demo(object):
    def requests_google_search(self, search):
        return str(self.__get_google_search(search).text)

    def bs4_google_search(self, search):
        results = self.__get_google_search(search)


    def __get_google_search(self, search):
        return requests.get("http://www.google.com/search", params={'q': search, 'first': 1})


