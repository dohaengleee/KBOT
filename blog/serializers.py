from rest_framework import serializers
from . import config as cfg
from . import article_models as models

if cfg.LEAGUE == 'FUTURES':
    from . import minor_baseball_models as b_models
else:
    from . import baseball_models as b_models


class ArticleLogSerializer(serializers.ModelSerializer):
    # Serializers define the API representation.
    class Meta:
        model = models.ArticleLog
        fields = '__all__'


class ArticlesSerializer(serializers.ModelSerializer):
    # Serializers define the API representation.
    class Meta:
        model = models.Articles
        fields = '__all__'


class ArticlesPublishedSerializer(serializers.ModelSerializer):
    # Serializers define the API representation.
    class Meta:
        model = models.ArticlesPublished
        fields = '__all__'


class RecordMatrixMixSerializer(serializers.ModelSerializer):
    class Meta:
        model = b_models.IeRecordMatrixMix
        fields = '__all__'


class GameListSerializer(serializers.ModelSerializer):
    class Meta:
        model = b_models.Gameinfo
        fields = ('gmkey', 'stadium', 'vteam', 'hteam')


class BaseHalfInningSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BaseHalfInning
        fields = '__all__'


class BasePlayerSentenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BasePlayerSentence
        fields = '__all__'


class BaseSentenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BaseSentence
        fields = '__all__'


class BaseTeamSentenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BaseTeamSentence
        fields = '__all__'


class BaseTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BaseTemplate
        fields = '__all__'


class CommonDynamicVariableSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CommonDynamicVariable
        fields = '__all__'


class EventDynamicVariableSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EventDynamicVariable
        fields = '__all__'


class HalfInningDynamicVariableSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.HalfInningDynamicVariable
        fields = '__all__'


class HitterrecordDynamicVariableSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.HitterrecordDynamicVariable
        fields = '__all__'


class MethodInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MethodInfo
        fields = '__all__'


class PitcherrecordDynamicVariableSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PitcherrecordDynamicVariable
        fields = '__all__'


class PlayerDynamicVariableSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PlayerDynamicVariable
        fields = '__all__'


class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = b_models.Score
        fields = '__all__'


class WESerializer(serializers.ModelSerializer):
    class Meta:
        model = b_models.IeRecordMatrixMix
        fields = ('gameid', 'inn_no', 'tb_sc', 'after_we_rt', 'wpa_rt', 'li_rt', 're_rt')


class TopPlayerHitterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TopPlayerHitter
        fields = ('game_id', 'gday', 'tb', 'name', 'pcode', 'top_point')


class TopPlayerPitcherSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TopPlayerPitcher
        fields = ('game_id', 'gday', 'tb', 'name', 'pcode', 'top_point')
