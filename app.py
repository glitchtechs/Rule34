from flask import Flask, render_template, request, redirect, url_for, send_file
from pyrule34 import AsyncRule34
import asyncio

app = Flask(__name__)

async def fetch_image_urls(search_tag, exclude_tags=None, max_pages=5):
    async with AsyncRule34() as r34:
        image_urls = []
        page_id = 0
        while True:
            search_result = await r34.search(tags=[search_tag], exclude_tags=exclude_tags, page_id=page_id)
            if not search_result:
                break
            image_urls.extend([post.file_url for post in search_result])
            page_id += 1
            if page_id >= max_pages:
                break
        return image_urls

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['GET'])
def download():
    image_url = request.args.get('image_url')
    return send_file(image_url, as_attachment=True)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form['search_query']
        exclude_tags = []  
        max_pages = 50000  
    
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        image_urls = loop.run_until_complete(fetch_image_urls(search_query, exclude_tags=exclude_tags, max_pages=max_pages))

        return render_template('search.html', 
                               search_query=search_query, 
                               image_urls=image_urls)

    elif request.method == 'GET':
        search_query = request.args.get('search_query')  
        if not search_query:
            return render_template('error.html', message='No search query provided')
    
        exclude_tags = []  
        max_pages = 50000  
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        image_urls = loop.run_until_complete(fetch_image_urls(search_query, exclude_tags=exclude_tags, max_pages=max_pages))

        return render_template('search.html', 
                               search_query=search_query, 
                               image_urls=image_urls)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="5501")
