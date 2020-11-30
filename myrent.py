from myrent_app import create_app


app = create_app()
ver = app.config['VERSION']

@app.route('/')
def index():
    return f'''<p>flask-myrent-api,<br> 
            prefiks=/api/{ver},<br> 
            author: Grzegorz Zając,<br>
            testing page for uploading pictures: api/v1/file</p>'''
