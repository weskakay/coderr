# Coderr API

REST backend for Coderr, a freelancer marketplace. Built with Django and
Django REST Framework.

Business users publish offers with three packages each (basic, standard,
premium). Customers order a package and review the business afterwards.

The frontend is not part of this repository. Tested with frontend version
1.2.1.

## Requirements

- Python 3.12+
- pip

## Setup

**1. Clone the repository**

```bash
git clone https://github.com/weskakay/coderr.git
```

**2. Enter the project folder**

```bash
cd coderr
```

**3. Create a virtual environment**

macOS and Linux:

```bash
python3 -m venv .venv
```

Windows:

```bash
python -m venv .venv
```

**4. Activate it**

macOS and Linux:

```bash
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

**5. Install the dependencies**

```bash
pip install -r requirements.txt
```

**6. Create the database**

```bash
python manage.py migrate
```

**7. Create the guest accounts**

```bash
python manage.py seed_guests
```

**8. Start the server**

```bash
python manage.py runserver
```

The API runs at `http://127.0.0.1:8000/api/`.

## Guest accounts

The frontend offers two guest logins. `seed_guests` creates both. Running it
again resets their passwords and account types, it never creates
duplicates.

| Type | Username | Password |
|---|---|---|
| customer | `andrey` | `asdasd` |
| business | `kevin` | `asdasd24` |

## Authentication

Every endpoint needs a token unless noted otherwise:

```
Authorization: Token <token>
```

## Endpoints

| Method | URL | Access |
|---|---|---|
| POST | `/api/registration/` | public |
| POST | `/api/login/` | public |
| GET | `/api/profile/{user_id}/` | logged in |
| PATCH | `/api/profile/{user_id}/` | own profile only |
| GET | `/api/profiles/business/` | logged in |
| GET | `/api/profiles/customer/` | logged in |

Login uses the username, not the email address.

Profile pictures are sent as `multipart/form-data` in the `file` field and
returned as an absolute URL, or `null` when there is none. Empty text fields
of a profile are returned as `""`, never as `null`.

## Design decisions

- **No password rules on registration.** The API only checks that both
  passwords match and that username and email are still free. The guest
  account `andrey` uses the password `asdasd`, which Django's password
  validators would reject. `createsuperuser` and the admin still apply them.

## Project layout

```
core/            project settings and root urls
auth_app/        registration and login
profile_app/     profiles for customers and business users
offers_app/      offers and their packages
orders_app/      orders placed on a package
reviews_app/     reviews of business users
base_info_app/   public platform statistics
```

Each app keeps its API code in an `api/` folder and its tests in a `tests/`
folder.

## Admin

```bash
python manage.py createsuperuser
```

The admin runs at `http://127.0.0.1:8000/admin/`.

## Configuration

`SECRET_KEY` and `DEBUG` are read from the environment and fall back to
development defaults, so the setup above works without any configuration.

`.env.example` lists the variables. Copy it and fill in your own values:

```bash
cp .env.example .env
```

The project does not load that file on its own. Export the values before
starting the server:

```bash
set -a; source .env; set +a
```

Uploaded images are stored in `media/` and served by the development server
while `DEBUG` is on.

Cross origin requests are allowed from `127.0.0.1` and `localhost` on ports
5500 and 5501, which is where the frontend is usually served.

## Development

Install the development dependencies:

```bash
pip install -r requirements-dev.txt
```

Run the tests:

```bash
coverage run manage.py test
```

Show the coverage report:

```bash
coverage report
```

Check the code style:

```bash
flake8
```
