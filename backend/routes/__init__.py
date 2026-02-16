"""
Vimarsh Routes Package — Azure Functions Blueprints

Modular route blueprints extracted from the monolithic function_app.py:

  - admin_bp:          vimarsh-admin/* (28 routes)
  - diagnostics_bp:    diagnostic, test, health, health/embeddings (4 routes)
  - guidance_bp:       guidance (1 route) + template helpers
  - personalities_bp:  personalities/active (1 route)
  - wisdom_bp:         wisdom-of-day, share/*, wisdom/*, og-image (7 routes)
  - user_bp:           user/* (5 routes)
  - voice_bp:          voice/* (2 routes)

Note: engagement, onboarding, memory, and notification routes are already
extracted into their respective packages and registered directly in function_app.py.
"""

from routes.admin_bp import bp as admin_bp
from routes.diagnostics_bp import bp as diagnostics_bp
from routes.guidance_bp import bp as guidance_bp
from routes.personalities_bp import bp as personalities_bp
from routes.wisdom_bp import bp as wisdom_bp
from routes.user_bp import bp as user_bp
from routes.voice_bp import bp as voice_bp

ALL_BLUEPRINTS = [
    admin_bp,
    diagnostics_bp,
    guidance_bp,
    personalities_bp,
    wisdom_bp,
    user_bp,
    voice_bp,
]
