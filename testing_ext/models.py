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
    num_rounds = 300


class Subsession(BaseSubsession):
    somerand = models.IntegerField()

    def creating_session(self):
        import random
        import string
        N = 10
        self.somerand = random.randint(10 ** 4, 10 ** 5)
        self.session.vars['qqqq'] = ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))
        for g in self.get_groups():
            g.somegrouprand = random.random()
            g.anothergrand = random.randint(10 ** 2, 10 ** 3)
        for p in self.session.get_participants():
            p.vars['ddd'] = ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))
        for p in self.get_players():
            p.myfield = random.random()


class Group(BaseGroup):
    somegrouprand = models.FloatField()
    anothergrand = models.IntegerField()


# from django.db import models


class Player(BasePlayer):
    another_field = models.CharField(default='asdfdsa')
    myfield = models.CharField()
