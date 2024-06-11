import random

from django.db import transaction
from django.core.management.base import BaseCommand, CommandParser

from core.factories import CourseFactory, UserFactory

NUM_USERS = 50
NUM_COURSES = 10
NUM_THREADS = 12
COMMENTS_PER_THREAD = 25
USERS_PER_CLUB = 8


class Command(BaseCommand):
    help = "Generates test data"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("num_courses", type=int)

    @transaction.atomic
    def handle(self, *args, **kwargs):
        # self.stdout.write("Deleting old data...")
        # models = [User, Thread, Comment, Club]
        # for m in models:
        #     m.objects.all().delete()

        num_courses = kwargs.get("num_courses") or NUM_COURSES
        self.stdout.write("Creating " + str(num_courses) + "....")
        # Create all the users
        CourseFactory.create_batch(num_courses)
