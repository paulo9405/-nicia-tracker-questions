from django.urls import path

from . import views

app_name = "exams"

urlpatterns = [
    path("", views.FilterView.as_view(), name="filter"),
    path("treino/<uuid:pk>/", views.PlayQuizView.as_view(), name="play"),
    path("resultado/<uuid:pk>/", views.ResultView.as_view(), name="result"),
    path("simulado/", views.SimulatedStartView.as_view(), name="simulated_start"),
    path("simulado/<uuid:pk>/", views.SimulatedPlayView.as_view(), name="simulated_play"),
]
