import json
from ac_flask.hipchat.auth import tenant
from ac_flask.hipchat.db import redis
import requests


class RoomClient(object):

    @staticmethod
    def send_notification(message):
        token = tenant.get_token(redis)
        base_url = tenant.capabilities_url[0:tenant.capabilities_url.rfind('/')]
        resp = requests.post("%s/room/%s/notification?auth_token=%s" % (base_url, tenant.room_id, token),
                             headers={'content-type': 'application/json'},
                             data=json.dumps({"message": message}), timeout=10)
        # todo: do better
        assert resp.status_code == 204

room_client = RoomClient()