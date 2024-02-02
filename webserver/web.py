from flask import Flask
from flask_restx import Api
import logging

import openbrokerapi.api as open_api

logger = logging.getLogger(__name__)
app = Flask(__name__)


authorizations = {
    'basic': {
        'type': 'basic',
    }
}



def initialize_app(app):
    app.config['RESTX_VALIDATE'] = True

    app.register_blueprint(get_api(logger, app), url_prefix='/open')

    return app

def get_api(logger, app):
    blueprint = open_api.get_blueprint(None, None, logger)
    api = Api(
                blueprint,
                version='0.1',
                title='title openservicebroker',
                description='',
                doc='/doc/',
                authorizations=authorizations,
                security='basic',
                url_scheme='http'
    )

    ns_exec = api.namespace('open', description='Endpoints')
    api.add_namespace(ns_exec)
    return blueprint

def run():
    return initialize_app(app)
