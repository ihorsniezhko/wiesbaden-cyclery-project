# 🚀 Local Development Setup

## Prerequisites
- Python 3.11+
- Git

## Quick Setup

```bash
# 1. Clone repository
git clone https://github.com/ihorsniezhko/wiesbaden-cyclery-project.git
cd wiesbaden-cyclery-project

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
echo "DEBUG=True
SECRET_KEY=your-secret-key-here" > .env

# 4. Setup database
python manage.py migrate
python manage.py createsuperuser

# 5. Load sample data
python manage.py loaddata products/fixtures/categories.json products/fixtures/sizes.json products/fixtures/products.json

# 6. Run server
python manage.py runserver
```

Visit http://127.0.0.1:8000

## Common Issues

| Issue | Solution |
|-------|----------|
| "No module named 'django'" | `pip install -r requirements.txt` |
| "SECRET_KEY not found" | Create `.env` with SECRET_KEY |
| "No such table" | Run `python manage.py migrate` |
| Port 8000 in use | Use `python manage.py runserver 8001` |

## Useful Commands

```bash
python manage.py test              # Run tests
python manage.py createsuperuser   # Create admin user
python manage.py check             # Check for issues
```
