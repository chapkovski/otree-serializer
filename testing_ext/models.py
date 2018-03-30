from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)

author = 'Your name here'

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'testing_ext'
    players_per_group = None
    num_rounds = 3


class Subsession(BaseSubsession):
    def creating_session(self):
        import random
        import string
        N = 10
        self.session.vars['qqqq'] = ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))
        for p in self.session.get_participants():
            p.vars['ddd'] = ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))
        for p in self.get_players():
            p.myfield = random.random()


class Group(BaseGroup):
    pass


# from django.db import models


class Player( BasePlayer):
    another_field = models.CharField(default='asdfdsa')
    myfield = models.CharField()
