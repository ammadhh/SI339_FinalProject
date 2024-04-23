from coolmedia.views.db_portal import UsersPortal
import flask

def auth_user():
    user_tb = UsersPortal()

    if (not flask.request.authorization or \
        'username' not in flask.request.authorization or 'password' not in flask.request.authorization) \
        and 'username' not in flask.session:
        return ''
    elif 'username' in flask.session:
        return flask.session['username']
    else:
        username = flask.request.authorization['username']
        password = flask.request.authorization['password']
        if not user_tb.verify_password(username,password):
            return ''
        return username