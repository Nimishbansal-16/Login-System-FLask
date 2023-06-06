## Setup

Clone this repo, then run the following:

```
virtualenv env
source env/bin/activate
pip install -r requirements.txt
```

Create Database and table using the following command:

```
create database loginsystem
use loginsystem
CREATE TABLE users (id INT AUTO_INCREMENT PRIMARY KEY, phone_number VARCHAR(15), email VARCHAR(255) UNIQUE, password VARCHAR(255));
```

Also update mysql user and password in the main.py file

## Running

```python main.py```

navigate to `localhost:5000/` to try it out!


## Key Features

Used Authy for sending otp to phone number

Used SHA256 hashing to hash the password

Whenever a user tries to log in using email, then if its password matches to that stored in database, then login is successful

Whenever user tries to log in using phone number, if it is an existing user then no new entry is created in the database, otherwise a new user is added into the database
