from django import forms

class maintenance_issue():
    OPTIONS = (
        ('option1', 'Opción 1'),
        ('option2', 'Opción 2'),
        ('option3', 'Opción 3'),
    )
    option = forms.ChoiceField(choices=OPTIONS, widget=forms.RadioSelect(), required=True)
    notas = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=True)

