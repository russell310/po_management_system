# Purchase Order Management System

A Django-based backend for managing purchase orders, inventory stock, and supplier interactions. Features include order approval, receiving items, inventory transaction logging, and access control via user roles (e.g., Manager).

---

## Features

- Create, approve, and receive purchase orders
- Inventory auto-update with transaction logging
- User permission control (Manager role-based actions)
- DRF API with filtering capabilities
- Time-stamped models with user tracking

---

## Tech Stack

- Python 3.13
- Django 5.x
- Django REST Framework
- PostgreSQL (or any supported DB)
- `django-filter` for filtering

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/po-management.git
cd po-management
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file at the root level and add necessary variables:

```env
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=postgres://user:password@localhost:5432/yourdb
```

### 5. Run Migrations

```bash
python manage.py migrate
```

### 6. Generate seed data

```bash
python manage.py seed_data --suppliers 10 --products 50
```

### 7. Run the Server

```bash
python manage.py runserver
```
---

## Questions?

Open an issue or email [russell310@gmail.com](mailto:russell310@gmail.com).