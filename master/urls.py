from django.urls import path

from . import views

app_name = "master"
urlpatterns = [
    ####---- Authentication system ------------------------------
    # path('loggin/', views.login_user, name='login-user'),
    path("", views.login_user, name="login-user"),
    path("loggout/", views.logout_user, name="logout-user"),
    # path('register/', views.register_user, name='register-user'),
]
