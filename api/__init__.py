from flask import Flask, jsonify, request, current_app, Response, Request
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException
from functools import wraps
import pymongo
import os


def make_json_error(ex):
    ''' A wrapper for all exceptions

        All error responses that you don't specifically
        manage yourself will have application/json content
        type, and will contain JSON like this (just an example):

        { "error": "405: Method Not Allowed" }
    '''
    response = jsonify(error=[str(ex)])
    response.status_code = (ex.code
                            if isinstance(ex, HTTPException)
                            else 500)
    return response


def support_jsonp(f):
    ''' Wraps JSONified output for JSONP '''
    @wraps(f)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            content = callback.encode("utf-8") + b'(' + f(*args, **kwargs).data + b')'
            return current_app.response_class(
                content, mimetype='application/javascript')
        else:
            return f(*args, **kwargs)
    return decorated_function


# Used for changing the Flask URL values for HTTPS forwarding, solution:
# http://stackoverflow.com/questions/19840051/mutating-request-base-url-in-flask
class ProxiedRequest(Request):
        def __init__(self, environ, populate_request=True, shallow=False):
            super(Request, self).__init__(environ, populate_request, shallow)
            # Support SSL termination.
            # Mutate the host_url within Flask to use https://
            # if the SSL was terminated.
            x_forwarded_proto = self.headers.get('X-Forwarded-Proto')
            if x_forwarded_proto == 'https':
                self.url = self.url.replace('http://', 'https://')
                self.host_url = self.host_url.replace('http://', 'https://')
                self.base_url = self.base_url.replace('http://', 'https://')
                self.url_root = self.url_root.replace('http://', 'https://')

# initialize the app and allow an instance configuration file
app = Flask(__name__, instance_relative_config=True)
app.request_class = ProxiedRequest
try:
    app.config.from_object('config')		# load default config file
except IOError:
    print("Could not load default config file!")

try:
    app.config.from_pyfile('config.py')		# load instance config file
except IOError:
    print("Could not load instance config file!")

# override all error handlers to be 'make_json_error'
for code in default_exceptions:
    app.error_handler_spec[None][code] = make_json_error


if 'MONGO_URI' in app.config:
    db = pymongo.MongoClient(app.config['MONGO_URI']).brown
elif 'MONGO_URI' in os.environ:
    db = pymongo.MongoClient(os.environ['MONGO_URI']).brown
else:
    print("The database URI's environment variable was not found.")

# BASIC AUTH


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    if 'DASHBOARD_PASS' in app.config:
        correct_password = app.config['DASHBOARD_PASS']
    elif 'DASHBOARD_PASS' in os.environ:
        correct_password = os.environ['DASHBOARD_PASS']
    else:
        print("The dashboard password's environment variable was not found.")
    return username == 'admin' and password == correct_password


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

import api.meta
import api.dining
import api.wifi
import api.laundry
import api.courses

import api.meta
import api.dining
import api.wifi
import api.laundry
import api.courses

__all__ = ['api', ]
