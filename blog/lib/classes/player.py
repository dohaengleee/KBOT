from blog.lib import globals as g
from blog.lib.sub_classes.hitter_record import HitterRecord
from blog.lib.sub_classes.pitcher_record import PitcherRecord
from blog.lib.sub_classes.player_vs_team import PlayerVsTeam
from datetime import datetime, timedelta

class Player(object):
    def __init__(self, player_cd, team_code):
        self.player_code = player_cd
        self.team_code = team_code
        self.team_kor = g.team_kor_dict[self.team_code]
        self.game_id = g.GAME_ID
        self._hitter = None
        self._pitcher = None
        self.player_event = None
        self.hitter_15_days_record = None
        self.hitter_season_record = None
        self.pitcher_season_record = None
        self._name = None
        if self.player_code in g.pitcher_list:
            self.hitter_flag = False
            self.pitcher_flag = True
        else:
            self.hitter_flag = True
            self.pitcher_flag = False
        self._is_sub = False
        self._is_pinch_hitter = False
        self.inn2 = self.inn2()
        self.r = self.r()
        self.win = self.win()
        self.first = self.first()
        self.kinds_of_article = g.kinds_of_article
        self.hitter_e_article = g.hitter_e_article
        g.define_method(self, g.player_method)
        for k, v in g.VARIABLE_DICT['player_dynamic_variable'].items():
            setattr(self, k, v)

    def win(self):
        if self.pitcher_flag:
            self.win = g.pitchers_today.get(pcode=self.player_code).wls
            return self.win
        else:
            return None

    def first(self):
        if self.pitcher_flag:
            self.first = g.pitchers_today.get(pcode=self.player_code).start
            return self.first
        else:
            None

    def inn2(self):
        if self.pitcher_flag:
            self.inn2 = g.pitchers_today.get(pcode=self.player_code).inn2
            return self.inn2
        else:
            return None

    def r(self):
        if self.pitcher_flag:
            self.r = g.pitchers_today.get(pcode=self.player_code).r
            return self.r
        else:
            return None

    def is_called_game(self):
        """
        is_콜드
        :return:
        """
        return g.is_called

    def code(self):
        return self.player_code

    def name(self):
        """
        이름
        :return:
        """
        if self._name:
            return self._name

        if self.hitter_flag:

            self._name = g.hitters_today.get(pcode=self.player_code).name
        else:
            self._name = g.pitchers_today.get(pcode=self.player_code).name
        return self._name

    def team(self):
        """
        팀
        :return:
        """

        return PlayerVsTeam(self.team_code)

    def is_win(self):
        """
        is_승리
        :return:
        """
        return self.team_kor == g.WIN_TEAM

    def player_vs_team_info(self):
        """
        상대팀
        :return:
        """
        if self.team_code == g.HOME_ID:
            vs_team_code = g.AWAY_ID
        else:
            vs_team_code = g.HOME_ID
        return PlayerVsTeam(vs_team_code)

    def is_hitter(self):
        """
        is_타자
        :return:
        """
        return self.hitter_flag

    def is_pitcher(self):
        """
        is_투수
        :return:
        """
        return self.pitcher_flag

    def is_substituted(self):
        """
        is_교체
        :return:
        """
        if self._is_sub:
            return self._is_sub

        if self.hitter_flag:
            self._is_sub = g.hitters_today.get(pcode__exact=self.player_code).turn[0] != '1'
        else:
            self._is_sub = g.pitchers_today.get(pcode__exact=self.player_code).start == '1'
        return self._is_sub

    def is_pinch_hitter(self):
        """
        is_대타
        :return:
        """
        if self._is_pinch_hitter:
            return self._is_pinch_hitter

        if self.hitter_flag:
            self._is_pinch_hitter = g.entry_obj.filter(pcode__exact=self.player_code).order_by('-posi')[0].posi[1] == 'H'
        else:
            self._is_pinch_hitter = False
        return self._is_pinch_hitter

    def hitter(self):
        """
        타자
        :return:
        """
        if self.hitter_flag:
            if self._hitter is None:
                self._hitter = HitterRecord(self.player_code)
            return self._hitter

    def pitcher(self):
        """
        투수
        :return:
        """
        if self.pitcher_flag:
            if self._pitcher is None:
                self._pitcher = PitcherRecord(self.player_code)
            return self._pitcher

    def hitter_recent_5_games_in_15_days(self):
        """
        타자_15일_2군_5경기
        :return:
        """
        if self.hitter_flag and self.hitter_15_days_record is None:
            game_date = datetime.strptime(self.game_id[0:8], '%Y%m%d')
            prev_date = (game_date - timedelta(days=15)).strftime('%Y%m%d')
            game_list = g.b_models.Hitter.objects\
                .filter(gday__gte=prev_date).filter(gday__lte=game_date) \
                .values_list('gmkey', flat=True)
            if len(game_list) >= 5:
                self.hitter_15_days_record = HitterRecord(hitter_code=self.player_code, recent_games=game_list)
                return self.hitter_15_days_record
        elif self.hitter_15_days_record:
            return self.hitter_15_days_record

    def hitter_futures_this_season(self):
        """
        이번시즌_타자_2군기록
        :return:
        """
        if self.hitter_flag:
            if self.hitter_season_record is None:
                self.hitter_season_record = HitterRecord(hitter_code=self.player_code, season=True)
            return self.hitter_season_record

    def pitcher_futures_this_season(self):
        if self.pitcher_flag:
            if self.pitcher_season_record is None:
                self.pitcher_season_record = PitcherRecord(self.player_code, season=True)
            return self.pitcher_season_record