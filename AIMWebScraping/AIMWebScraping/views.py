from datetime import datetime
from flask import render_template, request, jsonify
import json
from AIMWebScraping import app
from AIMWebScraping.Demos import webscraping_demo as demo
from AIMWebScraping.lego_price_scraper import init
from AIMWebScraping.library_demos import requests_demo

@app.route('/')
@app.route('/home')
def home():
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

@app.route('/libraries/requests')
def libraries_requests():
    return render_template(
        'requests.html',
        title='Requests',
        year=datetime.now().year,
        search ="2018",
        message = ""
    )

@app.route('/libraries/soup')
def libraries_soup():
    return render_template(
        'beautifulsoup.html',
        title='Beautiful Soup',
        year=datetime.now().year,
        search ="2018",
        message = ""
    )

@app.route('/libraries/scrapy')
def libraries_scrapy():
    return render_template(
        'scrapy.html',
        title='Scrapy',
        year=datetime.now().year,
        search ="2018",
        message = ""
    )

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

#@app.route('/requests_test')
#def requests_test():
#    year = request.args.get('year')
#    scraper = demo.webscraping_demo(year)
#    response = scraper.requests_brickset()
#    return json.dumps({'response': response.status_code, 'html': response.text})

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

@app.route('/soup_test')
def soup_test():
    year = request.args.get('year')
    scraper = demo.webscraping_demo(year)

    return jsonify(scraper.bs4_brickset())

@app.route('/scan_all_test')
def scan_all_test():
    year = request.args.get('year')
    scraper = demo.webscraping_demo(year)

    return jsonify(scraper.all_pages_brickset())

@app.route('/scrapy_test')
def scrapy_test():
    year = request.args.get('year')
    scrapy = demo.ScrapyExample()
    scrapy.begin_scraping(year)
    return jsonify("done")

@app.route('/full_brickset')
def full_brickset():
    init.LegoPriceScraper().begin_scraping()
    #scrapy = brickset.brickset_full()
    #scrapy.begin_scraping()
    return jsonify("done")

@app.route('/about')
def about():
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )
