from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .services.dashboard_service import DashboardService


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["stats"] = DashboardService.get_stats(self.request.user)
        return ctx
