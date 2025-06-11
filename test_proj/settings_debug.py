# Import specific settings instead of using star imports
import os
import logging
from datetime import datetime

# Import specific items from the main settings to avoid F403/F405 issues
from .settings import (
    BASE_DIR,
    SECRET_KEY,
    MIDDLEWARE,
)

# Override DEBUG setting
DEBUG = True

# Add STATIC_ROOT for collectstatic to work
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Allow all hosts for testing
ALLOWED_HOSTS = ["*"]

# Create logs directory if it doesn't exist
LOGS_DIR = os.path.join(BASE_DIR, "..", "request_logs")
os.makedirs(LOGS_DIR, exist_ok=True)


class RequestBasedFileHandler(logging.Handler):
    """Custom logging handler that creates separate log files per request."""

    def __init__(self):
        super().__init__()
        self.setFormatter(
            logging.Formatter(
                "{levelname} {asctime} {name} {process:d} {thread:d} {message}",
                style="{",
            )
        )

    def emit(self, record):
        # Get the current request info if available
        request_id = getattr(record, "request_id", "unknown")
        user_type = getattr(record, "user_type", "unknown")
        url_path = (
            getattr(record, "url_path", "unknown").replace("/", "_").strip("_")
            or "root"
        )

        # Create filename based on request info
        if request_id != "unknown":
            filename = f"{request_id}_{user_type}_{url_path}.log"
        else:
            # Fallback for non-request logs
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"general_{timestamp}.log"

        log_path = os.path.join(LOGS_DIR, filename)

        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(self.format(record) + "\n")
        except Exception:
            # Fallback to console if file writing fails
            print(f"Failed to write to {log_path}: {self.format(record)}")


class RequestLoggingMiddleware:
    """Middleware to add request context to log records."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.request_counter = 0

    def __call__(self, request):
        # Generate unique request ID
        self.request_counter += 1
        request_id = f"req_{self.request_counter:03d}"

        # Determine user type
        if hasattr(request, "user") and request.user.is_authenticated:
            if hasattr(request.user, "is_guest_user") and request.user.is_guest_user:
                user_type = "guest"
            elif request.user.is_superuser:
                user_type = "admin"
            else:
                user_type = "regular"
        else:
            user_type = "anonymous"

        # Store request info for logging
        request._logging_info = {
            "request_id": request_id,
            "user_type": user_type,
            "url_path": request.path,
            "method": request.method,
            "timestamp": datetime.now().isoformat(),
        }

        # Add custom filter to all loggers
        class RequestFilter(logging.Filter):
            def filter(self, record):
                record.request_id = request_id
                record.user_type = user_type
                record.url_path = request.path
                return True

        # Apply filter to Django loggers
        for logger_name in ["django", "django.request", "django.server", "guest_user"]:
            logger = logging.getLogger(logger_name)
            # Remove existing filters to avoid duplicates
            logger.filters = [
                f for f in logger.filters if not isinstance(f, RequestFilter)
            ]
            logger.addFilter(RequestFilter())

        # Log request start
        logger = logging.getLogger("django.request")
        logger.info(
            f"=== REQUEST START === {request.method} {request.path} [User: {user_type}] [ID: {request_id}]"
        )

        response = self.get_response(request)

        # Log request end
        logger.info(
            f"=== REQUEST END === {request.method} {request.path} [Status: {response.status_code}] [ID: {request_id}]"
        )

        return response


# Enhanced logging configuration with request-based file separation
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {name} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
        "request_detailed": {
            "format": "{levelname} {asctime} [{request_id}] [{user_type}] {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file_main": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "../django_debug_main.log",
            "formatter": "verbose",
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "request_based": {
            "level": "DEBUG",
            "class": "test_proj.settings_debug.RequestBasedFileHandler",
        },
    },
    "root": {
        "handlers": ["file_main", "console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["file_main", "console", "request_based"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["file_main", "console", "request_based"],
            "level": "DEBUG",
            "propagate": False,
        },
        "django.server": {
            "handlers": ["file_main", "console", "request_based"],
            "level": "DEBUG",
            "propagate": False,
        },
        "guest_user": {
            "handlers": ["file_main", "console", "request_based"],
            "level": "DEBUG",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["request_based"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

# Add the middleware
MIDDLEWARE = [
    "test_proj.settings_debug.RequestLoggingMiddleware",
] + MIDDLEWARE

# Use environment variables for sensitive settings
SECRET_KEY = os.environ.get("SECRET_KEY", SECRET_KEY)

# Additional debug settings
INTERNAL_IPS = ["127.0.0.1", "localhost"]

# Enable SQL query logging for guest user operations
if DEBUG:
    LOGGING["loggers"]["django.db.backends"]["level"] = "DEBUG"
