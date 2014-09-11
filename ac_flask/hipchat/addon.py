import httplib
import logging

from ac_flask.hipchat import installable
from ac_flask.hipchat.auth import require_tenant
import os
from flask import jsonify, url_for, redirect


_log = logging.getLogger(__name__)


def _not_none(app, name, default):
    val = app.config.get(name, default)
    if val is not None:
        return val
    else:
        raise ValueError("Missing '{key}' configuration property".format(key=name))


class Addon(object):

    def __init__(self, app, key=None, name=None, description=None, config=None, env_prefix="AC_",
                 allow_room=True, allow_global=False, scopes=None):
        if scopes is None:
            scopes = ['send_notification']

        self.app = app
        self._init_app(app, config, env_prefix)

        self.descriptor = {
            "key": _not_none(app, 'ADDON_KEY', key),
            "name": _not_none(app, 'ADDON_NAME', name),
            "description": app.config.get('ADDON_DESCRIPTION', description) or "",
            "links": {
                "self": "{base}/addon/descriptor".format(base=app.config['BASE_URL'])
            },
            "capabilities": {
                "installable": {
                    "allowRoom": allow_room,
                    "allowGlobal": allow_global
                },
                "hipchatApiConsumer": {
                    "scopes": scopes
                }
            }
        }

        installable.init(addon=self,
                         allow_global=allow_global,
                         allow_room=allow_room)

        @self.app.route("/addon/descriptor")
        def descriptor():
            return jsonify(self.descriptor)

        self.app.route("/")(descriptor)

    @staticmethod
    def _init_app(app, config, env_prefix):
        app.config.from_object('ac_flask.hipchat.default_settings')
        if config is not None:
            app.config.from_object(config)

        if env_prefix is not None:
            env_vars = {key[len(env_prefix):]: val for key, val in os.environ.items()}
            app.config.update(env_vars)

        if app.config['DEBUG']:
            # These two lines enable debugging at httplib level (requests->urllib3->httplib)
            # You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
            # The only thing missing will be the response.body which is not logged.
            httplib.HTTPConnection.debuglevel = 1

            # You must initialize logging, otherwise you'll not see debug output.
            logging.basicConfig()
            logging.getLogger().setLevel(logging.DEBUG)
            requests_log = logging.getLogger("requests.packages.urllib3")
            requests_log.setLevel(logging.DEBUG)
            requests_log.propagate = True
        else:
            logging.basicConfig()
            logging.getLogger().setLevel(logging.WARN)

        app.events = {}

    def configure_page(self, path="/configure", **kwargs):
        self.descriptor['capabilities'].setdefault('configurable', {})['url'] = self.app.config['BASE_URL'] + path

        def inner(func):
            return self.app.route(rule=path, **kwargs)(require_tenant(func))

        return inner

    def webhook(self, event, name=None, pattern=None, path=None, **kwargs):
        if path is None:
            path = "/event/" + event

        wh = {
            "event": event,
            "url": self.app.config['BASE_URL'] + path
        }
        if name is not None:
            wh['name'] = name

        if pattern is not None:
            wh['pattern'] = pattern
        self.descriptor['capabilities'].setdefault('webhook', []).append(wh)

        def inner(func):
            return self.app.route(rule=path, methods=['POST'], **kwargs)(require_tenant(func))

        return inner

    def route(self, anonymous=False, *args, **kwargs):
        """
        Decorator for routes with defaulted required authenticated tenants
        """
        def inner(func):
            f = self.app.route(*args, **kwargs)(func)
            if not anonymous:
                f = require_tenant(f)
            return f

        return inner

    def run(self, *args, **kwargs):
        self.app.run(*args, **kwargs)
