# Booking API

A room booking REST API built with FastAPI and PostgreSQL.

The project supports user authentication, room management and booking creation. Rooms can only be managed by admins, while regular users can create and manage their own bookings.

One of the main parts of the project is preventing overlapping bookings for the same room. The check is implemented both in the application logic and at the PostgreSQL level.

## Features

- User registration and login
- JWT authentication
- Password hashing
- User and admin roles
- Room creation and deletion for admins
- Room listing
- Booking creation
- Personal booking list
- Booking deletion
- Protection against overlapping bookings
- PostgreSQL database
- Database migrations with Alembic
- Automated tests with Pytest
- Docker and Docker Compose setup

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic
- PyJWT
- pwdlib / Argon2
- Pytest
- Docker
- Docker Compose

## Project Structure

```text
booking-api/
├── alembic/
│   └── versions/          # Database migrations
├── src/
│   └── app/
│       ├── routers/
│       │   ├── bookings.py
│       │   ├── rooms.py
│       │   └── users.py
│       ├── api.py         # FastAPI application
│       ├── database.py    # Database connection and sessions
│       ├── dependencies.py
│       ├── exceptions.py
│       ├── models.py      # SQLAlchemy models
│       ├── schemas.py     # Pydantic schemas
│       ├── security.py    # Password hashing and JWT
│       └── service.py     # Application logic
├── tests/
│   ├── api/
│   ├── database/
│   ├── integration/
│   ├── security/
│   └── service/
├── .env.example
├── compose.yaml
├── Dockerfile
└── requirements.txt
```

## API Endpoints

### Authentication

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Log in and receive an access token |

### Rooms

| Method | Endpoint | Description | Auth |
| --- | --- | --- | --- |
| `GET` | `/rooms` | List all rooms | No |
| `POST` | `/rooms` | Create a room | Admin |
| `DELETE` | `/rooms/{room_id}` | Delete a room | Admin |

### Bookings

| Method | Endpoint | Description | Auth |
| --- | --- | --- | --- |
| `POST` | `/bookings` | Create a booking | User |
| `GET` | `/bookings/my` | List current user's bookings | User |
| `DELETE` | `/bookings/{booking_id}` | Delete own booking | User |

## Booking Overlap Protection

Two bookings cannot use the same room during overlapping time periods.

The API checks for conflicts before creating a booking:

```text
existing_start < new_end
and
existing_end > new_start
```

PostgreSQL also enforces this rule with an exclusion constraint using a time range and GiST index.

This means conflicting bookings are rejected even if two requests reach the database at nearly the same time.

## Running with Docker

Clone the repository:

```bash
git clone https://github.com/herdlich/booking-api.git
cd booking-api
```

Create the environment file:

```bash
cp .env.example .env
```

Edit `.env` if you want to use different database credentials or a different JWT secret.

Build the containers:

```bash
docker compose build
```

Start PostgreSQL:

```bash
docker compose up -d db
```

Run the database migrations:

```bash
docker compose run --rm api alembic upgrade head
```

Start the API:

```bash
docker compose up -d api
```

The API will be available at:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

## Environment Variables

Example configuration:

```env
DATABASE_URL=postgresql+psycopg://user:password@db:5432/db_name
DATABASE_TEST_URL=postgresql+psycopg://user:password@db:5432/test_db_name
DATABASE_MIGRATION_TEST_URL=postgresql+psycopg://user:password@db:5432/migration_test_db_name

JWT_SECRET_KEY=your_secure_random_secret_hash_here
JWT_ALGORITHM=HS256

POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=db_name
```

A random JWT secret can be generated with:

```bash
openssl rand -hex 32
```

## Authentication

Protected endpoints use Bearer authentication.

After logging in through `/auth/login`, the API returns an access token:

```json
{
  "access_token": "...",
  "token_type": "bearer"
}
```

The token can then be sent in the `Authorization` header:

```text
Authorization: Bearer <token>
```

Tokens expire after two hours.

Swagger UI keeps the authorization token between requests, so the protected endpoints can also be tested directly from `/docs`.

## Admin Role

New accounts are created with the `user` role by default.

Creating and deleting rooms requires the `admin` role.

For local development, a user can be promoted directly in PostgreSQL:

```sql
UPDATE users
SET role = 'admin'
WHERE username = 'your_username';
```

## Running Tests

The test suite covers the API endpoints, service layer, database behavior, authentication and migrations.

Run it with:

```bash
pytest
```

## Current Status

The project is still under development. The main booking flow, authentication, role-based room management, database migrations and tests are already implemented.