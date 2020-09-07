'''
Functools  normally comes installed with the default libraries
incase it isnt installed please do the needfull
'''

from functools import wraps
from flask import redirect, session

# ------------------------------------------------------------------------------------------------------------

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# ------------------------------------------------------------------------------------------------------------
