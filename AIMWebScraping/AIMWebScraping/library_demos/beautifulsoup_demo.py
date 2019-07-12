import requests
from bs4 import SoupStrainer, BeautifulSoup

def navigate(direction):
    response = requests.get("http://testing-ground.scraping.pro/table")
    page = BeautifulSoup(response.content, 'html.parser')

    starting_element = page.select("#case_table>table>tbody>tr:nth-child(3)>td:nth-child(5)")
    print(starting_element)
    element_html = starting_element.prettify()
    if starting_element is not None:
        if direction == 'up':
            element_html = starting_element.parent.prettify()
    return element_html
            
