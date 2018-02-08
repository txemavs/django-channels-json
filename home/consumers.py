import json
import urlparse
import datetime
from channels import Group
from channels.generic.websockets import JsonWebsocketConsumer

def log(message):
    Group("log").send({"text":json.dumps({"stream":"log", "payload":{ 
        "app": "home",
        "message": message 
    }})})
    


class MainConsumer(JsonWebsocketConsumer):

    http_user_and_session = True
    strict_ordering = False

    method_mapping1 = {
        "json.debug": "json_debug",
    }




    def json_debug(self, message, **kwargs):
        print "JSON DEBUG ******************"


    def connection_groups(self, **kwargs):
        """ Manage Group
        """
        return ["main", "log"]

    def connect(self, message, **kwargs):
        """ No auth, but use a key parameter
        """
        multiplexer = kwargs['multiplexer']
        params = urlparse.parse_qs(message.content["query_string"])
        if b"key" in params:
            message.channel_session["key"] = params[b"key"][0].decode("utf8")
        elif message.user.is_anonymous:
            print "Main stream rejected %s" % message.user
            message.reply_channel.send({"close": True})
            return

        print "Main stream accepted %s" % message.user
        message.reply_channel.send({"accept": True})
        multiplexer.group_send("log","log",{"action":"connect"})  #g,stream,p

    def receive(self, content, **kwargs):
        """
        Called when a message is received with decoded JSON content.
        Reply with:
            Only to sender: multiplexer.send(reply_payload)
            Multicast: multiplexer.group_send(group, stream, payload) all groups

        """
        print "main receive %s = %s" % (self.message.user, content)
        multiplexer = kwargs['multiplexer']
        now = datetime.datetime.now()
        response = {
            "username": self.message.channel_session["key"] if self.message.user.is_anonymous else self.message.user.username,
            "text":content["text"],
            "date":now.strftime("%d/%m/%y"),
            "time":now.strftime("%H:%M:%S")
        }
        multiplexer.send({"response":"OK"}) 
        multiplexer.group_send("main","main", response)  
        

    def disconnect(self, message, **kwargs):
        multiplexer = kwargs['multiplexer']
        multiplexer.group_send("log","log",{
            "message":"Main disconnected %s" % message.user
        })



    # @classmethod
    # def decode_json(cls, text):
    #     return my_custom_json_decoder(text)
    #
    # @classmethod
    # def encode_json(cls, content):
    #     return my_custom_json_encoder(content)
