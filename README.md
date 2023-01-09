# Django Project Instructions

## Project Stack

|    Name    | Version |
|:----------:|:------:|
|   Python   |  3.11  |
|   Django   |   4.1  |
|    Git     |  2.37  |
| PostgreSQL |  14.5  |
|            |        |
|            |        |
|            |        |

---

## Development Environment Configuration

### 1. Clone the Project

Clone the repository first.

* **Via SSH:**

```sh
git clone
```

* **Via HTTP:**

```sh
git clone 
```

### 2. Python Environment Setup

**Install**, **create**, and **activate** the virtual environment, then **install dependencies** inside it.

* **Install the Virtualenv Package:**

```sh
pip install virtualenv --upgrade
```

* **Create the Virtual Environment:**

```sh
virtualenv .env
```

* **Activate the Virtualenv:**

In **linux:**

```sh
source .env/bin/activate
```

In **windows:**

```sh
.env\Scripts\activate
```

* #### Install All Dependencies:

```sh
pip install -r requirements.txt
```

**TIP:** To save all dependency versions after each installation, do as follows:

```sh
pip freeze > requirements.in
pip-compile requirements.in
```

### 3. Prepare Settings

* **Secret Key Configuration:**

Add a secret key to the `settings.ini` file as follows:

```py
import secrets

secrets.token_urlsafe(50)
```

**TIP:** Copy generated secret key to the `settings.ini` >> `SECRET_KEY`.

```ini
SECRET_KEY = <your_strong_password>
```

* **Database Configuration:**

Now you need to config your database configuration. The database of the current project is `PostgreSQL`.

Open `psql` and fulfill the requirements by pressing enter one by one, then do as follows:

1. Create Database on your `PostgreSQL` DBMS:

```sql
CREATE
DATABASE <db_name>;
```

2. Create user and grant rules:

```sql
CREATE
USER <db_user> WITH PASSWORD '<your_strong_password>';
ALTER
ROLE <db_user> SET client_encoding TO 'utf8';
ALTER
ROLE <db_user> SET default_transaction_isolation TO 'read committed';
ALTER
ROLE <db_user> SET timezone TO 'UTC';
```

3. Grant user to create the database (for Django tests database):

```sql
ALTER
USER <db_user> CREATEDB;
```

4. At last, grant all privileges to the user:

```sql
GRANT
ALL
PRIVILEGES
ON
DATABASE
<db_name> TO <db_user>;
```

5. Press `\q` and enter to quit.

6. Now consider the following `settings.ini` and fulfill it
   according to what you entered for your DB configuration above:

```ini
# Your database name that is created on ``PostgreSQL``.
DB_NAME =

# Enter your database user and it must have access to the created db.
DB_USER =

# Enter your specified user's database password.
DB_PASSWORD =

# Accessible port of the installed database (default is ``5432``).
DB_PORT =

# The local Database is localhost if you are using docker must enter ``docker-service-name``.
DB_HOST =

# Select a test database name for the created user.
DB_TEST =
```

### 4. Prepare Development Environment

* **Run Unit Tests:**

Before running the project, you should run tests to verify whether it is working correctly.
To run the tests, `cd` into the directory where the `manage.py` is located:

```sh
python manage.py test
```

* **Apply Migrations:**

```sh
python manage.py makemigrations
python manage.py migrate
```

* **Run Project:**

Now, You can run the development server:

```sh
python manage.py runserver
```

Finally navigate to http://localhost:8000