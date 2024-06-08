from django.db.models import F, Sum
from django.http import HttpRequest
from django.conf import settings

from core.models import Course


class Cart:
    def __init__(self, request: HttpRequest) -> None:
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = []

        if not isinstance(cart, list):
            raise ValueError(
                f"{settings.CART_SESSION_ID} should be a list not {type(cart)}"
            )

        if len(cart) > 0:
            valid_courses = Course.objects.filter(id__in=cart).values_list(
                "id", flat=True
            )
            valid_courses = [str(uuid) for uuid in valid_courses]
            prev_cart = cart.copy()
            #
            cart = [course for course in prev_cart if course in valid_courses]
            cart = self.session[settings.CART_SESSION_ID]
            if cart != prev_cart:
                self.session.modified = True

        self.cart = cart

    def add(self, course_id: str):
        course = Course.objects.get(id=course_id)
        if str(course.id) not in self.cart:
            self.cart.append(str(course.id))

        self.save()

    def remove(self, course_id: str):
        if course_id in self.cart:
            self.cart.remove(course_id)
        self.save()

    def clear(self):
        self.cart.clear()
        self.save()

    def save(self):
        self.session.modified = True

    @property
    def total_price(self):
        course_price = Course.objects.filter(id__in=self.cart).aggregate(total=Sum(F("price")))
        return course_price["total"] or 0

    def __contains__(self, course: Course | str):
        if not isinstance(course, str):
            course = str(course.id)

        return course in self.cart

    def __iter__(self):
        courses = Course.objects.filter(id__in=self.cart)
        for course in courses:
            yield course

    def __len__(self):
        return len(self.cart)
