import phantie.result_types as result_types
import requests


class RepoAnalyzer:
    def __init__(self, username_repo):
        self.headers = {'content-type': 'application/json'}
        self.github_api_url = f'https://api.github.com/repos/{username_repo}'
        self.url_rate_limit = 'https://api.github.com/rate_limit'
        self.results = []

    def analyze(self):
        if not self._rate_limit_ok():
            self._fill_results(
                result_types.NotWorkingResultType,
                'GitHub API rate limit exceeded',
                'Please try again later.'
            )
            return self.results

        response = requests.get(self.github_api_url, headers=self.headers)
        response.raise_for_status()
        repo_data = response.json()

        # Check basic info
        self._check_fork(repo_data['fork'])
        self._check_description(repo_data['description'])
        self._check_homepage(repo_data['homepage'])
        self._check_open_issues_pr(repo_data['open_issues_count'])

        return self.results

    def _rate_limit_ok(self):
        r = requests.get(self.url_rate_limit, headers=self.headers)
        rate_limit = int(r.json()['resources']['core']['remaining'])
        return rate_limit > 5

    def _fill_results(self, result_type, label, message=None, links=None):
        self.results.append({
            'label': label,
            'status': result_type.color_class,
            'message': message,
            'links': links,
            'svg_data': result_type.svg_data,
        })

    def _check_fork(self, value):
        if value:
            self._fill_results(
                result_types.BadResultType,
                'This repository is a fork of another repository',
                "That's not good."
            )

    def _check_description(self, value):
        if value:
            self._fill_results(result_types.SuccessResultType, 'Description is ok')
        else:
            self._fill_results(
                result_types.BadResultType,
                'Description is missing',
                "That's not good.",
                'Look here..'
            )

    def _check_homepage(self, value):
        if value:
            self._fill_results(result_types.SuccessResultType, 'Homepage is ok')
        else:
            self._fill_results(
                result_types.BadResultType,
                'Homepage is missing',
                "That's not good.",
                'Look here..'
            )

    def _check_open_issues_pr(self, open_issues_count):
        if open_issues_count > 0:
            self._fill_results(
                result_types.WarningResultType,
                f"The repository has {open_issues_count} opened issues and/or pull requests"
            )
        else:
            self._fill_results(result_types.SuccessResultType, 'No open issues or pull requests')
