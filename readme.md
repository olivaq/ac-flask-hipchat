# What is this?

A Python [Flask](http://flask.pocoo.org/)-based library for building [HipChat Connect add-ons](https://www.hipchat.com/docs/apiv2/addons).  This is an early, alpha-quality release, 
but can be used to build real add-ons today.  Future versions may include backward-incompatible changes.

# Getting started

For a simple alternative to the following set up instructions, you may consider using the [Vagrant starter project](https://bitbucket.org/atlassianlabs/ac-flask-hipchat-vagrant) to get up and running quickly.

## Dependencies

In addition to Python 2.7 or later, `ac-flask-hipchat` expects Redis to be available for temporary persistence of 
authentication tokens, and MongoDB for a permanent data store.

## A first add-on

Writing basic HipChat add-ons with `ac-flask-hipchat` requires very little code to get up and running.  Here's an 
example of a simple yet complete add-on, in two files:

### web.py

```
from ac_flask.hipchat import Addon, room_client, sender
from flask import Flask

addon = Addon(app=Flask(__name__),
              key="ac-flask-hipchat-greeter",
              name="HipChat Greeter Example Add-on",
              allow_room=True,
              scopes=['send_notification'])

@addon.webhook(event="room_enter")
def room_entered():
    room_client.send_notification('hi: %s' % sender.name)
    return '', 204


if __name__ == '__main__':
    addon.run()
```

### requirements.txt

```
AC-Flask-HipChat
```

## Running the server

To run this example yourself, add these files to a new directory and run the following commands there:

```
$ pip install -r requirements.txt
$ python web.js
```

If the server started as expected, you'll see something like the following emitted:

```
--------------------------------------
Public descriptor base URL: http://localhost:5000
--------------------------------------

INFO:werkzeug: * Running on http://127.0.0.1:5000/
INFO:werkzeug: * Restarting with reloader
```

To double check that the server is running correctly, try requesting it's add-on descriptor:

```
$ curl http://localhost:5000/
```

A successful request will return a HipChat descriptor for the add-on.

## Preparing the add-on for installation

Now that you have a server running, you'll want to try it somehow.  The next step is different depending on whether  
you're going to be developing with hipchat.com or a private HipChat instance being hosted behind your corporate firewall.

### Developing with HipChat.com

The easiest way to test with hipchat.com while developing on your local machine is to use [ngrok](https://ngrok.com).
Download and install it now if you need to -- it's an amazing tool that will change the way you develop and share web applications.

Start the ngrok tunnel in another terminal window or if using the [Vagrant starter project](https://bitbucket.org/atlassianlabs/ac-flask-hipchat-vagrant),
you should already have ngrok running, and the URL should be printed to the screen when starting the VM.  For the 
purposes of this tutorial, we'll assume your domain is `https://asdf123.ngrok.com`.

While ngrok will forward both HTTP and HTTPS, for the protection of you and your HipChat group members, you should 
always use HTTPS when running your add-on on the public internet.

### Developing with a private server

To install your add-on on a private HipChat server, both the add-on server and HipChat server need to be able to connect 
to each other via HTTP or HTTPS on your local network.  Simply determine an HTTP url that your HipChat server can use to 
connect to your locally running add-on, and use that as the value of your "local base url" needed by the Installation step.

If all goes well, you won't have to change anything from the defaults, as `ac-flask-hipchat` will simply attempt to 
use the OS's hostname to build the local base url, which may already be good enough for your private network.

## Installation

### Configuring the add-on's local base url

Now, we need to tell the add-on server where it's running so that it can successfully be installed.  By default, 
it'll assume your local computer name, but for installation into HipChat, especially if using ngrok, 
you'll likely want to set it explicitly.  

You can do that by setting the `AC_BASE_URL` environment variable when you start the server:

```
$ AC_BASE_URL=https://asdf123.ngrok.com python web.py
```

When properly configured, you'll see the server report the new local base url when it starts up:

```
--------------------------------------
Public descriptor base URL: https://asdf123.ngrok.com
--------------------------------------

INFO:werkzeug: * Running on http://127.0.0.1:5000/
INFO:werkzeug: * Restarting with reloader

```

__Note__: by signing up for an ngrok account, you can specify a generally stable, custom subdomain for even easier 
iterative development.  See [ngrok](http://ngrok.com) for more information.

### Manually installing the add-on using HipChat's admin UI

To install your add-on into HipChat, you have to register your addon's descriptor.

HipChat add-ons can operate inside a room or within the entire account.  When developing, you should probably register 
your add-on inside a room you've created just for testing. Also, you can only register add-ons inside a room where you 
are an administrator.

To register your add-on descriptor, navigate to the rooms administration page at 
`https://www.hipchat.com/rooms` (or whatever url your private server is running at, 
if appropriate).  Then select one of your rooms in the list.  In the following page, select `Integrations` in the 
sidebar, and then click the "Build and install your own integration" link at the bottom of the page:

![Installation Screenshot](https://s3.amazonaws.com/uploads.hipchat.com/10804/124261/ujDtrkh5UBsKs2Y/upload.png)

Paste your descriptor url in the `Integration URL` field of the opened dialog and then click `Add integration`.  This 
will initiate the installation of your add-on for that room.

# Library Features

This library provides help with many aspects of add-on development, such as:

* Choice of programmatic HipChat add-on descriptor builder or providing a full or partial descriptor object literal
* High-level conveniences for mounting webhook handlers and configuration pages
* A REST API client with built-in OAuth2 token acquisition and refresh
* JWT authentication validation, refresh, and token generation for web UI routes (e.g. the `configurable` capability)

See `test.py` for a very simple example add-on.

### Authenticating requests from the iframe to the add-on

Add-ons typically can't use sessions, because browsers treat cookies set by the add-on as third-party cookies.
You can still make an authenticated call to an endpoint in your add-on, however:

Say there is an endpoint like this:

```
@addon.route(rule='/data')
@addon.json_output
def data():
    return {'some': 'data'}
```

You want to call this endpoint from the iframe with the full authentication context. This can be done by rendering 
a token into the iframe:

```
@addon.webpanel(key='webpanel.key', name='Panel')
def web_panel():
    token = tenant.sign_jwt(sender.id)
    return render_template('panel.html', token=token)
```

The template can then render the token into the desired location:

```
var url = '/data?signed_request={{ token }}'
```

or

```
<meta name='token' content='{{ token }}'>
```

You can also include the full context of the original request from HipChat by using:

```
token = tenant.sign_jwt(sender.id, {
    'context': dict(context)
})
```
