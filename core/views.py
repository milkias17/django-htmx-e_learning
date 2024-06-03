from django.shortcuts import render
from django.urls import reverse_lazy

from django.views.generic import CreateView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from core.forms import CourseForm
from core.models import Course
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
        context =  super().get_context_data(**kwargs)
        context["num_stars"] = self.get_object().average_rating
        context["empty_stars"] = 5 - context["num_stars"]
        return context
