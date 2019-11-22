# Warbler

Warbler is a Python based Twitter clone built on a RESTful Flask API using SQLAlchemy.

Warbler is [live on Heroku](https://warbler-ja.herokuapp.com/).

## Table of Contents
- [Screenshots](#screenshots)
- [Installation](#installation)
- [Features](#features)
- [Technologies](#technologies)
- [Features to add](#features-to-add)

## Screenshots

![Alt text](/static/images/warbler1.png?raw=true "Home")
![Alt text](/static/images/warbler2.png?raw=true "Profile")
![Alt text](/static/images/warbler3.png?raw=true "DM")
![Alt text](/static/images/warbler4.png?raw=true "Conversations")

## Installation
### Creating the Python virtual environment:  

```shell
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Setting up the database:

```shell
createdb warbler
python seed.py
```

### Starting the server:

```shell
flask run
```

### Clone

- Clone this repo to your local machine using `https://github.com/jyahn/warbler`

---

## Features

- Direct messaging
- Posting messages
- Liking messages
- Following users
- User authentication / authorization


---

## Technologies

- Flask
- Jinja
- SQLAlchemy
- WTForm
- Bcrypt

--- 

## Features to add

- Users should be able to see their own tweets from the homepage.
