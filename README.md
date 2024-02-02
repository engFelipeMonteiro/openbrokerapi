
This repository heave a intent to be used in a isssue on github os flask-restx for study purpose.

---

The issue:

How to use flask-restx with a library that export the blueprint already with its paths, like openbrokerapi.

the code that is on [my repo](https://github.com/engFelipeMonteiro/openbrokerapi) is forked from [openbrokerapi](https://github.com/eruvanos/openbrokerapi) and served from a restx and gunicorn server.

With [requestly extension](https://app.requestly.io/) or curl I can add a arbitrary 'X-Broker-Api-Version' in the header, but the swagger page doesn't get fully rendered, see the following information 'No operations defined in spec!'.

How can I use flask-restx with this kind of architeture library?

My important code:

# webserver/web.py

<pre>
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
    return api

def run():
    return initialize_app(app)

</pre>

I can run the code with:

<pre>
 python -m gunicorn webserver.__main__:wsgi
</pre>