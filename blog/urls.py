from django.conf.urls import url, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'score', views.ScoreViewSet)
router.register(r'we', views.WEViewSet)
router.register(r'record-matrix', views.RecordMatrixMixList)
router.register(r'game-info', views.GameList)
router.register(r'article', views.ArticleViewSet)
router.register(r'log', views.LogViewSet)
router.register(r'top-player-hitter', views.TopPlayerHitter)
router.register(r'top-player-pitcher', views.TopPlayerPitcher)
router.register(r'base_half_inning', views.BaseHalfInning)
router.register(r'base_player_sentence', views.BasePlayerSentence)
router.register(r'base_sentence', views.BaseSentence)
router.register(r'base_team_sentence', views.BaseTeamSentence)
router.register(r'base_template', views.BaseTemplate)
router.register(r'common_dynamic_variable', views.CommonDynamicVariable)
router.register(r'event_dynamic_variable', views.EventDynamicVariable)
router.register(r'half_inning_dynamic_variable', views.HalfInningDynamicVariable)
router.register(r'hitterrecord_dynamic_variable', views.HitterrecordDynamicVariable)
router.register(r'method_info', views.MethodInfo)
router.register(r'pitcherrecord_dynamic_variable', views.PitcherrecordDynamicVariable)
router.register(r'player_dynamic_variable', views.PlayerDynamicVariable)


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^article/articles_create/(?P<pk>[^/.]+)', views.ArticleViewSet.as_view({'get': 'articles_create'})),
    url(r'^article/call/(?P<pk>[^/.]+)', views.ArticleViewSet.as_view({'get': 'call'})),
    url(r'^article/update/(?P<pk>[^/.]+)', views.ArticleViewSet.as_view({'get': 'update'})),
    url(r'^article/partial_update/(?P<pk>[^/.]+)', views.ArticleViewSet.as_view({'get': 'partial_update'})),
    url(r'^article/pitcher/(?P<pk>[^/.]+)', views.ArticleViewSet.as_view({'get': 'pitcher'})),
    url(r'^article/pitcher_update/(?P<pk>[^/.]+)', views.ArticleViewSet.as_view({'get': 'pitcher_update'})),
    url(r'^article/hitter_e/(?P<pk>[^/.]+)', views.ArticleViewSet.as_view({'get': 'hitter_e'})),
    url(r'^article/hitter_e_update/(?P<pk>[^/.]+)', views.ArticleViewSet.as_view({'get': 'hitter_e_update'})),
    url(r'^article/gameid', views.ArticleViewSet.as_view({'post': 'create'})),
    url(r'^article/kbo_update', views.ArticleViewSet.as_view({'post': 'kbo_update'})),
    url(r'^article/select_article', views.ArticleViewSet.as_view({'post': 'select_article'})),
    url(r'^article/select_pitcher_article', views.ArticleViewSet.as_view({'post': 'select_pitcher_article'})),
    url(r'^article/manually_update', views.ArticleViewSet.as_view({'post': 'manually_update'})),
    url(r'^article/pitcher_manually_update', views.ArticleViewSet.as_view({'post': 'pitcher_manually_update'})),
    url(r'^article/hitter_e_manually_update', views.ArticleViewSet.as_view({'post': 'hitter_e_manually_update'})),
]
