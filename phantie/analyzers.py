import logging
import requests


logger = logging.getLogger(__name__)


class RepoAnalyzer:
    """
    RepoAnalyzer is a class for analyzing GitHub repositories.

    Usage:
    - Create an instance of RepoAnalyzer with a GitHub username/repo as a parameter.
    - Call the analyze method to check various aspects of the repository.

    Example:
    analyzer = RepoAnalyzer("username/repo")
    results = analyzer.analyze()
    """
    GITHUB_API_URL = 'https://api.github.com/repos/{}'
    URL_RATE_LIMIT = 'https://api.github.com/rate_limit'
    HEADERS = {'content-type': 'application/json'}

    def __init__(self, username_repo):
        self.username_repo = username_repo
        self.results = []
        self.errors = []

    def analyze(self):
        try:
            if not self._rate_limit_ok():
                msg = 'GitHub API rate limit exceeded'
                self._save_error(msg)
                logger.info(msg)
                return False

            response = self._make_api_request(self.GITHUB_API_URL.format(self.username_repo))
            if response.status_code == 404:
                self._save_error('Repository not found')
                return False

            response.raise_for_status()
            repo_data = response.json()

            # Check basic info
            self._check_fork(repo_data['fork'])
            self._check_description(repo_data['description'])
            self._check_homepage(repo_data['homepage'])
            self._check_open_issues_pr(repo_data['open_issues_count'])

            return self.results
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return False

    def _rate_limit_ok(self):
        try:
            r = self._make_api_request(self.URL_RATE_LIMIT)
            rate_limit = int(r.json()['resources']['core']['remaining'])
            return rate_limit > 0
        except Exception as e:
            logger.error(f"An error occurred while checking rate limit: {e}")
            return False

    def _make_api_request(self, url):
        return requests.get(url, headers=self.HEADERS)

    def _save_result(self, label, status='danger', message=None):
        result = {'label': label, 'status': status}
        if message:
            result['message'] = message
        self.results.append(result)

    def _save_error(self, error_message):
        self.errors.append(error_message)

    def _check_fork(self, value):
        if value:
            self._save_result('This repository is a fork of another repository')

    def _check_description(self, value):
        if value:
            self._save_result('Description is ok', status='success')
        else:
            self._save_result('Description is missing',
                              message='It is a good practice to have a description of your project.')

    def _check_homepage(self, value):
        if value:
            self._save_result('Homepage is ok', status='success')
        else:
            self._save_result('Homepage is missing',
                              message='It is a good practice to have a homepage of your project.')

    def _check_open_issues_pr(self, open_issues_count):
        if open_issues_count > 0:
            self._save_result(f"The repository has {open_issues_count} opened issues and/or pull requests")
        else:
            self._save_result('No open issues or pull requests', status='success')
