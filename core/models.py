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
from django.urls import reverse_lazy
from core.transactions import chapa


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
    price = models.DecimalField(decimal_places=2, max_digits=5)
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
    enrolled_users = models.ManyToManyField(to=User, related_name="enrolled_courses")

    @property
    def creator_detail_url(self):
        return reverse_lazy("core:creator_detail_url", kwargs={"pk": self.id})

    @property
    def average_rating(self):
        average = self.courserating_set.aggregate(avg_val=Avg("rating"))["avg_val"]
        if not average:
            return 0.0

        return round(average, 2)

    @property
    def checked_star(self):
        return (round(self.average_rating * 2) / 2) * 2


class CourseRequirement(BaseModel):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="requirements"
    )
    description = models.TextField(verbose_name="Requirement")

    def __str__(self):
        return self.description


class CourseAudience(BaseModel):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="audience"
    )
    description = models.TextField(verbose_name="Who is this course for?")

    def __str__(self):
        return self.description


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


class TransactionStatus(models.TextChoices):
    CREATED = "Created", "CREATED"
    PENDING = "Pending", "PENDING"
    SUCCESS = "Success", "SUCCESS"
    FAILED = "Failed", "FAILED"


class Transaction(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="transactions"
    )
    courses = models.ManyToManyField(Course)
    amount = models.FloatField()
    currency = models.CharField(max_length=25, default="ETB")

    payment_title = models.CharField(max_length=255, default="Payment")
    description = models.TextField(null=True, blank=True)

    status = models.CharField(
        max_length=50, choices=TransactionStatus, default=TransactionStatus.CREATED
    )

    response_dump = models.JSONField(
        default=dict, blank=True
    )  # incase the response is valuable in the future
    checkout_url = models.URLField(null=True, blank=True)

    @staticmethod
    def initialize(user: User, amount: float, courses: list[Course]):
        transaction = Transaction(user=user, amount=amount)
        transaction.save()
        for course in courses:
            transaction.courses.add(course)
        transaction.save()
        response = chapa.initialize(
            email=user.email,
            amount=amount,
            first_name=user.first_name,
            last_name=user.last_name,
            tx_ref=transaction.id,
            customization={"title": "Udemy"},
            return_url="http://localhost:8000" + reverse_lazy("core:index"),
        )
        if response["status"] == "failed":
            transaction.status = TransactionStatus.FAILED
            transaction.save()
            return transaction

        transaction.checkout_url = response["data"]["checkout_url"]
        transaction.save()
        return transaction
