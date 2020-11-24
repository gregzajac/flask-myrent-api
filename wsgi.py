from myrent_app import create_app

app = create_app('production')
ver = app.config['VERSION']
uri = app.config['SQLALCHEMY_DATABASE_URI']


@app.route('/')
def index():
    return f'flask-myrent-api, prefiks=/api/{ver}, author: Grzegorz Zając, uri: {uri}'

if __name__ == "__main__":
    app.run()
