from django.core.management.base import BaseCommand
from django.db import connection
from auth_freedom.models import User, CandidateProfile
from django.db.models.signals import post_save
from auth_freedom.models import create_user_profile, save_user_profile

class Command(BaseCommand):
    help = 'Reset database and sequences for testing'

    def handle(self, *args, **kwargs):
        # Disconnect signals temporarily
        post_save.disconnect(create_user_profile, sender=User)
        post_save.disconnect(save_user_profile, sender=User)

        # Delete all records
        CandidateProfile.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()  # Don't delete superuser

        # Reset sequences
        with connection.cursor() as cursor:
            cursor.execute("ALTER SEQUENCE auth_freedom_candidateprofile_id_seq RESTART WITH 1")
            cursor.execute("ALTER SEQUENCE auth_freedom_user_id_seq RESTART WITH 1")
        
        self.stdout.write(self.style.SUCCESS('Successfully reset database and sequences')) 