from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("conta/", include("apps.accounts.urls", namespace="accounts")),
    path("questoes/", include("apps.exams.urls", namespace="exams")),
    path("", include("apps.dashboard.urls", namespace="dashboard")),
    path("estatisticas/", include("apps.performance.urls", namespace="performance")),
]
