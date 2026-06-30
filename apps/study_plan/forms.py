from django import forms
from django.core.exceptions import ValidationError

from .models import ActiveLearningNote, GuidedReflection


class ActiveLearningNoteForm(forms.ModelForm):
    class Meta:
        model = ActiveLearningNote
        fields = ["explanation"]
        widgets = {
            "explanation": forms.Textarea(
                attrs={
                    "rows": 8,
                    "class": "form-control",
                    "placeholder": "Escreva aqui sua explicação...",
                    "id": "id_explanation",
                }
            ),
        }
        labels = {
            "explanation": "Explique com suas palavras o que aprendeu neste capítulo",
        }

    def clean_explanation(self):
        text = self.cleaned_data.get("explanation", "").strip()
        if len(text) < 20:
            raise ValidationError(
                "Escreva pelo menos 20 caracteres para registrar sua explicação."
            )
        return text


class GuidedReflectionForm(forms.ModelForm):
    class Meta:
        model = GuidedReflection
        fields = ["what_understood", "most_important", "most_difficult"]
        widgets = {
            "what_understood": forms.Textarea(
                attrs={"rows": 4, "class": "form-control"}
            ),
            "most_important": forms.Textarea(
                attrs={"rows": 4, "class": "form-control"}
            ),
            "most_difficult": forms.Textarea(
                attrs={"rows": 4, "class": "form-control"}
            ),
        }
        labels = {
            "what_understood": "O que você entendeu neste capítulo?",
            "most_important": "Qual foi a parte mais importante?",
            "most_difficult": "Qual foi a parte mais difícil ou que gerou dúvida?",
        }
