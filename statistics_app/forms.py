# Django imports
from django import forms

# Local Imports
from workshop_app.models import states, WorkshopType


class FilterForm(forms.Form):
    from_date = forms.DateField(
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control'}
        )
    )
    to_date = forms.DateField(
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control'}
        )
    )
    workshop_type = forms.ModelChoiceField(
        queryset=WorkshopType.objects.all(), required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    state = forms.ChoiceField(
        choices=states, required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    show_workshops = forms.BooleanField(
        help_text="Show my workshops only", required=False,
    )
    sort = forms.ChoiceField(
        choices=(("date", "Oldest"), ("-date", "Latest")),
        help_text="Sort by",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    def __init__(self, *args, **kwargs):
        start = kwargs.pop("start") if "start" in kwargs else None
        end = kwargs.pop("end") if "end" in kwargs else None
        selected_state = kwargs.pop("state") if "state" in kwargs else None
        selected_type = kwargs.pop("type") if "type" in kwargs else None
        show_workshops = (kwargs.pop("show_workshops")
                            if "show_workshops" in kwargs else None)
        sort = kwargs.pop("sort") if "sort" in kwargs else None
        super(FilterForm, self).__init__(*args, **kwargs)
        self.fields["from_date"].initial = start
        self.fields["to_date"].initial = end
        self.fields["state"].initial = selected_state
        self.fields["workshop_type"].initial = selected_type
        self.fields["show_workshops"].initial = show_workshops
        self.fields["sort"].initial = sort
