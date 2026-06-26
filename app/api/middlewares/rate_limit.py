import os
from slowapi import Limiter
from slowapi.util import get_remote_address

# We use an abstraction so that we can potentially inject Redis storage in production
# Defaulting to in-memory for immediate local execution if Redis string is not set.

def get_real_ip(request):
    """
    Utility to get the real IP address, accounting for reverse proxies.
    """
    if "x-forwarded-for" in request.headers:
        return request.headers["x-forwarded-for"].split(",")[0].strip()
    return get_remote_address(request)

limiter = Limiter(
    key_func=get_real_ip,
    default_limits=["100/minute"] # Default rate limit for the entire API unless overridden
)
