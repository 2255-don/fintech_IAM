from django import forms
from django.contrib.auth import get_user_model

from apps.core.forms import StyledFormMixin


User = get_user_model()


class AgentBaseForm(StyledFormMixin, forms.Form):
    username = forms.CharField(label="Nom d'utilisateur", max_length=150)
    first_name = forms.CharField(label="Prénom", max_length=150)
    last_name = forms.CharField(label="Nom", max_length=150)
    telephone = forms.CharField(label="Téléphone", max_length=30, required=False)
    email = forms.EmailField(label="E-mail", required=False)
    adresse = forms.CharField(label="Adresse", required=False, widget=forms.Textarea(attrs={"rows": 4}))


class AgentCreateForm(AgentBaseForm):
    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ce nom d'utilisateur est déjà utilisé.")
        return username


class AgentUpdateForm(AgentBaseForm):
    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        queryset = User.objects.filter(username=username)
        if self.user is not None:
            queryset = queryset.exclude(id=self.user.id)
        if queryset.exists():
            raise forms.ValidationError("Ce nom d'utilisateur est déjà utilisé.")
        return username
