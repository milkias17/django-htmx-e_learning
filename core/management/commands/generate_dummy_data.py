import random

from django.db import transaction
from django.core.management.base import BaseCommand

from core.factories import CourseFactory, UserFactory

NUM_USERS = 50
NUM_COURSES = 10
NUM_THREADS = 12
COMMENTS_PER_THREAD = 25
USERS_PER_CLUB = 8

class Command(BaseCommand):
    help = "Generates test data"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        # self.stdout.write("Deleting old data...")
        # models = [User, Thread, Comment, Club]
        # for m in models:
        #     m.objects.all().delete()

        self.stdout.write("Creating new data...")
        # Create all the users
        for _ in range(NUM_COURSES):
            course = CourseFactory()
