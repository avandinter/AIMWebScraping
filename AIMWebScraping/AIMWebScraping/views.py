from datetime import datetime
from flask import render_template, request, jsonify
from AIMWebScraping import app
from AIMWebScraping.Demos import webscraping_demo as demo
from AIMWebScraping.lego_price_scraper import init

@app.route('/')
@app.route('/home')
def home():
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

@app.route('/requests_demo')
def requests_demo():
    return render_template(
        'requests.html',
        title='Demo',
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

@app.route('/requests_test')
def requests_test():
    year = request.args.get('year')
    scraper = demo.webscraping_demo(year)

    return jsonify(scraper.requests_brickset())

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
