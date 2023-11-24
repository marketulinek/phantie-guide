from django.shortcuts import render

from .analyzers import RepoAnalyzer
from .forms import RepoAnalyzerForm


def homepage(request):
    results = []
    errors = []
    form_init = {}
    form_user_input_value = request.GET.get('username_repo', None)

    if form_user_input_value:
        form_init = {'username_repo': form_user_input_value}
        analyzer = RepoAnalyzer(form_user_input_value)
        results = analyzer.analyze()
        errors = analyzer.errors

    form = RepoAnalyzerForm(initial=form_init)
    context = {'form': form, 'results': results, 'errors': errors}
    return render(request, 'home.html', context)
