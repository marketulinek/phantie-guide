from django.shortcuts import render

from .analyzers import RepoAnalyzer
from .forms import RepoAnalyzerForm


def homepage(request):
    repo_results = []
    form_init = {}
    form_user_input_value = request.GET.get('username_repo', None)

    if form_user_input_value:
        form_init = {'username_repo': form_user_input_value}
        repo_results = RepoAnalyzer(form_user_input_value).analyze()

    form = RepoAnalyzerForm(initial=form_init)
    context = {'form': form, 'repo_results': repo_results}
    return render(request, 'home.html', context)
