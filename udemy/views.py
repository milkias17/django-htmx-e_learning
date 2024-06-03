from django import forms
from django.contrib.admin.options import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render


class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            match visible.widget_type:
                case "text" | "number" | "email" | "password":
                    visible.field.widget.attrs["class"] = (
                        "input input-bordered input-sm"
                    )
                case "select" | "selectmultiple":
                    visible.field.widget.attrs["class"] = (
                        "select select-bordered select-sm"
                    )
                case "date":
                    visible.field.widget = forms.DateInput(
                        attrs={"type": "date", "class": "input input-bordered input-sm"}
                    )


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/")
        else:
            messages.error(request, form.errors)
            return render(request, "registration/register.html", {"form": form})
    else:
        form = RegisterForm()
        return render(request, "registration/register.html", {"form": form})
