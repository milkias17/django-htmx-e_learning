from django.contrib import admin

from core.models import Course, CourseCategory, CourseLecture, CourseSection

# Register your models here.
admin.site.register([Course, CourseCategory, CourseSection, CourseLecture])
