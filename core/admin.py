from django.contrib import admin

# Register your models here.
class Student(models.Model):
    name = models.CharField(max_length=100)
    student_id = models.IntegerField(unique=True)
    date_of_birth = models.DateField()

    def __str__(self):
        return self.name

class Course(models.Model):
    title = models.CharField(max_length=200)
    course_id = models.CharField(max_length=10, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title
