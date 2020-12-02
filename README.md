# Renting flats REST API

REST API for online renting flats. It supports landlords of flats and flats resources including authentication (JWT). It also provides managing tenants, agreements with connected to them settlements and pictures for flats. Working application can be found [here](https://flask-myrent-api.herokuapp.com/api/v1/).

The documentation can be found in `myrent_app/templates/myrent_api_documentation.html` or [here](https://documenter.getpostman.com/view/13065363/TVewY42z).
The schema of the database can be found [here](https://dbdiagram.io/embed/5f91f7463a78976d7b78d0b1)

## Setup

- Clone repository
- Create database and user
- Create AWS S3 bucket
- Rename .env.example to `.env` and set your values 
```buildoutcfg
# MySQL SQLALCHEMY_DATABASE_URI MySQL template
SQLALCHEMY_DATABASE_URI = mysql+pymysql://<db_user>:<db_password>@<db_host>/<db_name>?charset=utf8mb4
```
- Create a virtual environment
```buildoutcfg
python -m venv venv
```
- Install packages from `requirements.txt`
```buildoutcfg
pip install -r requirements.txt
```
- Migrate database
```buildoutcfg
flask db upgrade
```
- Run command
```buildoutcfg
flask run
```

### NOTE

Import / delete example data from 
`myrent_app/samples`
```buildoutcfg
# import (to database and AWS S3)
flask db-manage add-data

# remove with MySQL database
flask db-manage remove-data-mysql

# remove with PostgreSQL database
flask db-manage remove-data-postgres
```

## Tests

In order to execute tests located in `tests/` run the command:
```buildoutcfg
python -m pytest tests/
```

## Technologies / Tools

- Python 3.7.3
- Flask 1.1.2
- Alembic 1.4.3
- SQL Alchemy 1.3.20
- Pytest 6.1.1
- Marshmallow 3.8.0
- JWT 1.7.1
- Cors 3.0.9
- MySQL (dev) / PostgreSQL (prod)
- Heroku
- Postman
