"""Rate limiter configuration."""

from typing import Any, Callable, TypeVar

from app.config import get_settings

settings = get_settings()

F = TypeVar("F", bound=Callable[..., Any])


# Create appropriate limiter based on environment
if settings.environment == "test":

    class NoOpLimiter:
        """No-op limiter for testing."""

        def limit(self, limit_string: str) -> Callable[[F], F]:
            """Return a no-op decorator.
            
            Args:
                limit_string: Rate limit string (ignored for testing)
                
            Returns:
                A decorator function that returns the function unchanged
            """

            def decorator(func: F) -> F:
                return func

            return decorator

    limiter: Any = NoOpLimiter()
else:
    from slowapi import Limiter
    from slowapi.util import get_remote_address

    limiter = Limiter(key_func=get_remote_address)
