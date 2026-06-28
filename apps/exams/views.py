from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import FormView, TemplateView, View

from apps.questions.services.question_service import QuestionService

from .forms import QuizFilterForm
from .models import Quiz
from .services.quiz_service import QuizService
from .services.simulated_service import (
    TIME_LIMIT_MINUTES,
    InsufficientQuestionsError,
    SimulatedService,
)


def _get_quiz_for_user(quiz_id, user):
    """Retorna o quiz ou 404; impede acesso a quizzes de outros usuários."""
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    if quiz.user != user:
        raise Http404
    return quiz


class FilterView(LoginRequiredMixin, FormView):
    """Formulário de seleção: disciplina, tópico e quantidade."""

    template_name = "exams/filter.html"
    form_class = QuizFilterForm

    def form_valid(self, form):
        subject = form.cleaned_data["subject"]
        topic = form.cleaned_data.get("topic")
        quantity = int(form.cleaned_data["quantity"])

        available = QuestionService.count_available(
            subject_id=str(subject.pk),
            topic_id=str(topic.pk) if topic else None,
        )

        if available == 0:
            messages.warning(
                self.request,
                "Nenhuma questão encontrada com os filtros selecionados.",
            )
            return self.form_invalid(form)

        quiz = QuizService.create_practice_quiz(
            user=self.request.user,
            subject_id=str(subject.pk),
            topic_id=str(topic.pk) if topic else None,
            quantity=quantity,
        )
        return redirect("exams:play", pk=quiz.pk)


class PlayQuizView(LoginRequiredMixin, TemplateView):
    """Exibe as questões e recebe as respostas."""

    template_name = "exams/play.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        quiz = _get_quiz_for_user(self.kwargs["pk"], self.request.user)
        if quiz.is_finished:
            return {"redirect_to_result": True, "quiz": quiz}

        quiz_questions = (
            quiz.quiz_questions.select_related("question__subject")
            .prefetch_related("question__alternatives")
            .order_by("order")
        )
        ctx["quiz"] = quiz
        ctx["quiz_questions"] = quiz_questions
        return ctx

    def get(self, request, *args, **kwargs):
        ctx = self.get_context_data(**kwargs)
        if ctx.get("redirect_to_result"):
            return redirect("exams:result", pk=ctx["quiz"].pk)
        return self.render_to_response(ctx)

    def post(self, request, *args, **kwargs):
        quiz = _get_quiz_for_user(self.kwargs["pk"], request.user)
        if quiz.is_finished:
            return redirect("exams:result", pk=quiz.pk)

        raw_answers = {
            key[2:]: value
            for key, value in request.POST.items()
            if key.startswith("q_")
        }
        QuizService.submit_answers(quiz, raw_answers)
        return redirect("exams:result", pk=quiz.pk)


class ResultView(LoginRequiredMixin, TemplateView):
    """Exibe o resultado com acertos, erros e explicações."""

    template_name = "exams/result.html"

    def get(self, request, *args, **kwargs):
        quiz = _get_quiz_for_user(self.kwargs["pk"], request.user)
        if not quiz.is_finished:
            if quiz.quiz_type == Quiz.SIMULATED:
                return redirect("exams:simulated_play", pk=quiz.pk)
            return redirect("exams:play", pk=quiz.pk)

        result = QuizService.get_result(quiz)
        ctx = {"result": result, "quiz": quiz}

        if quiz.quiz_type == Quiz.SIMULATED:
            ctx["subject_breakdown"] = SimulatedService.get_subject_breakdown(quiz)

        return self.render_to_response(ctx)


class SimulatedStartView(LoginRequiredMixin, View):
    """Página de início do simulado; cria o quiz ao receber POST."""

    def get(self, request):
        in_progress = SimulatedService.get_in_progress(request.user)
        if in_progress:
            return redirect("exams:simulated_play", pk=in_progress.pk)

        return self.render(request)

    def post(self, request):
        in_progress = SimulatedService.get_in_progress(request.user)
        if in_progress:
            return redirect("exams:simulated_play", pk=in_progress.pk)

        try:
            quiz = SimulatedService.create_simulated_quiz(request.user)
        except InsufficientQuestionsError as exc:
            messages.error(request, str(exc))
            return self.render(request)

        return redirect("exams:simulated_play", pk=quiz.pk)

    def render(self, request):
        from django.shortcuts import render as django_render

        return django_render(
            request,
            "exams/simulated_start.html",
            {
                "time_limit_minutes": TIME_LIMIT_MINUTES,
                "basic_per_subject": 5,
                "specific_total": 20,
                "total": 40,
            },
        )


class SimulatedPlayView(LoginRequiredMixin, TemplateView):
    """Exibe as 40 questões do simulado com cronômetro."""

    template_name = "exams/simulated_play.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        quiz = _get_quiz_for_user(self.kwargs["pk"], self.request.user)

        if quiz.is_finished:
            return {"redirect_to_result": True, "quiz": quiz}

        if quiz.quiz_type != Quiz.SIMULATED:
            return {"redirect_to_play": True, "quiz": quiz}

        quiz_questions = (
            quiz.quiz_questions.select_related("question__subject")
            .prefetch_related("question__alternatives")
            .order_by("order")
        )
        ctx["quiz"] = quiz
        ctx["quiz_questions"] = quiz_questions
        ctx["time_limit_minutes"] = TIME_LIMIT_MINUTES
        return ctx

    def get(self, request, *args, **kwargs):
        ctx = self.get_context_data(**kwargs)
        if ctx.get("redirect_to_result"):
            return redirect("exams:result", pk=ctx["quiz"].pk)
        if ctx.get("redirect_to_play"):
            return redirect("exams:play", pk=ctx["quiz"].pk)
        return self.render_to_response(ctx)

    def post(self, request, *args, **kwargs):
        quiz = _get_quiz_for_user(self.kwargs["pk"], request.user)
        if quiz.is_finished:
            return redirect("exams:result", pk=quiz.pk)

        raw_answers = {
            key[2:]: value
            for key, value in request.POST.items()
            if key.startswith("q_")
        }
        QuizService.submit_answers(quiz, raw_answers)
        return redirect("exams:result", pk=quiz.pk)
