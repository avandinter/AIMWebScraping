import requests
from bs4 import SoupStrainer, BeautifulSoup

def navigate(direction):
    response = requests.get("http://testing-ground.scraping.pro/table")
    page = BeautifulSoup(response.content, 'html.parser')

    starting_element = page.select_one("#case_table>table>tbody>tr:nth-child(3)")
    print(starting_element)
    element_html = starting_element.prettify()

    if starting_element is not None:
        if direction == 'up':
            element_html = starting_element.parent.prettify()
        elif direction == 'down':
            element_html = starting_element.child.prettify()
        elif direction == 'forward':
            element_html = starting_element.nextSibling.prettify()
        elif direction == 'back':
            element_html = starting_element.previousSibling.prettify()

    return element_html


def soup_strainer():
    response = requests.get("http://testing-ground.scraping.pro/table")
    return BeautifulSoup(response.content, "html.parser", parse_only=SoupStrainer("td")).prettify()
