from django import forms

from apps.core.forms import StyledFormMixin


class ClientCreateForm(StyledFormMixin, forms.Form):
    nom = forms.CharField(label="Nom", max_length=100)
    prenom = forms.CharField(label="Prénom", max_length=100, required=False)
    telephone = forms.CharField(label="Téléphone", max_length=30)
    genre = forms.CharField(label="Genre", max_length=20, required=False)
    date_naissance = forms.DateField(
        label="Date de naissance",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    email = forms.EmailField(label="E-mail", required=False)
    adresse = forms.CharField(label="Adresse", required=False, widget=forms.Textarea(attrs={"rows": 4}))


class ClientUpdateForm(ClientCreateForm):
    pass
