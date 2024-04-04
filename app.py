from flask import Flask, render_template, request, redirect, url_for
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

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form['search_query']
        exclude_tags = []  
        max_pages = 50000  
    
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        image_urls = loop.run_until_complete(fetch_image_urls(search_query, exclude_tags=exclude_tags, max_pages=max_pages))

        # Calculate pagination
        items_per_page = 24
        total_pages = (len(image_urls) + items_per_page - 1) // items_per_page
        page = request.args.get('page', 1, type=int)
        start_index = (page - 1) * items_per_page
        end_index = min(start_index + items_per_page, len(image_urls))
        paginated_image_urls = image_urls[start_index:end_index]

        # Calculate previous and next page URLs
        prev_page = None
        if page > 1:
            prev_page = f'/search?search_query={search_query}&page={page - 1}'
        next_page = None
        if end_index < len(image_urls):
            next_page = f'/search?search_query={search_query}&page={page + 1}'

        return render_template('search.html', 
                       search_query=search_query, 
                       image_urls=paginated_image_urls, 
                       prev_page=prev_page, 
                       next_page=next_page,
                       total_pages=total_pages,
                       page=page)

    elif request.method == 'GET':
        search_query = request.args.get('search_query')
        page = request.args.get('page', 1, type=int)  # Ensure page parameter is retrieved
        if not search_query:
            return render_template('error.html', message='No search query provided')
    
        exclude_tags = []  
        max_pages = 50000  
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        image_urls = loop.run_until_complete(fetch_image_urls(search_query, exclude_tags=exclude_tags, max_pages=max_pages))

    # Calculate pagination
        items_per_page = 24
        total_pages = (len(image_urls) + items_per_page - 1) // items_per_page
        start_index = (page - 1) * items_per_page
        end_index = min(start_index + items_per_page, len(image_urls))
        paginated_image_urls = image_urls[start_index:end_index]

    # Calculate previous and next page URLs
        prev_page = None
        if page > 1:
            prev_page = url_for('search', search_query=search_query, page=page - 1)  # Use url_for to generate URL
        next_page = None
        if end_index < len(image_urls):
            next_page = url_for('search', search_query=search_query, page=page + 1)  # Use url_for to generate URL

        return render_template('search.html', 
                   search_query=search_query, 
                   image_urls=paginated_image_urls, 
                   prev_page=prev_page, 
                   next_page=next_page,
                   total_pages=total_pages,
                   page=page)






if __name__ == '__main__':
    app.run(debug=True)
