from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import RegisterUserForm


####---- Authentication system ------------------------------
def login_user(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            username = request.POST["username"]
            password = request.POST["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(reverse("a01_note:home"))
            else:
                messages.error(
                    request, ("There was an error. Please, try again")
                )
                return redirect(reverse("master:login-user"))
        context = {
            "web_title": "Log in | App Notes",
            "page_title": "Login to your account",
        }
        return render(request, "master/login.html", context)
    else:
        return redirect(reverse("a01_note:home"))


def logout_user(request):
    logout(request)
    messages.success(request, ("Hope to see you again : )"))
    return redirect(reverse("master:login-user"))


## User registration flow: Save, authenticate, login, and redirect
def register_user(request):
    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password1"]
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(
                request, ("Your registration was successfully completed! :D")
            )
            return redirect(reverse("a01_note:home"))
        else:
            messages.error(request, ("There was a error with your form..."))
    else:
        form = RegisterUserForm(label_suffix="")
    context = {
        "form": form,
        "web_title": "Registration | App Notes",
        "page_title": "Create an Account",
    }
    return render(request, "master/register.html", context)


# return HttpResponse(f"Working perfectly ;D ...<br>")
