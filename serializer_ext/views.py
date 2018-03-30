import csv
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.text import slugify
from otree.models import Session, Participant
from django.views.generic import TemplateView
import datetime
from django.shortcuts import render
from rest_framework import routers, serializers, viewsets
from django.db.models import ForeignKey
from testing_ext.models import Player
from rest_framework import generics
from otree.models.subsession import BaseSubsession
from otree.models.group import BaseGroup

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        ...

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
                    setattr(self, f.name, PlayerSerializer(many=True, read_only=True, model=f.related_model))

        ret = super().to_representation(instance)
        return ret


class SubSessionSerializer(serializers.ModelSerializer):
    class Meta:
        ...

    def __init__(self, model, *args, **kwargs):
        self.Meta.model = model
        self.Meta.fields = ('id', 'round_number')
        super().__init__(*args, **kwargs)


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

    # testing_ext_subsession =
    class Meta:
        model = Session
        fields = ('id', 'is_demo', 'num_participants', 'code', 'vars', 'participant_set',)

    def __init__(self, instance, *args, **kwargs):

        # print()
        # for f in self.Meta.model._meta.get_fields():
        #     if f.name == 'testing_ext_subsession':
        #         setattr(self.__class__, f.name, SubSessionSerializer(many=True, model=Subsession))
        super().__init__(instance, *args, **kwargs)

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

    def get(self, request, *args, **kwargs):
        res = super().get(request, *args, **kwargs)
        return res


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
