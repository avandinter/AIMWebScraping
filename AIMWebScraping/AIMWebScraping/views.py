"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, request, jsonify
from AIMWebScraping import app
from AIMWebScraping.Demos import webscraping_demo as req

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
        title='Requests Demo',
        year=datetime.now().year,
        search ="Python XKCD",
        message = ""
    )

@app.route('/requests_test')
def requests_test():
    
    name = request.args.get('name')
    print(name)
    demo = req.webscraping_demo()

    return jsonify(demo.requests_google_search(name))

@app.route('/soup_test')
def soup_test():
    
    name = request.args.get('name')
    print(name)
    demo = req.webscraping_demo()

    return jsonify(demo.requests_google_search(name))

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )
