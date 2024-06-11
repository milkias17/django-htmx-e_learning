from django.contrib.auth.models import User
import factory
from factory.django import DjangoModelFactory

from core.models import Course, CourseCategory


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker("sentence", nb_words=2)
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")
    password = factory.django.Password("admin")


class CourseCategoryFactory(DjangoModelFactory):
    class Meta:
        model = CourseCategory

    name = factory.Faker("sentence", nb_words=20, variable_nb_words=True)


class CourseFactory(DjangoModelFactory):
    class Meta:
        model = Course

    user = factory.Iterator(User.objects.all())
    title = factory.Faker("sentence", nb_words=5, variable_nb_words=True)
    language = factory.Faker("language_name")
    short_description = factory.Faker("sentence", nb_words=20, variable_nb_words=True)
    description = factory.Faker("sentence", nb_words=100, variable_nb_words=True)
    price = factory.Faker("pydecimal", min_value=0.0, max_value=300.0)
    preview = "courses/64b33392-0c20-4e4a-a7aa-73662292058a/preview/Is__Cultural_Fit__Still_Important__ICYgCju.webm"
    thumbnail = factory.django.ImageField(color="red")
    category = factory.Iterator(CourseCategory.objects.all())
