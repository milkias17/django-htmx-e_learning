from django.core.validators import (
    FileExtensionValidator,
    MaxValueValidator,
    MinValueValidator,
    validate_image_file_extension,
)
from django.db import models
import uuid
from django.contrib.auth.models import User
from django.db.models import Avg


# Create your models here.
class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CourseCategory(BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


def get_course_preview_file_path(instance, filename):
    return f"courses/{instance.id}/preview/{filename}"


def get_course_thumbnail_file_path(instance, filename):
    return f"courses/{instance.id}/thumbnail/{filename}"


class Course(BaseModel):
    title = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    short_description = models.CharField(max_length=100)
    description = models.TextField()
    language = models.CharField(max_length=100)
    price = models.FloatField()
    preview = models.FileField(
        upload_to=get_course_preview_file_path,
        validators=[FileExtensionValidator(allowed_extensions=["mp4", "mkv", "webm"])],
    )
    thumbnail = models.ImageField(
        upload_to=get_course_thumbnail_file_path,
        validators=[validate_image_file_extension],
        null=True,
    )
    category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE)

    @property
    def average_rating(self):
        return (
            round(self.courserating_set.aggregate(avg_val=Avg("rating"))["avg_val"], 2)
            or 0
        )


class CourseRequirement(BaseModel):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="requirements"
    )
    description = models.TextField()


class CourseAudience(BaseModel):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="audience"
    )
    description = models.TextField()


class CourseSection(BaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    order = models.IntegerField(default=0)


def get_course_lecture_file_path(instance, filename):
    return f"courses/{instance.section.course.id}/sections/{instance.section.id}/lectures/{filename}"


class CourseLecture(BaseModel):
    section = models.ForeignKey(CourseSection, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    order = models.IntegerField(default=0)
    content = models.FileField(upload_to=get_course_lecture_file_path)
    previewable = models.BooleanField(default=False)

    @property
    def content_type(self):
        return self.content.content_type


class CourseRating(BaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    review = models.TextField()
