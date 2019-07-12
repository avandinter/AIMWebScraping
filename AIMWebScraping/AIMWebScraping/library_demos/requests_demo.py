import requests
import shutil
import uuid

def get_table_page():
    return requests.get("http://testing-ground.scraping.pro/table")

def post_login(username, password):
    session = requests.Session()
    response = session.post('http://testing-ground.scraping.pro/login?mode=login',data={'usr':username,'pwd':password}, headers={'Connection':'close'})
    return response, session

def download_image(url):
    print(url)
    response = requests.get(url, stream=True)
    
    print(response.headers['content-type'])
    image_name = str(uuid.uuid4()) + "." + response.headers['content-type'].split('/')[1]
    if response.status_code == 200:
        with open("AIMWebScraping/static/images/" + image_name, 'wb') as f:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, f)  
    del response
    return image_name