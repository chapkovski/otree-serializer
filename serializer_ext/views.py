from otree.models import Session, Participant
from django.views.generic import TemplateView
from django.shortcuts import render
from rest_framework import routers, serializers, viewsets
from rest_framework import generics
from otree.models.subsession import BaseSubsession
from otree.models.group import BaseGroup
from otree.models.player import BasePlayer

block_fields = ['_gbat_arrived', '_gbat_grouped', '_index_in_subsessions', '_index_in_pages', '_index_in_pages',
                '_waiting_for_ids', '_last_page_timestamp', '_last_request_timestamp', 'is_on_wait_page',
                '_current_page_name', '_current_app_name', '_round_number', '_current_form_page_url', '_max_page_index',
                '_browser_bot_finished']


class oTreeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['pk', ]


    def get_field_names(self, declared_fields, info):

        res = super().get_field_names(declared_fields, info)
        res = [r for r in res if r not in block_fields]
        return res

    def get_deeper_models(self):
        return

    def __init__(self, *args, **kwargs):

        model = kwargs.pop('model', None)
        if model:
            self.Meta.model = model
        super().__init__(*args, **kwargs)
            #     names = [f.name for f in self.Meta.model._meta.get_fields()]
            #     print('NNNNN', names)
            #     for i in names:
            #         self.Meta.fields += (i,)

    def get_fields(self):
        fields = super().get_fields()
        deeper = self.get_deeper_models()
        if deeper:
            fff = self.Meta.model._meta.get_fields()
            for f in fff:
                if f.related_model:
                    if f.related_model.__base__ is deeper['base']:
                        if deeper.get('field_name'):
                            fname = deeper['field_name']
                        else:
                            fname = f.name
                        fields[fname] = deeper['serializer'](many=True, model=f.related_model)
        return fields


class PlayerSerializer(oTreeSerializer):
    ...


class GroupSerializer(oTreeSerializer):
    ...


class ParticipantSerializer(oTreeSerializer):
    def get_deeper_models(self):
        return {
            'base': BasePlayer,
            'serializer': PlayerSerializer

        }

    class Meta:
        model = Participant


class SubSessionSerializer(oTreeSerializer):

    def get_deeper_models(self):
        return {
            'base': BaseGroup,
            'serializer': GroupSerializer,
            'field_name':'group_set',

        }


class SessionSerializer(oTreeSerializer):
    participant_set = ParticipantSerializer(many=True)

    class Meta:
        model = Session
        fields = ('id', 'is_demo', 'num_participants', 'code', 'vars',
                  'participant_set',
                  )

    def get_deeper_models(self):
        return {
            'base': BaseSubsession,
            'serializer': SubSessionSerializer

        }


class SpecificSessionDataView(generics.ListAPIView):
    url_name = 'json_export'
    url_pattern = r'^json_session/(?P<session_code>.*)/$'
    serializer_class = SessionSerializer

    def get_queryset(self):
        session_code = self.kwargs['session_code']
        q = Session.objects.filter(code=session_code)
        return q

    def get_serializer(self, *args, **kwargs):
        srl = super().get_serializer(*args, **kwargs)
        return srl


class AllSessionsList(TemplateView):
    template_name = 'serializer_ext/all_session_list.html'
    url_name = 'json_sessions_list'
    url_pattern = r'^sessions_list_for_json/$'
    display_name = 'Exporting data to JSON'

    def get(self, request, *args, **kwargs):
        all_sessions = Session.objects.all()
        return render(request, self.template_name, {'sessions': all_sessions})
