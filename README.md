# GraphQL Backend Challenge

## Overview

This project is a Django + GraphQL API for managing users and deployed applications, supporting user plans (Hobby/Pro) and Relay-compliant queries.

## Features

- Django 5, ASGI-ready
- GraphQL API with Relay Node interface
- Custom user/app IDs (u_*, app_*)
- DataLoader for N+1 query prevention
- Pytest test suite for models, queries, mutations
- SQLite for development (PostgreSQL/MySQL ready)

## Setup

```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata fixtures/users.json
python manage.py loaddata fixtures/apps.json
python manage.py runserver
```

## Usage

- GraphQL endpoint: http://127.0.0.1:8000/graphql/
- Django admin: http://127.0.0.1:8000/admin/

## Example Queries

### List all users and their apps

```graphql
query {
  allUsers {
    id
    username
    plan
    apps {
      edges {
        node {
          id
          active
        }
      }
    }
  }
}
```

### List all deployed apps and their owners

```graphql
query {
  allApps {
    id
    active
    owner {
      id
      username
    }
  }
}
```

### Upgrade a user account

```graphql
mutation Upgrade($id: ID!) {
  upgradeAccount(userId: $id) {
    ok
    user { id plan }
  }
}
```

### Downgrade a user account

```graphql
mutation Downgrade($id: ID!) {
  downgradeAccount(userId: $id) {
    ok
    user { id plan }
  }
}
```

## Testing

```sh
pytest
```

## Deployment

- Use Uvicorn or Daphne for ASGI
- Configure environment variables as in `.env.example`


