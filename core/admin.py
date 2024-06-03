from django.contrib import admin

from core.models import Course, CourseCategory

# Register your models here.
admin.site.register([Course, CourseCategory])
