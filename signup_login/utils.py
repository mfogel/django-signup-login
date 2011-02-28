import urlparse

def redirect_to_security_check(redirect_to, request):
    """
    Short security check of redirect_to param.
    Logic taken from django.contrib.auth.login

    """
    netloc = urlparse.urlparse(redirect_to)[1]
    # Light security check -- make sure redirect_to isn't garbage.
    if not redirect_to or ' ' in redirect_to:
        return False
    # Heavier security check -- don't allow redirection to a diff host.
    elif netloc and netloc != request.get_host():
        return False
    return True
         
