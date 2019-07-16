from datetime import datetime
from flask import render_template, request, jsonify
import json
import os
from glob import glob
from AIMWebScraping import app
from AIMWebScraping.lego_price_scraper import init
from AIMWebScraping.library_demos import requests_demo, beautifulsoup_demo
from AIMWebScraping.library_demos.scrapy_demo import ScrapyDemo

@app.route('/')
@app.route('/home')
def home():
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

################ Information ####################
@app.route('/information/definitions')
def information_definitions():
    return render_template(
        'definitions.html',
        title='Definitions',
        year=datetime.now().year
    )

@app.route('/information/legality')
def information_legality():
    return render_template(
        'legality.html',
        title='Legality',
        year=datetime.now().year
    )

@app.route('/information/robots')
def information_robots():
    return render_template(
        'robots.html',
        title='Robots.txt',
        year=datetime.now().year
    )

################## Requests ######################
@app.route('/libraries/requests')
def libraries_requests():
    return render_template(
        'requests.html',
        title='Requests',
        year=datetime.now().year,
        search ="2018",
        message = ""
    )

@app.route('/requests_get_demo')
def requests_get_demo():
    response = requests_demo.get_table_page()
    return json.dumps({'response': response.status_code, 'html': response.text, 'headers': str(response.headers)})

@app.route('/requests_post_demo')
def requests_post_demo():
    args = request.args
    response, session = requests_demo.post_login(args.get('username'), args.get('password'))
    return json.dumps({'response': response.status_code, 'html': response.text, 'cookies': json.dumps(session.cookies.get_dict()), 'headers': str(response.headers)})

@app.route('/requests_download_image_demo')
def requests_download_image_demo():
    image_url = request.args.get('url')
    filepath = requests_demo.download_image(image_url)
    return json.dumps({'filepath': filepath })


################ BeautifulSoup ####################
@app.route('/libraries/soup')
def libraries_soup():
    return render_template(
        'beautifulsoup.html',
        title='Beautiful Soup',
        year=datetime.now().year,
        search ="2018",
        message = ""
    )

@app.route('/beautifulsoup_navigation_demo')
def beautifulsoup_navigation_demo():
    args = request.args
    return json.dumps({"html": beautifulsoup_demo.navigate(args.get("direction"))})

@app.route('/beautifulsoup_strainer_demo')
def beautifulsoup_strainer_demo():
    args = request.args

    message = beautifulsoup_demo.soup_strainer(args.get("tag"))
    return json.dumps({"html": message})

@app.route('/beautifulsoup_google_demo')
def beautifulsoup_google_demo():
    args = request.args
    return json.dumps({"links": beautifulsoup_demo.google_search(args.get("search"))})

################ Scrapy ####################
@app.route('/libraries/scrapy')
def libraries_scrapy():
    return render_template(
        'scrapy.html',
        title='Scrapy',
        year=datetime.now().year,
        search ="2018",
        message = ""
    )

@app.route('/full_brickset')
def full_brickset():
    init.LegoPriceScraper().begin_scraping()
    return jsonify("done")


@app.route('/scrapy_demo')
def scrapy_demo():
    ScrapyDemo().begin_scraping()
    return_message = ""
    json_dir_name = "AimWebScraping/data/tabledata"

    json_pattern = os.path.join(json_dir_name,'*.json')
    file_list = glob(json_pattern)
    
    for file in file_list:
        with open(file) as json_file:
            line = json_file.readline()
            while line:
                return_message += line
                line = json_file.readline()

    return json.dumps({"json": return_message})
