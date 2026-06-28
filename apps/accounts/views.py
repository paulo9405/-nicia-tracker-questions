from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.shortcuts import redirect, resolve_url
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView, UpdateView

from .forms import LoginForm, ProfileForm, RegisterForm
from .services.user_service import UserService


class RegisterView(FormView):
    template_name = "accounts/register.html"
    form_class = RegisterForm
    success_url = reverse_lazy("dashboard:home")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard:home")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        UserService.register(form, self.request)
        messages.success(
            self.request, "Conta criada com sucesso! Bem-vinda ao Nícia Track."
        )
        return super().form_valid(form)


class LoginView(DjangoLoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return resolve_url("dashboard:home")


class LogoutView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/logout_confirm.html"

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.info(request, "Você saiu da sua conta.")
        return redirect("accounts:login")


class ProfileView(LoginRequiredMixin, FormView):
    template_name = "accounts/profile.html"
    form_class = ProfileForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.request.user.profile
        return kwargs

    def get_initial(self):
        user = self.request.user
        return {"first_name": user.first_name, "last_name": user.last_name}

    def form_valid(self, form):
        UserService.update_profile(self.request.user, form)
        messages.success(self.request, "Perfil atualizado com sucesso.")
        return redirect("accounts:profile")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["user"] = self.request.user
        return ctx
