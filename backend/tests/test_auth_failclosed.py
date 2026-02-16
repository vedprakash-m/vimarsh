"""
Test: Auth module fail-closed behavior.

When auth dependencies are unavailable, auth decorators MUST deny requests
with HTTP 503 — never silently pass through (fail-open).
"""

import importlib
import sys
import unittest
from unittest.mock import MagicMock, patch


class TestAuthFailClosed(unittest.TestCase):
    """Verify auth module denies access when dependencies are missing."""

    def _reload_auth_with_import_error(self):
        """Force-reload auth module with unified_auth_service unavailable."""
        # Remove cached modules so re-import triggers the except branch
        modules_to_remove = [
            k for k in sys.modules
            if k.startswith("auth.") or k == "auth"
        ]
        for mod in modules_to_remove:
            del sys.modules[mod]

        # Make unified_auth_service raise ImportError
        with patch.dict(sys.modules, {"auth.unified_auth_service": None}):
            import auth as auth_module
            importlib.reload(auth_module)
            return auth_module

    def test_unified_auth_flag_is_false_on_import_error(self):
        auth_mod = self._reload_auth_with_import_error()
        self.assertFalse(auth_mod.UNIFIED_AUTH_AVAILABLE)

    def test_require_auth_returns_503(self):
        auth_mod = self._reload_auth_with_import_error()

        # Create a dummy handler
        @auth_mod.require_auth
        def my_handler(req):
            return "should never reach here"

        # Create a mock Azure Functions HttpRequest
        mock_req = MagicMock()

        # Call the decorated handler
        response = my_handler(mock_req)

        # Must return 503
        self.assertEqual(response.status_code, 503)

    def test_require_admin_returns_503(self):
        auth_mod = self._reload_auth_with_import_error()

        @auth_mod.require_admin
        def admin_handler(req):
            return "should never reach here"

        mock_req = MagicMock()
        response = admin_handler(mock_req)
        self.assertEqual(response.status_code, 503)

    def test_super_admin_required_returns_503(self):
        auth_mod = self._reload_auth_with_import_error()

        @auth_mod.super_admin_required
        def super_admin_handler(req):
            return "should never reach here"

        mock_req = MagicMock()
        response = super_admin_handler(mock_req)
        self.assertEqual(response.status_code, 503)

    def test_optional_auth_still_passes_through(self):
        """optional_auth should NOT block — anonymous access is intentional."""
        auth_mod = self._reload_auth_with_import_error()

        @auth_mod.optional_auth
        def public_handler(req):
            return "accessible"

        mock_req = MagicMock()
        result = public_handler(mock_req)
        self.assertEqual(result, "accessible")


if __name__ == "__main__":
    unittest.main()
