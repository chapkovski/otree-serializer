from otree.models import Session
from django.views.generic import TemplateView, View
from django.shortcuts import render
from .serializers import SessionSerializer
from rest_framework import generics
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer

import os, tempfile, zipfile
from django.http import HttpResponse
from wsgiref.util import FileWrapper


def get_full_file_name(session):
    return 'serializer_ext/temp/{}'.format(get_file_name(session))

def get_file_name(session):
    return 'session_data_{}.json'.format(session)


class DownloadJson(TemplateView):
    def get(self, request, *args, **kwargs):
        session_code = self.kwargs['session_code']
        full_filename = get_full_file_name(session_code)
        file = open(full_filename, 'r', encoding="latin-1")
        wrapper = FileWrapper(file)
        response = HttpResponse(wrapper, content_type='text/plain')
        response['Content-Length'] = os.path.getsize(full_filename)
        response['Content-Disposition'] = 'attachment; filename={}'.format(get_file_name(session_code))
        return response


class EmptyJsonView(TemplateView):
    template_name = 'serializer_ext/specific_session.html'

    def get_context_data(self, **kwargs):
        cont = super().get_context_data(**kwargs)
        cont['session'] = self.kwargs['session_code']
        return cont


# a view that returns json for specific session
class SpecificSessionDataView(generics.ListAPIView):
    serializer_class = SessionSerializer
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)

    def get_queryset(self):
        session_code = self.kwargs['session_code']
        q = Session.objects.filter(code=session_code)
        return q

    def get(self, request, *args, **kwargs):
        res = super().get(request, *args, **kwargs)
        if request.GET.get('format') == 'json':
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
