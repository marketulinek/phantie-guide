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
