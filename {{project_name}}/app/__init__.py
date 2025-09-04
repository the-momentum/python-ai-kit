import traceback

try:
    from app.user.models import User  # noqa: F401
except ImportError:
    traceback.print_exc()
    raise
