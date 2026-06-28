from django import forms

from apps.questions.models import Subject, Topic


class QuizFilterForm(forms.Form):
    QUANTITY_CHOICES = [("10", "10 questões"), ("20", "20 questões"), ("50", "50 questões")]

    subject = forms.ModelChoiceField(
        queryset=Subject.objects.filter(is_active=True).order_by("name"),
        label="Disciplina",
        empty_label="— Escolha uma disciplina —",
        widget=forms.Select(attrs={"class": "form-select", "id": "id_subject"}),
    )
    topic = forms.ModelChoiceField(
        queryset=Topic.objects.filter(is_active=True).order_by("name"),
        required=False,
        label="Tópico (opcional)",
        empty_label="Todos os tópicos",
        widget=forms.Select(attrs={"class": "form-select", "id": "id_topic"}),
    )
    quantity = forms.ChoiceField(
        choices=QUANTITY_CHOICES,
        initial="10",
        label="Quantidade de questões",
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
    )

    def clean(self):
        cleaned = super().clean()
        subject = cleaned.get("subject")
        topic = cleaned.get("topic")
        if topic and subject and topic.subject != subject:
            raise forms.ValidationError("O tópico selecionado não pertence à disciplina.")
        return cleaned
