import random
from ac_flask.hipchat import Addon, room_client, addon_client, sender, context
from ac_flask.hipchat.glance import Glance
from flask import Flask

addon = Addon(app=Flask(__name__),
              key="test-addon",
              name="Test AddOn",
              allow_room=True,
              scopes=['send_notification', 'view_room'])

@addon.configure_page()
def configure():
    return "hi"

@addon.webhook(event="room_enter")
def room_entered():
    room_client.send_notification('hi: %s' % sender.id)
    return '', 204

@addon.webhook(event='room_message', pattern='^/update')
def room_message():
    label = 'Update count: {}'.format(random.randint(1, 100))
    glance_data = Glance().with_label(label).with_lozenge('progress', 'current').data
    addon_client.update_room_glance('glance.key', glance_data, context['room_id'])
    return '', 204

@addon.glance(key='glance.key', name='Glance', target='webpanel.key', icon='static/glance.png')
def glance():
    label = 'Update count: {}'.format(random.randint(1, 100))
    return Glance().with_label(label).with_lozenge('progress', 'current').data

@addon.webpanel(key='webpanel.key', name='Panel')
def web_panel():
    return "This is a panel"

if __name__ == '__main__':
    addon.run(host="0.0.0.0")