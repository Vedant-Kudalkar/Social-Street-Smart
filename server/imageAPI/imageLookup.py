import argparse
import io
import bs4
import requests
from google.cloud import vision
import json
import re

headers = {'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Mobile Safari/537.36'}

# Load data from corpus.json
with open('./corpus.json') as f:
    data = json.load(f)

def annotate(path):
    """Returns web annotations given the path to an image."""
    client = vision.ImageAnnotatorClient()

    if path.startswith('http') or path.startswith('gs:'):
        image = vision.Image()
        image.source.image_uri = path
    else:
        with io.open(path, 'rb') as image_file:
            content = image_file.read()
        image = vision.Image(content=content)

    web_detection = client.web_detection(image=image).web_detection
    return web_detection

def report(annotations):
    """Prints detected features in the provided web annotations."""
    urls = []
    for page in annotations.pages_with_matching_images:
        fact = ""
        # Using raw strings to avoid escape sequence issues
        r = re.search(r"^(?:http://|www\.|https://)([^/]+)", page.url)
        if r:
            r = r.group()
        else:
            r = page.url
        
        for i in data:
            if re.sub(r'.*w\.', '', i['source_url'], 1) == re.sub(r'.*w\.', '', r, 1):
                fact = i['fact']

        try:
            r = requests.get(page.url, headers=headers)
            html = bs4.BeautifulSoup(r.text, features="html.parser")
            title = html.title.text
        except Exception as e:
            print(f"Error fetching page title: {e}")
            title = str(page.url)

        urls.append({"url": page.url, "title": title, "fact": fact})
    
    return urls
