from django.urls import path

from . import views

app_name = "study_plan"

urlpatterns = [
    path("", views.PlanDashboardView.as_view(), name="dashboard"),
    path("modulos/", views.ModuleListView.as_view(), name="module_list"),
    path("modulo/<slug:slug>/", views.ModuleDetailView.as_view(), name="module_detail"),
    path("capitulo/<slug:module_slug>/<slug:slug>/", views.ChapterReadView.as_view(), name="chapter_read"),
    path("capitulo/<slug:module_slug>/<slug:slug>/concluir/", views.ChapterCompleteView.as_view(), name="chapter_complete"),
    path("capitulo/<slug:module_slug>/<slug:slug>/nota/", views.ChapterNoteView.as_view(), name="chapter_note"),
    path("capitulo/<slug:module_slug>/<slug:slug>/reflexao/", views.ChapterReflectionView.as_view(), name="chapter_reflection"),
    path("capitulo/<slug:module_slug>/<slug:slug>/mini-quiz/", views.ChapterMiniQuizView.as_view(), name="chapter_mini_quiz"),
    path("caderno-de-erros/", views.ErrorNotebookView.as_view(), name="error_notebook"),
    path("caderno-de-erros/<uuid:pk>/nota/", views.ErrorNoteView.as_view(), name="error_note"),
    path("caderno-de-erros/<uuid:pk>/revisar/", views.ErrorReviewView.as_view(), name="error_review"),
    path("progresso/", views.ProgressView.as_view(), name="progress"),
]
