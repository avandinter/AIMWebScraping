"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, request, jsonify
from AIMWebScraping import app
from AIMWebScraping.Demos import webscraping_demo as demo, brickset_full as brickset

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
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
    scrapy = brickset.brickset_full()
    scrapy.begin_scraping()
    return jsonify("done")

@app.route('/about')
def about():
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )
