# settings.py
INSTALLED_APPS = ["corsheaders", ...]
MIDDLEWARE = ["corsheaders.middleware.CorsMiddleware",
              "django.middleware.common.CommonMiddleware", ...]
CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]
