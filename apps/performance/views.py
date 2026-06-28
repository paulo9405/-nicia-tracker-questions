from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .services.performance_service import PerformanceService


class PerformanceView(LoginRequiredMixin, TemplateView):
    template_name = "performance/stats.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["stats"] = PerformanceService.get_full_stats(self.request.user)
        return ctx
