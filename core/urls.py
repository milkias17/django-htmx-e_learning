from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    # path("", views.home, name="index"),
    path("", views.CoursesListView.as_view(), name="index"),
    path("courses/create/", views.CourseCreateView.as_view(), name="course_create"),
    path("courses/<slug:pk>/", views.CourseDetailView.as_view(), name="course_detail"),
    path("cart/", views.CartOperations.as_view(), name="cart"),
    path("user_courses/", views.UserCourseListView.as_view(), name="user_courses"),
    # path("register/", views.register, name="register"),
    # path("creator_login/", views.creator_login, name="creator_login"),
    # path("course/create/", views.CourseCreate.as_view(), name="create_course")
]
