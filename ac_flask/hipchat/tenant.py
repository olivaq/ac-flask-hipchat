from datetime import timedelta
import time
import jwt
import logging
import requests
from requests.auth import HTTPBasicAuth
from urlparse import urlparse
from .db import db, cache

_log = logging.getLogger(__name__)

ACCESS_TOKEN_CACHE = "hipchat-tokens:{oauth_id}"


def base_url(url):
    if not url:
        return None
    result = urlparse(url)
    return "{scheme}://{netloc}".format(scheme=result.scheme, netloc=result.netloc)


class Tenant(db.Model):
    __tablename__ = 'tenant'
    _id = db.Column(db.Integer, primary_key=True)
    oauth_id = db.Column(db.Text, unique=True)
    secret = db.Column(db.Text, nullable=False)
    room_id = db.Column(db.Integer, nullable=True)
    group_id = db.Column(db.Integer, nullable=True)
    group_name = db.Column(db.Text)
    homepage = db.Column(db.Text)
    token_url = db.Column(db.Text)
    capabilities_url = db.Column(db.Text)
    api_base_url = db.Column(db.Text)
    installed_from = db.Column(db.Text)

    def __init__(self, oauth_id, secret=None, homepage=None, capabilities_url=None, room_id=None, token_url=None,
                 group_id=None, group_name=None, capdoc=None):
        self.oauth_id = oauth_id
        self.secret = secret
        self.room_id = room_id
        self.group_id = group_id
        self.group_name = None if not group_name else group_name
        self.homepage = homepage or None if not capdoc else capdoc['links']['homepage']
        self.token_url = token_url or None if not capdoc else capdoc['capabilities']['oauth2Provider']['tokenUrl']
        self.capabilities_url = capabilities_url or None if not capdoc else capdoc['links']['self']
        self.api_base_url = capdoc['capabilities']['hipchatApiProvider']['url'] if capdoc \
            else self.capabilities_url[0:self.capabilities_url.rfind('/')] if self.capabilities_url else None
        self.installed_from = base_url(self.token_url)

    @cache.memoize(3600)
    def get_token(self, token_only=True, scopes=None):
        if scopes is None:
            scopes = ["send_notification"]

        def gen_token():
            resp = requests.post(self.token_url, data={"grant_type": "client_credentials", "scope": " ".join(scopes)},
                                 auth=HTTPBasicAuth(self.oauth_id, self.secret), timeout=10)
            if resp.status_code == 200:
                _log.debug("Token request response: " + resp.text)
                return resp.json()
            elif resp.status_code == 401:
                _log.error("Client %s is invalid but we weren't notified.  Uninstalling" % self.oauth_id)
                raise OauthClientInvalidError(self)
            else:
                raise Exception("Invalid token: %s" % resp.text)

        if token_only:
            data = gen_token()
            token = data['access_token']
            return token
        else:
            return gen_token()

    def sign_jwt(self, user_id, data=None):
        if data is None:
            data = {}

        now = int(time.time())
        exp = now + timedelta(hours=1).total_seconds()

        jwt_data = {"iss": self.oauth_id,
                    "iat": now,
                    "exp": exp}

        if user_id:
            jwt_data['sub'] = user_id

        data.update(jwt_data)
        return jwt.encode(data, self.secret)


class OauthClientInvalidError(Exception):
    def __init__(self, client, *args, **kwargs):
        super(OauthClientInvalidError, self).__init__(*args, **kwargs)
        self.client = client
