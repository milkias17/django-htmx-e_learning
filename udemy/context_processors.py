from django.http import HttpRequest
from core.cart import Cart
from core.models import CourseCategory

def app_info(request: HttpRequest):
    cart = Cart(request)

    course_categories = CourseCategory.objects.all()
    return {"cart": cart, "course_categories": course_categories}
