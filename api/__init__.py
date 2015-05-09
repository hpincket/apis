from flask import Flask, jsonify, request, current_app, url_for
from flask_limiter import Limiter
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
            content = str(callback) + '(' + str(f(*args,**kwargs).data) + ')'
            return current_app.response_class(content, mimetype='application/javascript')
        else:
            return f(*args, **kwargs)
    return decorated_function

# initialize the app and allow an instance configuration file
app = Flask(__name__, instance_relative_config=True)
try:
	app.config.from_object('config')		# load default config file
except IOError:
	print "Could not load default config file!"

try:
	app.config.from_pyfile('config.py')		# load instance config file
except IOError:
	print "Could not load instance config file!"

# override all error handlers to be 'make_json_error'
for code in default_exceptions.iterkeys():
    app.error_handler_spec[None][code] = make_json_error

if 'MONGO_URI' in app.config:
    db = pymongo.MongoClient(app.config['MONGO_URI']).brown
elif 'MONGO_URI' in os.environ:
	db = pymongo.MongoClient(os.environ['MONGO_URI']).brown
else:
    print "The database URI's environment variable was not found."

# setup rate limiting
RATE_LIMIT = "10/second;100/minute"
limiter = Limiter(app, global_limits=["10/second", "100/minute"], key_func=lambda : request.args.get('client_id', 'missing_client'))

import meta
import dining
import wifi
import courses