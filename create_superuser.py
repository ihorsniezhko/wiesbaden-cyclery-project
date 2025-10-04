#!/usr/bin/env python
"""
Script to create superuser on Heroku
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wiesbaden_cyclery.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Delete existing user if exists
if User.objects.filter(username='administrator').exists():
    User.objects.get(username='administrator').delete()
    print('Existing user deleted')

# Create superuser
User.objects.create_superuser(
    username='administrator',
    email='admin@wiesbaden-cyclery.de',
    password='wiesbaden_cyclery_project'
)

print('Superuser created successfully!')
print('Username: administrator')
print('Email: admin@wiesbaden-cyclery.de')
