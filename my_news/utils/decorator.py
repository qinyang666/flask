from flask import session
import functools
from flask import redirect


def is_login(func):
    """验证是否已登录"""
    @functools.wraps(func)
    def inner( *args, **kwargs):
        if "user_id" in session:
            return func(*args, **kwargs)
        else:
            return redirect("/")
    return inner


