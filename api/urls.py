from django.urls import path

from . import views

app_name = "api"
urlpatterns = [
    path("reply/", views.EcholaliaView.as_view()),
    path("numeron/", views.NumeronView.as_view()),
]
