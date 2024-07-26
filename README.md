# Django + HTMX

A very basic e-learning platform built with Django and HTMX.

## Features

- Login/Signup
- Courses
- SPA like navigation
- Lazy-loading
- Dynamic state transformations

# Tech Stack

- Django
- HTMX
- Tailwind CSS
- DaisyUI

# Installation

1. Clone the repository
1. Create a virtual environment
1. Install dependencies
1. Run the tailwindcss compiler
1. Run the server

```bash
git clone https://github.com/milkias17/django-htmx-e_learning.git
cd django-htmx-e_learning
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
npm run dev
python manage.py runserver
```

Tip: Use `python manage.py generate_dummy_data --num_courses=<number of courses>` to generate dummy data.
