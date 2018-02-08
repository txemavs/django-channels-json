import json
from channels import Group
from channels.routing import route, route_class, include
from channels.generic.websockets import WebsocketDemultiplexer
from channels.handler import AsgiHandler
from django.http import HttpResponse
from home.consumers import MainConsumer

class Demultiplexer(WebsocketDemultiplexer):

    consumers = {
        "main": MainConsumer,
    }


def log_send(message):
    """
    """
    text = {
        "stream":"log",
        "payload":{
            "message": message 
            }
        }
    Group("log").send({"text":json.dumps(text)})
    



def http_consumer(message):
    print "HTTP request %s" % message.content['path']
    log_send("HTTP request %s" % message.content['path'])
    Group("log").send({"text":json.dumps({'text':"HTTP Connect!"})})
    response = HttpResponse("Channels %s" % message.content['path'])
    for chunk in AsgiHandler.encode_response(response):
        message.reply_channel.send(chunk)


def websocket_connect(message, channel):
    print "Test Connect %s " % channel
    message.reply_channel.send({"accept": True})
    Group("test").add(message.reply_channel)

def websocket_receive(message, channel):
    print "Test Receive %s " % channel
    Group("test").send({
        "text": "[user] %s" % message.content['text'],
    })

def websocket_disconnect(message, channel):
    print "Test Disconnect %s " % channel
    Group("test").discard(message.reply_channel)


test_routing = [
    route("websocket.connect", websocket_connect),
    route("websocket.receive", websocket_receive),
    route("websocket.disconnect", websocket_disconnect),
]


channel_routing = [
    route("http.request",           http_consumer ),
    include(test_routing,           path=r"^/channel/test/(?P<channel>[a-zA-Z0-9_]+)/$"),
    route_class(Demultiplexer,      path=r"^/channel/$")
]