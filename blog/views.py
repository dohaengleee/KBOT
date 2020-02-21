from django.shortcuts import render
from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from . import serializers
from . import config as cfg
from .controllers import GameArticles
from . import article_models as models

if cfg.LEAGUE == 'FUTURES':
    from . import minor_baseball_models as b_models
else:
    from . import baseball_models as b_models
import time
import pandas as pd
from blog.article_models import Articles


# Create your views here.
class LogViewSet(viewsets.ModelViewSet):
    queryset = models.ArticleLog.objects.all()
    serializer_class = serializers.ArticleLogSerializer

    def get_queryset(self):
        game_id = self.request.query_params.get('game_id')
        serial = self.request.query_params.get('serial')

        queryset = models.ArticleLog.objects.filter(game_id=game_id, serial=serial)
        return queryset

    # def retrieve(self, request, pk=None):
    #     queryset = models.ArticleLog.objects.filter(game_id=pk)
    #     serializer = serializers.ArticleLogSerializer(queryset, many=True)
    #     return Response(serializer.data)


class BaseHalfInning(viewsets.ModelViewSet):
    queryset = models.BaseHalfInning.objects.all()
    serializer_class = serializers.BaseHalfInningSerializer


class BasePlayerSentence(viewsets.ModelViewSet):
    queryset = models.BasePlayerSentence.objects.all()
    serializer_class = serializers.BasePlayerSentenceSerializer


class BaseSentence(viewsets.ModelViewSet):
    queryset = models.BaseSentence.objects.all()
    serializer_class = serializers.BaseSentenceSerializer


class BaseTeamSentence(viewsets.ModelViewSet):
    queryset = models.BaseTeamSentence.objects.all()
    serializer_class = serializers.BaseTeamSentenceSerializer


class BaseTemplate(viewsets.ModelViewSet):
    queryset = models.BaseTemplate.objects.all()
    serializer_class = serializers.BaseTemplateSerializer


class CommonDynamicVariable(viewsets.ModelViewSet):
    queryset = models.CommonDynamicVariable.objects.all()
    serializer_class = serializers.CommonDynamicVariableSerializer


class EventDynamicVariable(viewsets.ModelViewSet):
    queryset = models.EventDynamicVariable.objects.all()
    serializer_class = serializers.EventDynamicVariableSerializer


class HalfInningDynamicVariable(viewsets.ModelViewSet):
    queryset = models.HalfInningDynamicVariable.objects.all()
    serializer_class = serializers.HalfInningDynamicVariableSerializer


class HitterrecordDynamicVariable(viewsets.ModelViewSet):
    queryset = models.HitterrecordDynamicVariable.objects.all()
    serializer_class = serializers.HitterrecordDynamicVariableSerializer


class MethodInfo(viewsets.ModelViewSet):
    queryset = models.MethodInfo.objects.all()
    serializer_class = serializers.MethodInfoSerializer


class PitcherrecordDynamicVariable(viewsets.ModelViewSet):
    queryset = models.PitcherrecordDynamicVariable.objects.all()
    serializer_class = serializers.PitcherrecordDynamicVariableSerializer


class PlayerDynamicVariable(viewsets.ModelViewSet):
    queryset = models.PlayerDynamicVariable.objects.all()
    serializer_class = serializers.PlayerDynamicVariableSerializer


class UsingVar:
    using = False

    def __init__(self):
        global using
        using = False


class ArticleViewSet(viewsets.ViewSet):
    queryset = models.Articles.objects.all()

    def list(self, request):
        if 'gyear' in request.query_params:
            queryset = models.Articles.objects.filter(gyear=request.query_params['gyear'])
        else:
            queryset = models.Articles.objects.all()
        serializer = serializers.ArticlesSerializer(queryset, many=True)
        for data in serializer.data:
            data['contents'] = data['article'].split('\n')
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = models.Articles.objects.filter(game_id=pk, le_id=2, article_type=1).order_by('-serial')
        try:
            if queryset.count() == 0:
                #  무한 로딩이 생길 경우 삭제
                while True:
                    if UsingVar.using:
                        time.sleep(3)
                        continue
                    else:
                        break
                UsingVar.using = True
                ##############################
                game_app = GameArticles(pk)
                result = game_app.generate_article()
                if not result:
                    return Response({'ERROR': 'ERROR'})

            serializer = serializers.ArticlesSerializer(queryset[:1], many=True)
            for data in serializer.data:
                data['contents'] = data['article'].split('\n')
            UsingVar.using = False
            return Response(serializer.data)
        except Exception as e:
            UsingVar.using = False
            return Response({'ERROR': e.args[0]}, status=status.HTTP_206_PARTIAL_CONTENT)

    def update(self, request, pk=None):
        game_key_list = list(
            b_models.Gameinfo.objects.filter(gmkey__startswith='2019').order_by('gmkey').values_list('gmkey', flat=True))[:-5]
        for game_key in game_key_list:
            try:
                game_app = GameArticles(game_key)
                game_app.generate_article()
                game_app.generate_article(kinds_of_article='pitcher')
                game_app.generate_article(hitter_e_article='hitter_e')
            except Exception as e:
                return Response({'ERROR': e.args[0]}, status=status.HTTP_206_PARTIAL_CONTENT)

        return Response({'COMPLETE': True})

    def partial_update(self, request, pk=None):
        #  무한 로딩이 생길 경우 삭제
        while True:
            if UsingVar.using:
                time.sleep(3)
                continue
            else:
                break
        UsingVar.using = True
        ##############################
        game_app = GameArticles(pk)
        try:
            result = game_app.generate_article()
            if not result:
                return Response({'ERROR': 'ERROR'})

            queryset = models.Articles.objects.filter(game_id=pk, le_id=2, article_type=1).order_by('-serial')
            serializer = serializers.ArticlesSerializer(queryset[:1], many=True)
            for data in serializer.data:
                data['contents'] = data['article'].split('\n')
            UsingVar.using = False
            return Response(serializer.data)
        except Exception as e:
            UsingVar.using = False
            return Response({'ERROR': e.args[0]}, status=status.HTTP_206_PARTIAL_CONTENT)

    def articles_create(self, request, pk=None):
        for i in range(2, 4):
            try:
                #  무한 로딩이 생길 경우 삭제
                while True:
                    if UsingVar.using:
                        time.sleep(3)
                        continue
                    else:
                        break
                UsingVar.using = True
                ##############################
                game_app = GameArticles(pk)
                UsingVar.using = False
                if i == 2:
                    #  무한 로딩이 생길 경우 삭제
                    while True:
                        if UsingVar.using:
                            time.sleep(3)
                            continue
                        else:
                            break
                    UsingVar.using = True
                    ##############################
                    game_app.generate_article()
                    UsingVar.using = False
                elif i == 3:
                    #  무한 로딩이 생길 경우 삭제
                    while True:
                        if UsingVar.using:
                            time.sleep(3)
                            continue
                        else:
                            break
                    UsingVar.using = True
                    ##############################
                    game_app.generate_article(kinds_of_article='pitcher')
                    UsingVar.using = False
            except Exception as e:
                UsingVar.using = False
                return Response({'ERROR': e.args[0]}, status=status.HTTP_206_PARTIAL_CONTENT)
        return Response({'COMPLETE': True})

    def call(self, request, pk=None):
        try:
            queryset = models.Articles.objects.filter(game_id=pk, le_id=2).order_by('-serial')
            article_type = queryset[0].highlight
            selected_queryset = models.Articles.objects.filter(game_id=pk, le_id=2, article_type=article_type).order_by('-serial')
            serializer = serializers.ArticlesSerializer(selected_queryset[:1], many=True)
            for data in serializer.data:
                data['contents'] = data['article'].split('\n')
            return Response(serializer.data)
        except Exception as e:
            return Response({'ERROR': e.args[0]}, status=status.HTTP_206_PARTIAL_CONTENT)

    def pitcher(self, request, pk=None):
        queryset = models.Articles.objects.filter(game_id=pk, le_id=2, article_type=2).order_by('-serial')
        try:
            if queryset.count() == 0:
                # game_app = GameArticles(pk)
                # result = game_app.generate_article(kinds_of_article='pitcher')
                # if not result:
                return Response({'ERROR': 'ERROR'})
            else:
                serializer = serializers.ArticlesSerializer(queryset[:1], many=True)
                for data in serializer.data:
                    data['contents'] = data['article'].split('\n')
                return Response(serializer.data)
        except Exception as e:
            return Response({'ERROR': e.args[0]}, status=status.HTTP_206_PARTIAL_CONTENT)

    def pitcher_update(self, request, pk=None):
        #  무한 로딩이 생길 경우 삭제
        while True:
            if UsingVar.using:
                time.sleep(3)
                continue
            else:
                break
        UsingVar.using = True
        ##############################
        game_app = GameArticles(pk)
        try:
            result = game_app.generate_article(kinds_of_article='pitcher')
            if not result:
                return Response({'ERROR': 'ERROR'})

            queryset = models.Articles.objects.filter(game_id=pk, le_id=2, article_type=2).order_by('-serial')
            serializer = serializers.ArticlesSerializer(queryset[:1], many=True)
            for data in serializer.data:
                data['contents'] = data['article'].split('\n')
            UsingVar.using = False
            return Response(serializer.data)
        except Exception as e:
            UsingVar.using = False
            return Response({'ERROR': e.args[0]}, status=status.HTTP_206_PARTIAL_CONTENT)

    def hitter_e(self, request, pk=None):
        queryset = models.Articles.objects.filter(game_id=pk, le_id=2, article_type=3).order_by('-serial')
        try:
            if queryset.count() == 0:
                # game_app = GameArticles(pk)
                # result = game_app.generate_article(hitter_e_article='hitter_e')
                # if not result:
                return Response({'ERROR': 'ERROR'})
            else:
                serializer = serializers.ArticlesSerializer(queryset[:1], many=True)
                for data in serializer.data:
                    data['contents'] = data['article'].split('\n')
                return Response(serializer.data)
        except Exception as e:
            return Response({'ERROR': e.args[0]}, status=status.HTTP_206_PARTIAL_CONTENT)

    def hitter_e_update(self, request, pk=None):
        #  무한 로딩이 생길 경우 삭제
        while True:
            if UsingVar.using:
                time.sleep(3)
                continue
            else:
                break
        UsingVar.using = True
        ##############################
        game_app = GameArticles(pk)
        try:
            result = game_app.generate_article(hitter_e_article='hitter_e')
            if not result:
                return Response({'ERROR': 'ERROR'})

            queryset = models.Articles.objects.filter(game_id=pk, le_id=2, article_type=3).order_by('-serial')
            serializer = serializers.ArticlesSerializer(queryset[:1], many=True)
            for data in serializer.data:
                data['contents'] = data['article'].split('\n')
            UsingVar.using = False
            return Response(serializer.data)
        except Exception as e:
            UsingVar.using = False
            return Response({'ERROR': e.args[0]}, status=status.HTTP_206_PARTIAL_CONTENT)

    def kbo_update(self, request):
        pk = request.data['game_id']
        serial = request.data['serial']
        updated = request.data['article']
        updated_title = request.data['title']
        queryset = models.Articles.objects.filter(game_id=pk, serial=serial)
        serializer = serializers.ArticlesSerializer(queryset[:1], many=True)

        temp = None
        for data in serializer.data:
            data['contents'] = updated
            temp = data

        models.Articles.objects.filter(serial=temp['serial'], le_id=temp['le_id'], article_type=temp['article_type']).delete()
        article_model = Articles(
            game_id=temp["game_id"],
            le_id=temp["le_id"],
            serial=temp["serial"],
            gyear=temp["gyear"],
            status=temp["status"],
            title=updated_title,
            article=temp["contents"],
            highlight=temp["highlight"],
            article_type=temp["article_type"],
        )
        article_model.save(force_insert=True)

        return Response({'COMPLETE': True})

    def select_article(self, request):
        pk = request.data['pk']
        queryset = models.Articles.objects.filter(game_id=pk, le_id=2).exclude(article_type=3).order_by('-serial')
        for idx, row in enumerate(queryset):
            serializer = serializers.ArticlesSerializer(queryset[idx:idx+1], many=True)
            temp = None
            for data in serializer.data:
                temp = data
            models.Articles.objects.filter(serial=temp['serial'], le_id=temp['le_id'], article_type=temp['article_type']).delete()
            article_model = Articles(
                game_id=temp["game_id"],
                le_id=2,
                serial=temp["serial"],
                gyear=temp["gyear"],
                status=temp["status"],
                title=temp["title"],
                article=temp["article"],
                highlight=1,
                article_type=temp["article_type"]
            )
            article_model.save(force_insert=True)
        return Response({'COMPLETE': True})

    def select_pitcher_article(self, request):
        pk = request.data['pk']
        queryset = models.Articles.objects.filter(game_id=pk, le_id=2).exclude(article_type=3).order_by('-serial')
        for idx, row in enumerate(queryset):
            serializer = serializers.ArticlesSerializer(queryset[idx:idx+1], many=True)
            temp = None
            for data in serializer.data:
                temp = data
            models.Articles.objects.filter(serial=temp['serial'], le_id=temp['le_id'], article_type=temp['article_type']).delete()
            article_model = Articles(
                game_id=temp["game_id"],
                le_id=2,
                serial=temp["serial"],
                gyear=temp["gyear"],
                status=temp["status"],
                title=temp["title"],
                article=temp["article"],
                highlight=2,
                article_type=temp["article_type"]
            )
            article_model.save(force_insert=True)
        return Response({'COMPLETE': True})

    def manually_update(self, request):
        pk = request.data['pk']
        updated = request.data['updated']
        updated_title = request.data['updated_title']
        queryset = models.Articles.objects.filter(game_id=pk, le_id=2).exclude(article_type=2 or 3).order_by('-serial')
        serializer = serializers.ArticlesSerializer(queryset[:1], many=True)

        temp = None
        for data in serializer.data:
            data['contents'] = updated
            temp = data

        models.Articles.objects.filter(serial=temp['serial'], le_id=temp['le_id'], article_type=temp['article_type']).delete()
        article_model = Articles(
            game_id=temp["game_id"],
            le_id=2,
            serial=temp["serial"],
            gyear=temp["gyear"],
            status=temp["status"],
            title=updated_title,
            article='\n'.join(temp["contents"]),
            highlight=temp["highlight"],
            article_type=1
        )
        article_model.save(force_insert=True)

        return Response(serializer.data)

    def pitcher_manually_update(self, request):
        pk = request.data['pk']
        updated = request.data['updated']
        updated_title = request.data['updated_title']
        queryset = models.Articles.objects.filter(game_id=pk, le_id=2).exclude(article_type=1 or 3).order_by('-serial')
        serializer = serializers.ArticlesSerializer(queryset[:1], many=True)

        temp = None
        for data in serializer.data:
            data['contents'] = updated
            temp = data

        models.Articles.objects.filter(serial=temp['serial'], le_id=temp['le_id'], article_type=temp['article_type']).delete()
        article_model = Articles(
            game_id=temp["game_id"],
            le_id=2,
            serial=temp["serial"],
            gyear=temp["gyear"],
            status=temp["status"],
            title=updated_title,
            article='\n'.join(temp["contents"]),
            highlight=temp["highlight"],
            article_type=2
        )
        article_model.save(force_insert=True)

        return Response(serializer.data)

    def hitter_e_manually_update(self, request):
        pk = request.data['pk']
        updated = request.data['updated']
        updated_title = request.data['updated_title']
        queryset = models.Articles.objects.filter(game_id=pk, le_id=2).exclude(article_type=1 or 2).order_by('-serial')
        serializer = serializers.ArticlesSerializer(queryset[:1], many=True)

        temp = None
        for data in serializer.data:
            data['contents'] = updated
            temp = data

        models.Articles.objects.filter(serial=temp['serial'], le_id=temp['le_id'], article_type=temp['article_type']).delete()
        article_model = Articles(
            game_id=temp["game_id"],
            le_id=2,
            serial=temp["serial"],
            gyear=temp["gyear"],
            status=temp["status"],
            title=updated_title,
            article='\n'.join(temp["contents"]),
            highlight=temp["highlight"],
            article_type=3
        )
        article_model.save(force_insert=True)

        return Response(serializer.data)

    def create(self, request):
        print(request)
        serializer = serializers.ArticlesPublishedSerializer(data=request.data)
        # serializer = serializers.ArticlesPublishedSerializer.create(request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'COMPLETE': serializer.data})
        else:
            return Response({'ERROR': serializer.errors})
        # return Response(result.serializer.data)


class ScoreViewSet(viewsets.ModelViewSet):
    queryset = b_models.Score.objects.all()
    serializer_class = serializers.ScoreSerializer


class WEViewSet(viewsets.ViewSet):    
    queryset = b_models.IeRecordMatrixMix.objects.all()
    def list(self, request):
        queryset = b_models.IeRecordMatrixMix.objects.all()
        serializer = serializers.WESerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = b_models.IeRecordMatrixMix.objects.filter(gameid=pk)
        serializer = serializers.WESerializer(queryset, many=True)
        return Response(serializer.data)


class RecordMatrixMixList(viewsets.ViewSet):
    queryset = b_models.IeRecordMatrixMix.objects.all()

    def list(self, request):
        queryset = b_models.IeRecordMatrixMix.objects.all()
        serializer = serializers.WESerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = b_models.IeRecordMatrixMix.objects.filter(gameid=pk)
        serializer = serializers.WESerializer(queryset, many=True)
        return Response(serializer.data)


class GameList(viewsets.ViewSet):
    # queryset = b_models.Gameinfo.objects.all().order_by('-gmkey')
    queryset = b_models.Gameinfo.objects
    serializer_class = serializers.GameListSerializer

    def list(self, request):
        queryset = b_models.Gameinfo.objects.all().order_by('-gmkey')
        serializer = serializers.GameListSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = b_models.Gameinfo.objects.filter(gmkey__startswith=pk).order_by('-gmkey')
        serializer = serializers.GameListSerializer(queryset, many=True)
        return Response(serializer.data)


class TopPlayerHitter(viewsets.ViewSet):
    queryset = models.TopPlayerHitter.objects.all()

    def retrieve(self, request, pk=None):
        top_queryset = models.TopPlayerHitter.objects.filter(game_id=pk)
        hitter_queryset = b_models.Hitter.objects.filter(gmkey=pk)

        df_top = pd.DataFrame(top_queryset.values())
        df_hitter = pd.DataFrame(hitter_queryset.values()).fillna(0)

        df = df_hitter.merge(df_top[['pcode', 'top_point']]).sort_values(by='top_point', ascending=False)

        # hitter_serializer = serializers.TopPlayerHitterSerializer(hitter_queryset, many=True)
        return Response({
            'hitters': df.to_dict('records'),
        })


class TopPlayerPitcher(viewsets.ViewSet):
    queryset = models.TopPlayerPitcher.objects.all()

    def retrieve(self, request, pk=None):
        top_queryset = models.TopPlayerPitcher.objects.filter(game_id=pk)
        pitcher_queryset = b_models.Pitcher.objects.filter(gmkey=pk)

        df_top = pd.DataFrame(top_queryset.values())
        df_pitcher = pd.DataFrame(pitcher_queryset.values()).fillna(0)

        df = df_pitcher.merge(df_top[['pcode', 'top_point']]).sort_values(by='top_point', ascending=False)

        # hitter_serializer = serializers.TopPlayerHitterSerializer(hitter_queryset, many=True)
        return Response({
            'pitchers': df.to_dict('records'),
        })

# class test():
#     gameinfo = b_models.Score.objects.filter(gmkey__startswith=201809).values_list('gmkey', flat=True)
#     for game_key in gameinfo:
#         print('====================================================================================')
#         try:
#             # start_time = time.time()
#             game_key = '20180912KTSK0'
#             game_app = GameArticles(game_key)
#             print(game_app.get_article())
#             print('GameId:{0}'.format(game_key))
#         except ValueError as error:
#             print('Error: %s' % repr(error))
