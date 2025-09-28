#!/usr/bin/env python
"""
Script to update the Site domain for production deployment.
Run this after deploying to Heroku to ensure email templates use the correct domain.
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wiesbaden_cyclery.settings')
django.setup()

from django.contrib.sites.models import Site
from django.conf import settings

def update_site_domain():
    """Update the Site domain to the production Heroku domain."""
    production_domain = 'wiesbaden-cyclery-project-818faeff3e83.herokuapp.com'
    
    try:
        # Get or create the site
        site, created = Site.objects.get_or_create(
            pk=settings.SITE_ID,
            defaults={
                'domain': production_domain,
                'name': 'Wiesbaden Cyclery'
            }
        )
        
        if not created:
            # Update existing site
            site.domain = production_domain
            site.name = 'Wiesbaden Cyclery'
            site.save()
            
        print(f'✅ Successfully updated site domain to: {production_domain}')
        print(f'   Site name: {site.name}')
        print(f'   Site ID: {site.id}')
        
        # Verify the change
        current_site = Site.objects.get_current()
        site_url = f"https://{current_site.domain}" if not settings.DEBUG else f"http://{current_site.domain}:8000"
        print(f'   Email site_url will be: {site_url}')
        
        return True
        
    except Exception as e:
        print(f'❌ Error updating site domain: {str(e)}')
        return False

if __name__ == '__main__':
    success = update_site_domain()
    sys.exit(0 if success else 1)