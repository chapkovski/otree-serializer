from otree.models import Session
from django.views.generic import TemplateView, View
from django.shortcuts import render
from .serializers import SessionSerializer
from rest_framework import generics
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer

import os, tempfile, zipfile
from django.http import HttpResponse
from wsgiref.util import FileWrapper



class EmptyJsonView(TemplateView):
    template_name = 'serializer_ext/specific_session.html'

    def get_context_data(self, **kwargs):
        cont = super().get_context_data(**kwargs)
        cont['session'] = self.kwargs['session_code']
        return cont

from rest_framework_extensions.cache.decorators import (
cache_response
)

# a view that returns json for specific session
class SpecificSessionDataView(generics.ListAPIView):
    serializer_class = SessionSerializer
    renderer_classes = (JSONRenderer,)

    def get_renderer_context(self):
        ret = super().get_renderer_context()
        ret['indent'] = 4
        return ret

    def get_queryset(self):
        session_code = self.kwargs['session_code']
        q = Session.objects.filter(code=session_code)
        q.prefetch_related('participant_set')
        return q

    @cache_response(60 * 15)
    def get(self, request, *args, **kwargs):
        res = super().get(request, *args, **kwargs)
        filename = 'session_{}.json'.format(self.kwargs.get('session_code'))
        res['Content-Disposition'] = ('attachment; filename={0}'.format(filename))
        return res


# the view to get a list of all sessions
class AllSessionsList(TemplateView):
    template_name = 'serializer_ext/all_session_list.html'
    url_name = 'json_sessions_list'
    url_pattern = r'^sessions_list_for_json/$'
    display_name = 'Exporting data to JSON'

    def get(self, request, *args, **kwargs):
        all_sessions = Session.objects.all()
        return render(request, self.template_name, {'sessions': all_sessions})
