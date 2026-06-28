from django import forms

from apps.questions.models import Subject, Topic


class TopicSelect(forms.Select):
    def __init__(self, *args, **kwargs):
        self.topic_subjects = {}
        super().__init__(*args, **kwargs)

    def create_option(self, name, value, label, selected, index, subgroup=None, attrs=None, subindex=None):
        option = super().create_option(name, value, label, selected, index, subgroup, attrs, subindex)
        if value:
            subject_id = self.topic_subjects.get(str(value))
            if subject_id:
                option["attrs"]["data-subject"] = subject_id
        return option


class QuizFilterForm(forms.Form):
    QUANTITY_CHOICES = [
        ("10", "10 questões"),
        ("20", "20 questões"),
        ("50", "50 questões"),
    ]

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
        widget=TopicSelect(attrs={"class": "form-select", "id": "id_topic"}),
    )
    quantity = forms.ChoiceField(
        choices=QUANTITY_CHOICES,
        initial="10",
        label="Quantidade de questões",
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        topics = Topic.objects.filter(is_active=True).select_related("subject")
        self.fields["topic"].widget.topic_subjects = {
            str(t.pk): str(t.subject_id) for t in topics
        }

    def clean(self):
        cleaned = super().clean()
        subject = cleaned.get("subject")
        topic = cleaned.get("topic")
        if topic and subject and topic.subject != subject:
            raise forms.ValidationError(
                "O tópico selecionado não pertence à disciplina."
            )
        return cleaned
