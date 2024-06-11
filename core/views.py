from django.conf import settings
from django.core.files.storage import FileSystemStorage
import os
from django.forms import modelformset_factory
from django.http import HttpRequest, HttpResponse, QueryDict
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView, ListView, View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django_htmx.http import reswap, retarget, trigger_client_event
import django_filters
from django_filters.views import FilterView
import time
from formtools.wizard.views import SessionWizardView

from core.cart import Cart
from core.forms import CourseAudienceForm, CourseForm, CourseRequirementForm
from core.models import Course, CourseAudience, CourseRequirement
from core.utils import inject_messages, render_html_block
from udemy.auth_utils import GroupRequiredMixin


def home(request):
    return render(request, "home.html")


class CourseFilter(django_filters.FilterSet):
    class Meta:
        model = Course
        fields = ["title", "category"]


class CoursesListView(FilterView):
    model = Course
    template_name = "home.html"
    context_object_name = "courses"
    filterset_class = CourseFilter
    queryset = Course.objects.order_by("-updated_at")

    def render_to_response(self, context, **response_kwargs):
        if self.request.htmx and not self.request.htmx.boosted:
            time.sleep(1)
            return render_html_block(
                self.template_name, "course_list", context, self.request
            )
        return super().render_to_response(context, **response_kwargs)


class UserCourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = "core/user_course_list.html"
    context_object_name = "courses"

    def get_queryset(self):
        return self.request.user.enrolled_courses.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class CourseCreateView(LoginRequiredMixin, SessionWizardView):
    form_list = [
        CourseForm,
        modelformset_factory(CourseRequirement, form=CourseRequirementForm, extra=5),
        modelformset_factory(CourseAudience, form=CourseAudienceForm, extra=5),
    ]
    file_storage = FileSystemStorage(
        location=os.path.join(settings.MEDIA_ROOT, "tmp/courses")
    )

    template_name = "core/wizard_form.html"

    def done(self, form_list, form_dict, **kwargs):
        course_form = form_dict["0"]
        course = course_form.save(commit=False)
        course.user = self.request.user
        course.save()

        course_requirements = form_dict["1"].save(commit=False)
        for course_requirement in course_requirements:
            course_requirement.course = course
            course_requirement.save()

        course_audiences = form_dict["2"].save(commit=False)
        for course_audience in course_audiences:
            course_audience.course = course
            course_audience.save()
        return redirect(self.request.META.get("HTTP_REFERER"))


class CreatedCoursesListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = "core/my_courses.html"
    context_object_name = "courses"
    queryset = Course.objects.order_by("-updated_at")

    def get_queryset(self):
        courses = super().get_queryset()
        return courses.filter(user=self.request.user)


@method_decorator(inject_messages, name="post")
class CourseDetailView(LoginRequiredMixin, DetailView):
    model = Course

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        average_rating = course.average_rating
        context["checked_star"] = (round(average_rating * 2) / 2) * 2
        context["num_stars"] = average_rating
        cart = Cart(self.request)
        context["in_cart"] = course in cart
        return context

    def post(self, request, *args, **kwargs):
        user = self.request.user
        self.object = course = self.get_object()
        if course.user == user:
            messages.error(request, "You can't buy your own course")
            response = HttpResponse(status=200)
            reswap(response, "none")
            return response

        user.enrolled_courses.add(course)
        user.save()
        cart = Cart(self.request)
        cart.remove(str(course.id))
        context = self.get_context_data()
        return render_html_block(
            "core/course_detail.html",
            "course_actions",
            context=context,
            request=self.request,
        )


@method_decorator(inject_messages, name="post")
@method_decorator(inject_messages, name="delete")
class CartOperations(View):
    def get(self, request, *args, **kwargs):
        cart = Cart(request)
        if request.htmx and not request.htmx.boosted:
            return render(request, "partials/nav-cart-dropdown.html", {"cart": cart})
        return render(request, "core/cart.html", context={"cart": cart})

    def post(self, request: HttpRequest, *args, **kwargs):
        operation = self.request.POST.get("operation")
        cart = Cart(request)

        course = get_object_or_404(Course, pk=request.POST.get("course_id"))
        if course.user == request.user:
            messages.error(request, "You can't buy your own course :( ")
            response = HttpResponse(status=200)
            reswap(response, "none")
            return trigger_client_event(response, "refresh_nav_cart")

        match operation:
            case "add":
                cart.add(request.POST.get("course_id"))
                messages.success(request, "Course Added to Cart!")
            case "clear":
                cart.clear()
                messages.success(request, "Cart Cleared!")
            case "checkout":
                user = self.request.user
                user.enrolled_courses.add(*cart.cart)
                user.save()
                cart.clear()
                messages.success(request, "Cart Checkout Successful!")
                return redirect("core:index")

        response = HttpResponse(status=200)
        return trigger_client_event(response, "refresh_nav_cart")

    def delete(self, request, *args, **kwargs):
        data = QueryDict(request.body)
        cart = Cart(request)
        cart.remove(data.get("course_id"))
        response = render_html_block(
            "core/cart.html", "courses", {"cart": cart}, request
        )
        messages.success(request, "Course removed from cart!")
        return trigger_client_event(response, "refresh_nav_cart")
