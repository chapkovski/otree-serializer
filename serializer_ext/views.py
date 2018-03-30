import csv
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.text import slugify
from otree.models import Session, Participant
from django.views.generic import TemplateView
import datetime
from django.shortcuts import render

import json
from django.http import JsonResponse

from rest_framework import routers, serializers, viewsets


class VarsField(serializers.CharField):
    def to_representation(self, obj):
        print('I AM IN REPRE CALLL')
        return str(obj.vars)


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ('id', 'is_demo', 'num_participants', 'code', 'vars',)


from django.db.models import ForeignKey


def get_fk_model(model, fieldname):
    '''returns None if not foreignkey, otherswise the relevant model'''
    field_object, model, direct, m2m = model._meta.get_field(fieldname)
    if not m2m and direct and isinstance(field_object, ForeignKey):
        return field_object.rel.to
    return None


from testing_ext.models import Player


class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'id_in_group', '_payoff', 'participant', 'session', 'round_number', '_gbat_arrived',
                  '_gbat_grouped', 'myfield', 'subsession', 'group']

    def __init__(self, model=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if model:
            self.Meta.model = model
            self.Meta.fields = ('round_number', 'pk')
            names = [f.name for f in model._meta.get_fields()]
            self.Meta.fields = names


class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        depth = 1
        fields = ('id', 'code',)

    def to_representation(self, instance):
        from otree.models.player import BasePlayer
        fff = instance._meta.get_fields()
        for f in fff:
            if f.related_model:
                if f.related_model.__base__ is BasePlayer:
                    self.Meta.fields = self.Meta.fields + (f.name,)
                    setattr(self, f.name, TrackSerializer(many=True, read_only=True, model=f.related_model))

        ret = super().to_representation(instance)
        return ret


def get_export_response(request, file_prefix):
    if bool(request.GET.get('xlsx')):
        content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        file_extension = 'xlsx'
    else:
        content_type = 'text/csv'
        file_extension = 'csv'
    response = HttpResponse(
        content_type=content_type)
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(
        '{} (accessed {}).{}'.format(
            file_prefix,
            datetime.date.today().isoformat(),
            file_extension
        ))
    return response, file_extension


class SessionUserViewSet(viewsets.ModelViewSet):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer

    def __init__(self, *args, **kwargs):
        print('I AM IN INIT')
        super().__init__(*args, **kwargs)


from rest_framework import generics


class SpecificSessionDataView(generics.ListAPIView):
    url_name = 'json_export'
    url_pattern = r'^json_session/(?P<session_code>.*)/$'
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer

    def get(self, request, *args, **kwargs):
        res = super().get(request, *args, **kwargs)
        queryset = self.filter_queryset(self.get_queryset())
        ser = self.get_serializer(queryset, many=True)
        print(ser.data)
        # session_code = kwargs['session_code']
        # response, file_extension = get_export_response(
        #     request, session_code)
        # writer = csv.writer(response)
        # # q = Session.objects.all()
        # q = Participant.objects.all()
        # serializer = ParticipantSerializer(q)
        # print('AAAA', serializer.data)
        from rest_framework.renderers import JSONRenderer
        #
        json = JSONRenderer().render(ser.data, renderer_context={'indent':4})
        print('BBBB', json)
        with open("Output.txt", "w") as text_file:
            text_file.write("Purchase Amount: {0}".format(json))
        # l = [[1, 2, 3]]
        # for item in l:
        #     writer.writerow(item)
        return res


# class SpecificSessionDataView(TemplateView):
#     url_name = 'json_export'
#     url_pattern = r'^json_session/(?P<session_code>.*)/$'
#
#     def get(self, request, *args, **kwargs):
#         session_code = kwargs['session_code']
#         response, file_extension = get_export_response(
#             request, session_code)
#         writer = csv.writer(response)
#         # q = Session.objects.all()
#         q = Participant.objects.all()
#         serializer = ParticipantSerializer(q)
#         print('AAAA', serializer.data)
#         from rest_framework.renderers import JSONRenderer
#
#         json = JSONRenderer().render(serializer.data)
#         print('BBBB', json)
#         with open("Output.txt", "w") as text_file:
#             text_file.write("Purchase Amount: {0}".format(json))
#         l = [[1, 2, 3]]
#         for item in l:
#             writer.writerow(item)
#         return response


class AllSessionsList(TemplateView):
    template_name = 'serializer_ext/all_session_list.html'
    url_name = 'json_sessions_list'
    url_pattern = r'^sessions_list_for_json/$'
    display_name = 'Exporting data to JSON'

    def get(self, request, *args, **kwargs):
        all_sessions = Session.objects.all()
        return render(request, self.template_name, {'sessions': all_sessions})


class JsonExport(object):
    model = Session
    template_name = 'serializer_ext/json_export.html'
    success_url = reverse_lazy('linked_sessions_list')
    url_name = 'delete_linked_session'
    url_pattern = r'^linkedsession/(?P<pk>[a-zA-Z0-9_-]+)/delete/$'

    def render_to_response(self, context, **response_kwargs):
        # Sniff if we need to return a CSV export
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s.csv"' % slugify(context['title'])

        return response
