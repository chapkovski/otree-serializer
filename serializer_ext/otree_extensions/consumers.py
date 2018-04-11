from channels.generic.websockets import WebsocketConsumer
import json
from otree.models import Session
from serializer_ext.serializers import SessionSerializer
from rest_framework import generics
from django.urls import reverse
from serializer_ext.views import get_full_file_name

class JsonLoader(WebsocketConsumer):
    url_pattern = (
        r'^/jsonloader' +
        '/session/(?P<session_code>[a-zA-Z0-9_-]+)' +
        '$')

    def clean_kwargs(self, kwargs):
        self.session = self.kwargs['session_code']

    def connect(self, message, **kwargs):
        self.clean_kwargs(kwargs)
        session = Session.objects.filter(code=self.session)
        result = SessionSerializer(session, many=True, )
        with open(get_full_file_name(self.session), "w+") as f:
            f.write(json.dumps(result.data))
            download_link = reverse('download_json', kwargs={'session_code': self.session})
            self.send({'data': result.data,
                       'download_link': download_link})

    def send(self,  content):
        self.message.reply_channel.send({'text': json.dumps(content)})
