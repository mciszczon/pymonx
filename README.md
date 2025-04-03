# Pymonx

__A simple process-monitoring app built using Django, HTMX, Alpine and DaisyUI__

## Getting Started

### Prerequisites

- Python (refer to `.python-version` file for the version)

### Installation

1. Clone the repository
2. Create a virtual environment using `python -m venv venv` and activate it: `source venv/bin/activate`
3. Install the dependencies using `pip install -r requirements.txt`
4. Run migrations: `python manage.py migrate`
5. Run the server using `python manage.py runserver`
6. Start Tailwind watcher using `python manage.py tailwind start`
7. Open the browser at `http://localhost:8000` to access the app

In order to use the app, you have to create a user and log in:

`python manage.py createsuperuser`

### Project Structure

The project consists of two apps: `landing`, which only hold views for login and logout pages,
and `monitor`.

## TODO:

- E2E tests using Playwright
- Sorting in Snapshot view
