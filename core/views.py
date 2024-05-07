from django.shortcuts import render

class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

def home(request):
    return render(request, "home.html")
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


