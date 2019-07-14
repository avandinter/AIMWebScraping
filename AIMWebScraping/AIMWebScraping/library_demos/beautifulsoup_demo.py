import requests
from bs4 import SoupStrainer, BeautifulSoup, NavigableString


def wrap(to_wrap, wrap_in):
    contents = to_wrap.replace_with(wrap_in)
    wrap_in.append(contents)

def navigate(direction):
    response = requests.get("http://testing-ground.scraping.pro/table")
    soup = BeautifulSoup(response.content, 'html.parser')

    starting_element = soup.select_one("#case_table>table>tbody>tr:nth-child(3)")
    element_html = starting_element

    if starting_element is not None:
        if direction == 'up':
            element_html = starting_element.parent
        elif direction == 'down':
            element_html = starting_element.child
        elif direction == 'forward':
            element_html = starting_element.nextSibling
        elif direction == 'back':
            element_html = starting_element.previousSibling

    return element_html.prettify()


def soup_strainer(tag):
    response = requests.get("http://testing-ground.scraping.pro/table")
    return BeautifulSoup(response.content, "html.parser", parse_only=SoupStrainer(tag)).prettify()

def google_search(search_term):
    response = response = requests.get('https://www.google.com/search', params={'q': search_term})
    soup = BeautifulSoup(response.content, "html.parser")

    result_div = soup.find_all('div', attrs = {'class': 'ZINbbc'})
    link_string = ""

    title_element = soup.new_tag("h3")
    title_element.insert(0, NavigableString(search_term + " Results"))

    ul_element = soup.new_tag("ul")

    for r in result_div:
        try:
            link = r.find('a', href = True)
            title = r.find('div', attrs={'class':'vvjwJb'}).get_text()
            description = r.find('div', attrs={'class':'s3v9rd'}).get_text()

            if link != '' and title != '' and description != '': 
                link['href'] = "https://google.com" + link['href']
                link['target'] = "_blank"

                new_list_element = soup.new_tag("li")
                new_list_element.append(link)

                ul_element.append(new_list_element)
        except:
            continue

    div_element = soup.new_tag("div")
    div_element.append(title_element)
    div_element.append(ul_element)
    return div_element.prettify()
