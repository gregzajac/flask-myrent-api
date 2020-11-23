from myrent_app import create_app

app = create_app('production')

@app.route('/')
def index():
    return 'flask-myrent-api, prefiks=/api/v1, author: Grzegorz Zając'

if __name__ == "__main__":
    app.run()
