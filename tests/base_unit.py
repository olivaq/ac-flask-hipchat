import unittest
import flask
from flask import Flask
from flask.ext.testing import TestCase
import ac_flask.hipchat.addon

class FlaskrTestCase(TestCase):
    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app

    def test_no_such_header(self):
        try:
            app = self.create_app()
            with app.app_context():
                with app.test_request_context():
                    headers = flask.request.headers["foo"]
                    self.fail("Expected a KeyError")
        except KeyError:
            pass #expected a KeyError

    def test__get_white_listed_origin(self):
        app = self.create_app()
        addon = ac_flask.hipchat.addon.Addon(app, "KEY", "NAME")
        self.assertEqual(None, addon._get_white_listed_origin())