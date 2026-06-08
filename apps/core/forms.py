from django import forms


class StyledFormMixin:
    base_input_class = (
        "w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 "
        "shadow-sm outline-none transition focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100"
    )
    base_textarea_class = (
        "min-h-[120px] w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 "
        "shadow-sm outline-none transition focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100"
    )
    base_select_class = (
        "w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 "
        "shadow-sm outline-none transition focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100"
    )

    def apply_style(self) -> None:
        for field in self.fields.values():
            widget = field.widget
            current = widget.attrs.get("class", "")

            if isinstance(widget, forms.Textarea):
                css_class = self.base_textarea_class
            elif isinstance(widget, (forms.Select, forms.SelectMultiple, forms.DateInput)):
                css_class = self.base_select_class
            else:
                css_class = self.base_input_class

            widget.attrs["class"] = f"{css_class} {current}".strip()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_style()
