"""
Custom storage classes for AWS S3 - MEDIA FILES ONLY
Static files are now served locally via Whitenoise
"""
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


# StaticStorage class removed - static files now served locally via Whitenoise


class MediaStorage(S3Boto3Storage):
    """Custom storage for media files ONLY"""
    location = 'media'
    default_acl = None
    file_overwrite = False
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(f"MediaStorage initialized with location: {self.location}")