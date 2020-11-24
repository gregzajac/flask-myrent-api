from myrent_app import create_app

app = create_app()

key = app.config['SECRET_KEY']

@app.route('/')
def index():
    return f'flask-myrent-api, prefiks=/api/v1, author: Grzegorz Zając {key}'