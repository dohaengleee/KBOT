# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from blog import config as cfg
if cfg.LEAGUE == 'FUTURES':
    from blog import minor_baseball_models as b_models
else:
    from blog import baseball_models as b_models


class BasePlayerSentence(models.Model):
    index = models.IntegerField(primary_key=True)
    group = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    rank = models.CharField(max_length=10)
    use = models.CharField(max_length=5, blank=True, null=True)
    condition = models.CharField(max_length=300, blank=True, null=True)
    eval = models.CharField(max_length=5, blank=True, null=True)
    sentence = models.CharField(max_length=1000, blank=True, null=True)

    objects = models.Manager()

    class Meta:
        app_label = 'lab2ai_article'
        managed = False
        db_table = 'base_player_sentence'


class BaseSentence(models.Model):
    index = models.IntegerField(primary_key=True)
    group = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    rank = models.CharField(max_length=10)
    use = models.CharField(max_length=5, blank=True, null=True)
    condition = models.CharField(max_length=300, blank=True, null=True)
    eval = models.CharField(max_length=5, blank=True, null=True)
    sentence = models.CharField(max_length=500, blank=True, null=True)

    objects = models.Manager()

    class Meta:
        app_label = 'lab2ai_article'
        managed = False
        db_table = 'base_sentence'


class BaseTeamSentence(models.Model):
    index = models.IntegerField(primary_key=True)
    group = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    rank = models.CharField(max_length=10)
    use = models.CharField(max_length=5, blank=True, null=True)
    condition = models.CharField(max_length=300, blank=True, null=True)
    eval = models.CharField(max_length=5, blank=True, null=True)
    sentence = models.CharField(max_length=500, blank=True, null=True)

    objects = models.Manager()

    class Meta:
        app_label = 'lab2ai_article'
        managed = False
        db_table = 'base_team_sentence'


class BaseTemplate(models.Model):
    index = models.IntegerField(primary_key=True)
    group = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    rank = models.CharField(max_length=10)
    use = models.CharField(max_length=5, blank=True, null=True)
    condition = models.CharField(max_length=200, blank=True, null=True)
    eval = models.CharField(max_length=5, blank=True, null=True)
    sentence = models.CharField(max_length=500, blank=True, null=True)
    template_tab = models.CharField(max_length=50, blank=True, null=True)

    objects = models.Manager()

    class Meta:
        app_label = 'lab2ai_article'
        managed = False
        db_table = 'base_template'


class CommonDynamicVariable(models.Model):
    index = models.IntegerField(primary_key=True)
    group = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    rank = models.CharField(max_length=10)
    use = models.CharField(max_length=5, blank=True, null=True)
    condition = models.CharField(max_length=200, blank=True, null=True)
    eval = models.CharField(max_length=5, blank=True, null=True)
    sentence = models.CharField(max_length=500, blank=True, null=True)

    objects = models.Manager()

    class Meta:
        app_label = 'lab2ai_article'
        managed = False
        db_table = 'common_dynamic_variable'


class GameArticles(models.Model):
    game_key = models.CharField(primary_key=True, max_length=13)
    title = models.CharField(max_length=200, blank=True, null=True)
    contents = models.CharField(max_length=1000, blank=True, null=True)
    created_time = models.DateTimeField(blank=True, null=True)

    objects = models.Manager()

    class Meta:
        app_label = 'lab2ai_article'
        managed = False
        db_table = 'game_articles'


class HitterrecordDynamicVariable(models.Model):
    index = models.IntegerField(primary_key=True)
    group = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    rank = models.CharField(max_length=10)
    use = models.CharField(max_length=5, blank=True, null=True)
    condition = models.CharField(max_length=300, blank=True, null=True)
    eval = models.CharField(max_length=5, blank=True, null=True)
    sentence = models.CharField(max_length=500, blank=True, null=True)

    objects = models.Manager()

    class Meta:
        app_label = 'lab2ai_article'
        managed = False
        db_table = 'hitterrecord_dynamic_variable'


class MethodInfo(models.Model):
    index = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    kor = models.CharField(max_length=100)
    method = models.CharField(max_length=100)

    objects = models.Manager()

    class Meta:
        app_label = 'lab2ai_article'
        managed = False
        db_table = 'method_info'


class PitcherrecordDynamicVariable(models.Model):
    index = models.IntegerField(primary_key=True)
    group = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    rank = models.CharField(max_length=10)
    use = models.CharField(max_length=5, blank=True, null=True)
    condition = models.CharField(max_length=300, blank=True, null=True)
    eval = models.CharField(max_length=5, blank=True, null=True)
    sentence = models.CharField(max_length=500, blank=True, null=True)

    objects = models.Manager()

    class Meta:
        app_label = 'lab2ai_article'
        managed = False
        db_table = 'pitcherrecord_dynamic_variable'


class PlayerDynamicVariable(models.Model):
    index = models.IntegerField(primary_key=True)
    group = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    rank = models.CharField(max_length=10)
    use = models.CharField(max_length=5, blank=True, null=True)
    condition = models.CharField(max_length=300, blank=True, null=True)
    eval = models.CharField(max_length=5, blank=True, null=True)
    sentence = models.CharField(max_length=500, blank=True, null=True)

    objects = models.Manager()

    class Meta:
        app_label = 'lab2ai_article'
        managed = False
        db_table = 'player_dynamic_variable'


class EventDynamicVariable(models.Model):
    index = models.IntegerField(primary_key=True)
    group = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    rank = models.CharField(max_length=10)
    use = models.CharField(max_length=5, blank=True, null=True)
    condition = models.CharField(max_length=300, blank=True, null=True)
    eval = models.CharField(max_length=5, blank=True, null=True)
    sentence = models.CharField(max_length=500, blank=True, null=True)

    objects = models.Manager()

    class Meta:
        app_label = 'lab2ai_article'
        managed = False
        db_table = 'event_dynamic_variable'


class BaseHalfInning(models.Model):
    index = models.IntegerField(primary_key=True)
    group = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    rank = models.CharField(max_length=10)
    use = models.CharField(max_length=5, blank=True, null=True)
    condition = models.CharField(max_length=300, blank=True, null=True)
    eval = models.CharField(max_length=5, blank=True, null=True)
    sentence = models.CharField(max_length=500, blank=True, null=True)

    objects = models.Manager()

    class Meta:
        app_label = 'lab2ai_article'
        managed = False
        db_table = 'base_half_inning'


class BasePitcher(models.Model):
    index = models.IntegerField(primary_key=True)
    group = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    rank = models.CharField(max_length=10)
    use = models.CharField(max_length=5, blank=True, null=True)
    condition = models.CharField(max_length=300, blank=True, null=True)
    eval = models.CharField(max_length=5, blank=True, null=True)
    sentence = models.CharField(max_length=500, blank=True, null=True)

    objects = models.Manager()

    class Meta:
        app_label = 'lab2ai_article'
        managed = False
        db_table = 'base_pitcher'


class PitcherSentence(models.Model):
    index = models.IntegerField(primary_key=True)
    group = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    rank = models.CharField(max_length=10)
    use = models.CharField(max_length=5, blank=True, null=True)
    condition = models.CharField(max_length=300, blank=True, null=True)
    eval = models.CharField(max_length=5, blank=True, null=True)
    sentence = models.CharField(max_length=500, blank=True, null=True)

    objects = models.Manager()

    class Meta:
        app_label = 'lab2ai_article'
        managed = False
        db_table = 'pitcher_sentence'


class PitcherPlayerSentence(models.Model):
    index = models.IntegerField(primary_key=True)
    group = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    rank = models.CharField(max_length=10)
    use = models.CharField(max_length=5, blank=True, null=True)
    condition = models.CharField(max_length=300, blank=True, null=True)
    eval = models.CharField(max_length=5, blank=True, null=True)
    sentence = models.CharField(max_length=500, blank=True, null=True)

    objects = models.Manager()

    class Meta:
        app_label = 'lab2ai_article'
        managed = False
        db_table = 'pitcher_player_sentence'


class HalfInningDynamicVariable(models.Model):
    index = models.IntegerField(primary_key=True)
    group = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    rank = models.CharField(max_length=10)
    use = models.CharField(max_length=5, blank=True, null=True)
    condition = models.CharField(max_length=300, blank=True, null=True)
    eval = models.CharField(max_length=5, blank=True, null=True)
    sentence = models.CharField(max_length=500, blank=True, null=True)

    objects = models.Manager()

    class Meta:
        app_label = 'lab2ai_article'
        managed = False
        db_table = 'half_inning_dynamic_variable'


class TeamMethod(models.Model):
    kor = models.CharField(max_length=50, blank=True, null=True)
    method = models.CharField(max_length=50, blank=True, null=True)

    objects = models.Manager()

    class Meta:
        app_label = 'lab2ai_article'
        managed = False
        db_table = 'team_method'


class Articles(models.Model):
    game_id = models.CharField(db_column='game_id', primary_key=True, max_length=13)
    le_id = models.SmallIntegerField(db_column='le_id')
    serial = models.IntegerField(db_column='serial')
    gyear = models.SmallIntegerField(db_column='gyear')
    status = models.CharField(db_column='status', max_length=10)
    title = models.CharField(db_column='title', max_length=200)
    article = models.CharField(max_length=5000, blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    highlight = models.IntegerField(db_column='highlight')
    article_type = models.IntegerField(db_column='article_type')
    objects = models.Manager()

    class Meta:
        app_label = 'lab2ai_article'
        managed = False
        db_table = 'articles'
        unique_together = (('game_id', 'le_id', 'serial'),)


class ArticleLog(models.Model):
    game_id = models.CharField(db_column='game_id', primary_key=True, max_length=13)
    counter = models.IntegerField(db_column='counter')
    le_id = models.SmallIntegerField(db_column='le_id')
    serial = models.IntegerField(db_column='serial')
    status = models.CharField(db_column='status', max_length=10)
    tab = models.CharField(db_column='tab', max_length=50)
    mode = models.CharField(db_column='mode', max_length=10)
    logs = models.CharField(db_column='logs', max_length=1000)
    created_at = models.DateTimeField(blank=True, null=True)

    objects = models.Manager()

    class Meta:
        app_label = 'lab2ai_article'
        managed = False
        db_table = 'articles_log'


class ArticlesPublished(models.Model):
    game_id = models.CharField(db_column='game_id', max_length=13)
    le_id = models.SmallIntegerField(db_column='le_id')
    serial = models.IntegerField(db_column='serial')
    gyear = models.SmallIntegerField(db_column='gyear')
    status = models.CharField(db_column='status', max_length=10)
    title = models.CharField(db_column='title', max_length=200)
    article = models.CharField(max_length=5000, blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    objects = models.Manager()

    class Meta:
        app_label = 'lab2ai_article'
        managed = False
        db_table = 'articles_published'
        unique_together = (('game_id', 'le_id', 'serial'),)


class TopPlayerHitter(models.Model):
    game_id = models.CharField(db_column='game_id', primary_key=True, max_length=13)
    gday = models.CharField(db_column='gday', max_length=8)
    pcode = models.CharField(db_column='pcode', max_length=5)
    tb = models.CharField(db_column='tb', max_length=1, blank=True)
    name = models.CharField(db_column='name', max_length=30, blank=True)
    top_point = models.FloatField(db_column='top_point', blank=True, null=True)

    objects = models.Manager()

    class Meta:
        app_label = 'lab2ai_article'
        managed = False
        db_table = 'top_players_hitter'
        unique_together = (('game_id', 'gday', 'pcode'),)


class TopPlayerPitcher(models.Model):
    game_id = models.CharField(db_column='game_id', primary_key=True, max_length=13)
    gday = models.CharField(db_column='gday', max_length=8)
    pcode = models.CharField(db_column='pcode', max_length=5)
    tb = models.CharField(db_column='tb', max_length=1, blank=True)
    name = models.CharField(db_column='name', max_length=30, blank=True)
    top_point = models.FloatField(db_column='top_point', blank=True, null=True)
   
    objects = models.Manager()

    class Meta:
        app_label = 'lab2ai_article'
        managed = False
        db_table = 'top_players_pitcher'
        unique_together = (('game_id', 'pcode'),)


class ExceptionalSentence(models.Model):
    index = models.IntegerField(primary_key=True)
    group = models.CharField(max_length=11)
    name = models.CharField(max_length=50)
    rank = models.CharField(max_length=11)
    use = models.CharField(max_length=5, blank=True, null=True)
    condition = models.CharField(max_length=200, blank=True, null=True)
    eval = models.CharField(max_length=5, blank=True, null=True)
    sentence = models.CharField(max_length=500, blank=True, null=True)

    objects = models.Manager()

    class Meta:
        app_label = 'lab2ai_article'
        managed = False
        db_table = 'exceptional_sentence'

class BaseExceptional(models.Model):
    index = models.IntegerField(primary_key=True)
    group = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    rank = models.CharField(max_length=10)
    use = models.CharField(max_length=5, blank=True, null=True)
    condition = models.CharField(max_length=300, blank=True, null=True)
    eval = models.CharField(max_length=5, blank=True, null=True)
    sentence = models.CharField(max_length=500, blank=True, null=True)

    objects = models.Manager()

    class Meta:
        app_label = 'lab2ai_article'
        managed = False
        db_table = 'base_exceptional'

class ExceptionalPlayerSentence(models.Model):
    index = models.IntegerField(primary_key=True)
    group = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    rank = models.CharField(max_length=10)
    use = models.CharField(max_length=5, blank=True, null=True)
    condition = models.CharField(max_length=300, blank=True, null=True)
    eval = models.CharField(max_length=5, blank=True, null=True)
    sentence = models.CharField(max_length=1000, blank=True, null=True)

    objects = models.Manager()

    class Meta:
        app_label = 'lab2ai_article'
        managed = False
        db_table = 'exceptional_player_sentence'

class ExceptionalTeamSentence(models.Model):
    index = models.IntegerField(primary_key=True)
    group = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    rank = models.CharField(max_length=10)
    use = models.CharField(max_length=5, blank=True, null=True)
    condition = models.CharField(max_length=300, blank=True, null=True)
    eval = models.CharField(max_length=5, blank=True, null=True)
    sentence = models.CharField(max_length=500, blank=True, null=True)

    objects = models.Manager()

    class Meta:
        app_label = 'lab2ai_article'
        managed = False
        db_table = 'exceptional_team_sentence'
