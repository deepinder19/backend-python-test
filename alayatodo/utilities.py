"""
This module contains utility/helper functions.
"""

from functools import wraps
from flask import session, redirect, url_for


def login_required(f):
    """
    Decorator function to validate login

    Attributes
    ----------
    f : <function object>
        Function to be decorated
    
    Returns
    -------
    <function object>
        Returns the wrapper function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
