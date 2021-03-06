from otree.models import Session
from django.views.generic import TemplateView, View
from django.shortcuts import render
from .serializers import SessionSerializer
from rest_framework import generics
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
import random
import string
import os
from django.http import HttpResponse
from wsgiref.util import FileWrapper


def get_full_file_name(filename):
    return 'serializer_ext/temp/{}'.format(filename)


def get_random_code():
    return ''.join(random.choice(string.ascii_letters) for i in range(10))


def get_file_name(session_code, random_code):
    return 'session_data_{}_{}.json'.format(session_code, random_code)


def downloadable_filename(session_code):
    return 'session_data_{}.json'.format(session_code)


class DownloadJson(TemplateView):
    def get(self, request, *args, **kwargs):
        session_code =self.kwargs['session_code']
        filename = get_file_name(session_code, self.kwargs['random_code'])
        full_filename = get_full_file_name(filename)
        fn_to_download = downloadable_filename(session_code)
        file = open(full_filename, 'r', encoding="latin-1")
        wrapper = FileWrapper(file)
        response = HttpResponse(wrapper, content_type='text/plain')
        response['Content-Length'] = os.path.getsize(full_filename)
        response['Content-Disposition'] = 'attachment; filename={}'.format(fn_to_download)
        os.remove(full_filename)  # cleaning
        return response



# the view to get a list of all sessions
class AllSessionsList(TemplateView):
    template_name = 'serializer_ext/all_session_list.html'
    url_name = 'json_sessions_list'
    url_pattern = r'^sessions_list_for_json/$'
    display_name = 'Exporting data to JSON'

    def get(self, request, *args, **kwargs):
        all_sessions = Session.objects.all()
        return render(request, self.template_name, {'sessions': all_sessions})
