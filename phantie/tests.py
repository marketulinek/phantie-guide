from django.test import TestCase
from unittest.mock import patch, MagicMock
from phantie.analyzers import RepoAnalyzer


class RepoAnalyzerTests(TestCase):

    def setUp(self):
        patcher = patch('phantie.analyzers.requests.get')
        self.mock_requests_get = patcher.start()
        self.addCleanup(patcher.stop)

    def create_mock_response(self, status_code, json_data):
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = json_data
        return mock_response

    def test_api_rate_limit_ok(self):
        """Test that _rate_limit_ok method returns True when API rate limit is sufficient."""
        self.mock_requests_get.return_value = self.create_mock_response(200, {'resources': {'core': {'remaining': 55}}})

        analyzer = RepoAnalyzer('testuser/testrepo')
        rate_limit_ok = analyzer._rate_limit_ok()
        self.assertTrue(rate_limit_ok)

    def test_api_rate_limit_exceeded(self):
        """Test that _rate_limit_ok method returns False when API rate limit is exceeded."""
        self.mock_requests_get.return_value = self.create_mock_response(200, {'resources': {'core': {'remaining': 0}}})

        analyzer = RepoAnalyzer('testuser/testrepo')
        rate_limit_ok = analyzer._rate_limit_ok()
        self.assertFalse(rate_limit_ok)
        # TODO: check error list

    def test_analyze_success(self):
        """Test analyze method for successful case."""
        self.mock_requests_get.side_effect = [
            self.create_mock_response(200, {'resources': {'core': {'remaining': 55}}}),
            self.create_mock_response(200, {'description': 'Test repo', 'homepage': 'http://test.com', 'open_issues_count': 5, 'fork': False}),
        ]

        analyzer = RepoAnalyzer('testuser/testrepo')
        results = analyzer.analyze()

        expected_results = [
            {'label': 'Description is ok', 'status': 'success'},
            {'label': 'Homepage is ok', 'status': 'success'},
            {'label': 'The repository has 5 opened issues and/or pull requests', 'status': 'danger'},
        ]
        self.assertEqual(results, expected_results)

    def test_analyze_not_found(self):
        """Test analyze method for repository not found case."""
        self.mock_requests_get.side_effect = [
            self.create_mock_response(200, {'resources': {'core': {'remaining': 55}}}),
            self.create_mock_response(404, {'message': 'Not Found', 'documentation_url': '...'}),
        ]

        analyzer = RepoAnalyzer('testuser/testrepo')
        results = analyzer.analyze()
        self.assertFalse(results)

        expected_errors = ['Repository not found']
        self.assertEqual(analyzer.errors, expected_errors)
