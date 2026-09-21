from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from profile_app.models import Profile


def create_user(username, profile_type=Profile.CUSTOMER, **extra):
    """Create a user with a profile of the given type."""
    user = User.objects.create_user(
        username=username,
        email=f'{username}@example.com',
        password='pw12345!',
        **extra,
    )
    Profile.objects.create(user=user, type=profile_type)
    return user


def make_image(name='avatar.png'):
    """Return a tiny PNG ready for a multipart upload."""
    buffer = BytesIO()
    Image.new('RGB', (2, 2)).save(buffer, format='PNG')
    return SimpleUploadedFile(name, buffer.getvalue(), 'image/png')


def make_text_file(name='notes.txt'):
    """Return a plain text file that is not an image."""
    return SimpleUploadedFile(name, b'hello', 'text/plain')
