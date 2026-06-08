from django import forms

from apps.core.forms import StyledFormMixin


class CycleCreateForm(StyledFormMixin, forms.Form):
    mise = forms.IntegerField(label="Mise (FCFA)", min_value=100)
