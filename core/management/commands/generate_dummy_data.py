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
        parser.add_argument("--num_courses", type=int)
        parser.add_argument("--num_users", type=int)
        parser.add_argument("-users", action="store_true")

    @transaction.atomic
    def handle(self, *args, **kwargs):
        # self.stdout.write("Deleting old data...")
        # models = [User, Thread, Comment, Club]
        # for m in models:
        #     m.objects.all().delete()

        if "users" in args:
            num_users = kwargs.get("num_users") or NUM_USERS
            self.stdout.write("Creating " + str(num_users) + ".....")
            UserFactory.create_batch(num_users)
            self.stdout.write("Created" + str(num_users)  + "!!!")
        else:
            num_courses = kwargs.get("num_courses") or NUM_COURSES
            self.stdout.write("Creating " + str(num_courses) + " courses ....")
            # Create all the users
            CourseFactory.create_batch(num_courses)
