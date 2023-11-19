from django import forms


class RepoAnalyzerForm(forms.Form):
    username_repo = forms.CharField(max_length=100)

    username_repo.widget.attrs.update({
        'class': 'form-control form-control-lg',
        'id': 'formGroupUserNameRepo',
        'placeholder': 'username/repo',
        'autocomplete': 'off'
    })
