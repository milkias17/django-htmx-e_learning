import json
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import os
from django.forms import modelformset_factory
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, QueryDict
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django_htmx.http import (
    HttpResponseClientRedirect,
    reswap,
    retarget,
    trigger_client_event,
)
import django_filters
from django_filters.views import FilterView
import time
from formtools.wizard.views import SessionWizardView

from core.cart import Cart
from core.forms import (
    CourseAudienceForm,
    CourseForm,
    CourseLectureForm,
    CourseRequirementForm,
)
from core.models import (
    Course,
    CourseAudience,
    CourseLecture,
    CourseRequirement,
    CourseSection,
    Transaction,
    TransactionStatus,
)
from core.utils import htmx_redirect, inject_messages, render_html_block
from udemy.auth_utils import GroupRequiredMixin


def home(request):
    return render(request, "home.html")


class CourseFilter(django_filters.FilterSet):
    class Meta:
        model = Course
        fields = ["title", "category"]


class CoursesListView(FilterView):
    model = Course
    template_name = "partials/course-list.html"
    context_object_name = "courses"
    filterset_class = CourseFilter
    paginate_by = 16

    def render_to_response(self, context, **response_kwargs):
        if not self.request.htmx:
            return render(self.request, "home.html")
        time.sleep(1)
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

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["is_creator"] = True
        return context


class CreatorCourseDetailView(LoginRequiredMixin, DetailView):
    model = Course
    template_name_suffix = "_creator_detail"

    def post(self, request, *args, **kwargs):
        operation_type = self.request.POST.get("op-type", None)
        if not operation_type:
            return HttpResponseBadRequest("Operation Type not provided")
        match operation_type:
            case "requirement":
                description = self.request.POST.get("description", None)
                if not description:
                    messages.error(request, "Need to provide description")
                    return HttpResponseBadRequest("Description required")
                requirement = CourseRequirement.objects.create(
                    course=self.get_object(), description=description
                )
                return HttpResponse(
                    f"<li>{requirement.description}</li>", content_type="text/html"
                )
            case "audience":
                description = self.request.POST.get("description", None)
                if not description:
                    messages.error(request, "Need to provide description")
                    return HttpResponseBadRequest("Description required")
                audience = CourseAudience.objects.create(
                    course=self.get_object(), description=description
                )
                return HttpResponse(
                    f"<li>{audience.description}</li>", content_type="text/html"
                )
            case "section":
                title = self.request.POST.get("title", None)
                if not title:
                    messages.error(request, "Need to provide title")
                    return HttpResponseBadRequest("Title Required")
                section = CourseSection.objects.create(
                    course=self.get_object(),
                    title=title,
                    order=CourseSection.objects.count(),
                )
                return HttpResponse(
                    f"<li>{section.title}</li>", content_type="text/html"
                )


class CourseLectureCreateView(LoginRequiredMixin, CreateView):
    model = CourseLecture
    form_class = CourseLectureForm
    template_name = "partials/base-form.html"

    def get_success_url(self) -> str:
        return self.request.META.get("HTTP_REFERER")


class CourseLectureEditView(LoginRequiredMixin, UpdateView):
    model = CourseLecture
    form_class = CourseLectureForm
    context_object_name = "lecture"

    def get_success_url(self) -> str:
        return self.request.META.get("HTTP_REFERER")

    def form_valid(self, form):
        ret = super().form_valid(form)
        return htmx_redirect(
            self.request,
            reverse_lazy(
                "core:creator_course_detail",
                kwargs={"pk": self.get_object().section.course.id},
            ),
        )


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

        match operation:
            case "add":
                course = get_object_or_404(Course, pk=request.POST.get("course_id"))
                if course.user == request.user:
                    messages.error(request, "You can't buy your own course 󰱶")
                    response = HttpResponse(status=200)
                    reswap(response, "none")
                    return trigger_client_event(response, "refresh_nav_cart")

                cart.add(request.POST.get("course_id"))
                messages.success(request, "Course Added to Cart!")
            case "clear":
                cart.clear()
                messages.success(request, "Cart Cleared!")
            case "checkout":
                user = self.request.user
                transaction = Transaction.initialize(
                    user, cart.total_price, courses=cart.courses
                )
                if transaction.status == TransactionStatus.FAILED:
                    messages.error(request, "Error Processing your buy request")
                else:
                    transaction.status = TransactionStatus.SUCCESS
                    transaction.save()
                    for course in cart:
                        course.enrolled_users.add(user)
                        course.save()
                    cart.clear()
                    return HttpResponseClientRedirect(transaction.checkout_url)

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


def handle_successful_payment(request: HttpRequest):
    body = request.body
    print(body)
    data = json.loads(body)
    print(data)
    return HttpResponse(data, status=200)
