from myrent_app import create_app

app = create_app()

@app.route('/')
def index():
    return f'flask-myrent-api, prefiks=/api/v1, author: Grzegorz Zając'