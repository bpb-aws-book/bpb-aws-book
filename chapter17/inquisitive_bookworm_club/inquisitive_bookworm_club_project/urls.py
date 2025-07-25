"""
URL configuration for inquisitive_bookworm_club_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include
from books import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.login_view, name="login"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("password-reset/", views.password_reset_view, name="password_reset"),
    path("force-password-reset/", views.force_password_reset_view, name="force_password_reset"),
    path("home/", views.home, name="home"),
    path("details/<int:pk>/", views.details, name="details"),
    path("rentbook/<int:pk>/", views.rentbook, name="rentbook"),
    path("returnbook/<int:pk>/", views.returnbook, name="returnbook"),
    path("about/", views.about, name="about"),
    path("api-test/", views.api_test, name="api_test")]
