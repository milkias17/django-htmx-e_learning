
from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="index"),
    # path("register/", views.register, name="register"),
    # path("creator_login/", views.creator_login, name="creator_login"),
    # path("course/create/", views.CourseCreate.as_view(), name="create_course")
]
