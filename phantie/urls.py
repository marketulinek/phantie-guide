from django.urls import path

import phantie.views as views

urlpatterns = [
    path('', views.homepage, name='home'),
]
