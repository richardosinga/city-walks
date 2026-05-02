from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "dev-only-change-in-production"
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "city_walks_app",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
            ],
        },
    },
]

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Optional: path to a world66 content directory to use as POI fallback.
# Override with env var WORLD66_CONTENT_DIR when world66 is not a sibling repo.
import os as _os
_w66_env = _os.environ.get("WORLD66_CONTENT_DIR")
if _w66_env:
    WORLD66_CONTENT_DIR = Path(_w66_env)
else:
    # Try common locations: sibling dir, home/Repos/world66, etc.
    _candidates = [
        BASE_DIR.parent / "world66" / "content",
        Path.home() / "Repos" / "world66" / "content",
        Path.home() / "repos" / "world66" / "content",
        Path.home() / "projects" / "world66" / "content",
    ]
    WORLD66_CONTENT_DIR = next((p for p in _candidates if p.is_dir()), None)
