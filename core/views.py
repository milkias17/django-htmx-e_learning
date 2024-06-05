from django.http import HttpRequest, HttpResponse, QueryDict
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from django.views.generic import CreateView, DetailView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin

from core.cart import Cart
from core.forms import CourseForm
from core.models import Course
from core.utils import render_html_block
from udemy.auth_utils import GroupRequiredMixin


def home(request):
    return render(request, "home.html")


class CoursesListView(ListView):
    model = Course
    template_name = "home.html"
    context_object_name = "courses"


class CourseCreateView(GroupRequiredMixin, LoginRequiredMixin, CreateView):
    model = Course
    queryset = Course.objects.order_by("-created_at")
    template_name_suffix = "_create_form"
    form_class = CourseForm
    success_url = reverse_lazy("core:index")
    group_required = "creator"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class CourseDetailView(LoginRequiredMixin, DetailView):
    model = Course

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        average_rating = course.average_rating
        context["checked_star"] = (round(average_rating * 2) / 2) * 2
        context["num_stars"] = average_rating
        context["odd_even"] = [(i % 2) + 1 for i in range(10)]
        cart = Cart(self.request)
        context["in_cart"] = course in cart
        return context


class CartOperations(View):
    def get(self, request, *args, **kwargs):
        cart = Cart(request)
        return render(request, "core/cart.html", context={"cart": cart})

    def post(self, request: HttpRequest, *args, **kwargs):
        operation = self.request.POST.get("operation")
        cart = Cart(request)

        match operation:
            case "add":
                print("Add to cart: ", request.POST.get("course_id"))
                cart.add(request.POST.get("course_id"))
            case "clear":
                cart.clear()
            case "checkout":
                user = self.request.user
                user.enrolled_courses.add(*cart.cart)
                user.save()
                cart.clear()
                return redirect("core:index")

        return HttpResponse(status=200)

    def delete(self, request, *args, **kwargs):
        data = QueryDict(request.body)
        cart = Cart(request)
        cart.remove(data.get("course_id"))
        return render_html_block("core/cart.html", "courses", {"cart": cart}, request)
