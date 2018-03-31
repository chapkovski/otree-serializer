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
                '_current_page_name', '_current_app_name', '_round_number', '_current_form_page_url', ]


class oTreeSerializer(serializers.ModelSerializer):
    class Meta:
        ...

    def get_field_names(self, declared_fields, info):
        res = super().get_field_names(declared_fields, info)
        res = [r for r in res if r not in block_fields]
        return res

    def __init__(self, model=None, further_models=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.further_models = further_models
        if model:
            self.Meta.model = model
            names = [f.name for f in model._meta.get_fields() if f.name not in block_fields]
            self.Meta.fields = names


class PlayerSerializer(oTreeSerializer):
    ...


class ParticipantSerializer(oTreeSerializer):
    class Meta:
        model = Participant
        ...

    def get_fields(self):
        fields = super().get_fields()
        fff = self.Meta.model._meta.get_fields()
        for f in fff:
            if f.related_model:
                if f.related_model.__base__ is BasePlayer:
                    fields[f.name] = PlayerSerializer(many=True, model=f.related_model)

        return fields


class SubSessionSerializer(oTreeSerializer):
    class Meta:
        ...

    def __init__(self, model=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if model:
            self.Meta.model = model
            names = [f.name for f in model._meta.get_fields() if not f.related_model]
            self.Meta.fields = names

    def get_fields(self):
        fields = super().get_fields()
        fff = self.Meta.model._meta.get_fields()
        for f in fff:
            if f.related_model:
                if f.related_model.__base__ is BaseGroup:
                    fields['group_set'] = SubSessionSerializer(many=True, model=f.related_model)

        return fields


class SessionSerializer(serializers.ModelSerializer):
    participant_set = ParticipantSerializer(many=True)

    class Meta:
        model = Session
        fields = ('id', 'is_demo', 'num_participants', 'code', 'vars', 'participant_set',)

    def get_fields(self):
        fields = super().get_fields()
        fff = self.Meta.model._meta.get_fields()
        for f in fff:
            if f.related_model:
                if f.related_model.__base__ is BaseSubsession:
                    fields[f.name] = SubSessionSerializer(many=True, model=f.related_model)

        return fields


class SpecificSessionDataView(generics.ListAPIView):
    url_name = 'json_export'
    url_pattern = r'^json_session/(?P<session_code>.*)/$'
    serializer_class = SessionSerializer

    def get_queryset(self):
        session_code = self.kwargs['session_code']
        q = Session.objects.filter(code=session_code)
        return q


class AllSessionsList(TemplateView):
    template_name = 'serializer_ext/all_session_list.html'
    url_name = 'json_sessions_list'
    url_pattern = r'^sessions_list_for_json/$'
    display_name = 'Exporting data to JSON'

    def get(self, request, *args, **kwargs):
        all_sessions = Session.objects.all()
        return render(request, self.template_name, {'sessions': all_sessions})
