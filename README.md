# Coderr API

REST backend for Coderr, a freelancer marketplace. Built with Django and
Django REST Framework.

Business users publish offers with three packages each (basic, standard,
premium). Customers order a package and review the business afterwards.

The frontend is not part of this repository, see [Frontend](#frontend).

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

## Frontend

Tested with frontend version 1.2.1.

The frontend works without any change to its `config.js`, the defaults
already match this API:

| Setting | Value |
|---|---|
| `API_BASE_URL` | `http://127.0.0.1:8000/api/` |
| `STATIC_BASE_URL` | `http://127.0.0.1:8000/` |
| `PAGE_SIZE` | `6` |
| `GUEST_LOGINS` | `andrey` and `kevin`, as created by `seed_guests` |

Keep the API running and serve the frontend on port 5500 or 5501, for
example with the Live Server extension of VS Code. Other ports are blocked
by CORS, see [Configuration](#configuration).

## Authentication

Registration and login return a token. Every endpoint needs it unless noted
otherwise:

```
Authorization: Token <token>
```

## Endpoints

Login uses the username, not the email address. Methods that are not listed
return 405.

### Auth

| Method | Path | Who | Codes |
|---|---|---|---|
| POST | `/api/registration/` | anyone | 201, 400 |
| POST | `/api/login/` | anyone | 200, 400 |

Registration takes `username`, `email`, `password`, `repeated_password` and
`type` (`customer` or `business`) and creates the profile along with the
account.

### Profiles

| Method | Path | Who | Codes |
|---|---|---|---|
| GET | `/api/profile/{user_id}/` | any user | 200, 401, 404 |
| PATCH | `/api/profile/{user_id}/` | owner only | 200, 400, 401, 403, 404 |
| GET | `/api/profiles/business/` | any user | 200, 401 |
| GET | `/api/profiles/customer/` | any user | 200, 401 |

`{user_id}` is the id of the user, not of the profile. Profile pictures are
sent as `multipart/form-data` in the `file` field and returned as an absolute
URL, or `null` when there is none. Empty text fields of a profile are
returned as `""`, never as `null`.

### Offers

| Method | Path | Who | Codes |
|---|---|---|---|
| GET | `/api/offers/` | anyone | 200, 400 |
| POST | `/api/offers/` | business users | 201, 400, 401, 403 |
| GET | `/api/offers/{id}/` | any user | 200, 401, 404 |
| PATCH | `/api/offers/{id}/` | creator only | 200, 400, 401, 403, 404 |
| DELETE | `/api/offers/{id}/` | creator only | 204, 401, 403, 404 |
| GET | `/api/offerdetails/{id}/` | any user | 200, 401, 404 |

Every offer has exactly three packages: `basic`, `standard` and `premium`.
A PATCH finds packages by `offer_type` and updates them in place, so their
ids never change. `revisions: -1` means unlimited revisions. Prices are
returned as numbers.

The offer list is the only paginated endpoint, with 6 offers per page by
default. It accepts these query parameters:

| Parameter | Effect |
|---|---|
| `creator_id` | offers of this user only |
| `min_price` | cheapest package costs at least this much |
| `max_delivery_time` | fastest package takes at most this many days |
| `search` | searches title and description |
| `ordering` | `updated_at` or `min_price`, prefix `-` for descending |
| `page`, `page_size` | page number and offers per page (max 100) |

Empty parameters are ignored. Invalid numbers or an unknown ordering field
return 400, a page past the end returns 404.

### Orders

| Method | Path | Who | Codes |
|---|---|---|---|
| GET | `/api/orders/` | any user, own orders only | 200, 401 |
| POST | `/api/orders/` | customer users | 201, 400, 401, 403, 404 |
| PATCH | `/api/orders/{id}/` | business user of the order | 200, 400, 401, 403, 404 |
| DELETE | `/api/orders/{id}/` | staff only | 204, 401, 403, 404 |
| GET | `/api/order-count/{business_user_id}/` | any user | 200, 401, 404 |
| GET | `/api/completed-order-count/{business_user_id}/` | any user | 200, 401, 404 |

An order is created from one package with `{"offer_detail_id": 1}`. Title,
price, delivery time, revisions and features are copied from the package,
so later changes to the offer do not touch existing orders. A PATCH accepts
`status` only (`in_progress`, `completed`, `cancelled`). There is no
`GET /api/orders/{id}/`. Deleting an order needs a staff account, see
[Admin](#admin). The counters answer 404 for an id without a business
profile.

### Reviews

| Method | Path | Who | Codes |
|---|---|---|---|
| GET | `/api/reviews/` | any user | 200, 400, 401 |
| POST | `/api/reviews/` | customer users, once per business | 201, 400, 401, 403 |
| PATCH | `/api/reviews/{id}/` | author only | 200, 400, 401, 403, 404 |
| DELETE | `/api/reviews/{id}/` | author only | 204, 401, 403, 404 |

The review list accepts `business_user_id`, `reviewer_id` and `ordering`
(`updated_at` or `rating`, prefix `-` for descending). Newest reviews come
first. A PATCH accepts `rating` (1 to 5) and `description`. There is no
`GET /api/reviews/{id}/`.

### Base info

| Method | Path | Who | Codes |
|---|---|---|---|
| GET | `/api/base-info/` | anyone | 200 |

Returns the number of reviews, the average rating rounded half up to one
decimal (`0` without reviews), the number of business profiles and the
number of offers.

## Design decisions

- **No password rules on registration.** The API only checks that both
  passwords match and that username and email are still free. The guest
  account `andrey` uses the password `asdasd`, which Django's password
  validators would reject. `createsuperuser` and the admin still apply them.
- **Users with orders cannot be deleted.** Both users of an order are
  protected, so neither the customer nor the business user loses their order
  history. Delete the orders first, for example in the admin.
- **A second review returns 403.** A customer may review each business user
  once. The API specification lists both 400 and 403 for this case; the API
  answers 403, because the request is well formed but not allowed. Invalid
  data, such as a rating outside 1 to 5, returns 400.
- **Read-only fields in a PATCH.** Order and review updates reject any field
  besides the ones they may change with 400, because the specification names
  exactly those fields. Profile and offer updates ignore read-only fields such
  as `type` or `user`, the default of Django REST Framework, because the
  frontend sends the whole form there. A review PATCH without `rating` or
  `description` returns 400.
- **An invalid token counts as no token.** The frontend sends its stored
  token with every request. After a database reset that token is stale, and
  Django REST Framework would answer 401 even on the public offer list and
  base info, where the specification lists no 401. The API therefore treats
  an invalid token like a missing one: public endpoints work, protected ones
  still return 401.

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

Create a staff account:

```bash
python manage.py createsuperuser
```

The admin runs at `http://127.0.0.1:8000/admin/`. Log in there to see and
edit all users, profiles, offers, orders and reviews. A user added in the
admin gets the profile type chosen on the same page. The packages of an offer
can be edited there but not removed, every offer keeps all three. The same
account may delete orders through the API.

## Configuration

`SECRET_KEY` and `DEBUG` are read from environment variables and fall back
to development defaults, so the setup above works without any configuration.
`.env.example` lists both variables.

To set your own secret key, export it before starting the server.

macOS and Linux:

```bash
export DJANGO_SECRET_KEY="your-secret-key"
```

Windows (PowerShell):

```powershell
$env:DJANGO_SECRET_KEY="your-secret-key"
```

`DJANGO_DEBUG` works the same way and defaults to `True`. Keep it on for
local development: uploaded images in `media/` are only served while `DEBUG`
is on.

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
