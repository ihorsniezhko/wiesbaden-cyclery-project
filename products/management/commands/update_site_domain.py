from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings


class Command(BaseCommand):
    help = 'Update the Site domain for email templates and allauth'

    def add_arguments(self, parser):
        parser.add_argument(
            '--domain',
            type=str,
            default='wiesbaden-cyclery-project-818faeff3e83.herokuapp.com',
            help='Domain to set for the site (default: Heroku production domain)'
        )

    def handle(self, *args, **options):
        domain = options['domain']
        
        try:
            # Get or create the site
            site, created = Site.objects.get_or_create(
                pk=settings.SITE_ID,
                defaults={
                    'domain': domain,
                    'name': 'Wiesbaden Cyclery'
                }
            )
            
            if not created:
                # Update existing site
                site.domain = domain
                site.name = 'Wiesbaden Cyclery'
                site.save()
                
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated site domain to: {domain}'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Error updating site domain: {str(e)}'
                )
            )