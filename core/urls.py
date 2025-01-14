from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="index"),
    path("courses/", views.CoursesListView.as_view(), name="course_list"),
    path("courses/create/", views.CourseCreateView.as_view(), name="course_create"),
    path("courses/<slug:pk>/", views.CourseDetailView.as_view(), name="course_detail"),
    path(
        "course_content/video/<slug:lecture_id>/",
        views.lecture_video_view,
        name="lecture_video",
    ),
    path(
        "course_content/<slug:pk>/",
        views.CourseContentView.as_view(),
        name="course_content",
    ),
    path(
        "lectures/create/",
        views.CourseLectureCreateView.as_view(),
        name="lecture_create",
    ),
    path(
        "lectures/delete/<slug:pk>/",
        views.CourseLectureDeleteView.as_view(),
        name="lecture_delete",
    ),
    path(
        "lecture/<slug:pk>/edit/",
        views.CourseLectureEditView.as_view(),
        name="lecture_edit",
    ),
    path(
        "creator_coures/<slug:pk>/",
        views.CreatorCourseDetailView.as_view(),
        name="creator_course_detail",
    ),
    path(
        "section/<slug:pk>/delete",
        views.CourseSectionDeleteView.as_view(),
        name="section_delete",
    ),
    path("cart/", views.CartOperations.as_view(), name="cart"),
    path("user_courses/", views.UserCourseListView.as_view(), name="user_courses"),
    path("created_courses/", views.CreatedCoursesListView.as_view(), name="my_courses"),
    path("test/", views.handle_successful_payment, name="transaction_success"),
]
