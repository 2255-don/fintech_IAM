from django import forms

from apps.core.forms import StyledFormMixin


class DepotCreateForm(StyledFormMixin, forms.Form):
    nb_mises = forms.IntegerField(label="Nombre de mises", min_value=1)


class RetraitCreateForm(StyledFormMixin, forms.Form):
    montant = forms.IntegerField(label="Montant du retrait (FCFA)", min_value=1)
    motif = forms.CharField(label="Motif", required=False, widget=forms.Textarea(attrs={"rows": 4}))


class EmergencyWithdrawalForm(StyledFormMixin, forms.Form):
    montant = forms.IntegerField(label="Montant a remettre au client (FCFA)", min_value=1)
    motif = forms.CharField(
        label="Motif du retrait d'urgence",
        required=False,
        widget=forms.Textarea(attrs={"rows": 4}),
    )
