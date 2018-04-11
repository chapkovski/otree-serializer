from channels.generic.websockets import WebsocketConsumer
import json
from otree.models import Session
from serializer_ext.serializers import SessionSerializer
from rest_framework import generics
from django.urls import reverse


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
        download_link = reverse('json_export', kwargs={'session_code': self.session})
        self.send({'data': result.data,
                   'download_link': download_link})

    def send(self, content):
        self.message.reply_channel.send({'text': json.dumps(content)})
