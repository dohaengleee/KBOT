from blog.lib import globals as g
import pandas as pd
import datetime
from blog.baseball_models import PlayerInjury
from blog.baseball_models import Pitcher as t_Pitcher
from blog.lib.classes.pitcher import PitcherVariables


class PitcherRecord(object):
    def __init__(self, pitcher_code, season=None):
        # if g.kinds_of_article == 'pitcher':
        #     self.pitcher_code = g.top_pitcher_cd
        # else:
        self.pitcher_code = pitcher_code
        self.season = season
        self.game_id = g.GAME_ID
        self.team_kor_dict = g.team_kor_dict
        self.team_kor_dict['PL'] = '경찰'
        self.today_record = None
        self.df_season_record = None
        self.record = None
        self.pitcher_take_plate_event = None
        # region [Today record]
        self.today_is_first = False
        self.today_is_win = False
        self.today_is_save = False
        self.today_is_loss = False
        self.today_is_sho = False
        self.today_is_cg = False
        self.today_is_hold = False
        self.today_er = 0
        self.today_r = 0
        self.today_inn2 = 0
        self.today_bb = 0
        self.today_kk = 0
        self.today_hit = 0
        self.today_hr = 0
        self.today_is_closing = 0
        self.today_num_of_inning = 0
        # endregion [Today record]
        # region [Season record]
        self.season_game_num = 0
        self.season_hold = 0
        self.season_er = 0
        self.season_r = 0
        self.season_inn2 = 0
        self.season_bb = 0
        self.season_kk = 0
        self.season_hit = 0
        self.pv = PitcherVariables(self.pitcher_code)
        # endregion [Season record]

        self.set_pitcher_record()
        g.define_method(self, g.pitcher_method)
        for k, v in g.VARIABLE_DICT['pitcherrecord_dynamic_variable'].items():
            setattr(self, k, v)

    def set_pitcher_record(self):
        _today_record = g.pitchers_today.filter(pcode__exact=self.pitcher_code)
        self.today_record = _today_record[0]
        season_record = g.b_models.Pitcher.objects \
            .filter(pcode=self.pitcher_code) \
            .filter(gmkey__startswith=g.GAME_YEAR) \
            .filter(gday__lte=g.GAME_DATE).order_by('-gday')
        self.df_season_record = pd.DataFrame(list(season_record.values()))
        # region [Today record]
        self.today_is_first = self.today_record.start == '1'
        self.today_is_closing = self.today_record.quit == '1'
        self.today_is_win = self.today_record.wls == 'W'
        self.today_is_save = self.today_record.wls == 'S'
        self.today_is_loss = self.today_record.wls == 'L'
        self.today_is_sho = self.today_record.sho > 0
        self.today_is_cg = self.today_record.cg > 0
        self.today_is_hold = self.today_record.hold == 1
        self.today_er = self.today_record.er
        self.today_r = self.today_record.r
        self.today_inn2 = int(self.today_record.inn2)
        self.today_num_of_inning = int(self.today_inn2 / 3) if int(self.today_inn2 / 3) > 0 else 1
        self.today_bb = self.today_record.bb
        self.today_kk = self.today_record.kk
        self.today_hit = self.today_record.hit
        self.today_hr = self.today_record.hr
        # endregion [Today record]
        # region [Season record]
        self.season_game_num = self.df_season_record.shape[0]
        self.season_hold = int(self.df_season_record['hold'].sum())
        self.season_er = int(self.df_season_record['er'].sum())
        self.season_r = int(self.df_season_record['r'].sum())
        self.season_inn2 = int(int(self.df_season_record['inn2'].sum()) / 3) if int(int(self.df_season_record['inn2'].sum()) / 3) > 0 else 1
        self.season_bb = int(self.df_season_record['bb'].sum())
        self.season_kk = int(self.df_season_record['kk'].sum())
        self.season_hit = int(self.df_season_record['hit'].sum())
        # endregion [Season record]
        if self.season:
            self.record = self.df_season_record

    def name(self):
        return self.today_record.name

    def is_enough(self):
        """
        is_충분
        :return:
        """
        inn = self.today_num_of_inning
        r = inn / (self.how_many_games_in(g.LEAGUE) * 3.1)
        is_enough = self.season_game_num >= 3 and inn > 5 and ((inn > 20) or (r > 0.1))
        return is_enough

    def how_many_games_in(self, league):
        if league == 'FUTURES':
            result = self.season_game_num / 6
        else:
            result = self.season_game_num / 5
        return result

    def is_win(self):
        """
        is_승리투수
        :return:
        """
        return self.today_is_win

    def is_lose(self):
        """
        is_패전투수
        :return:
        """
        return self.today_is_loss

    def is_save(self):
        """
        is_세이브
        :return:
        """
        return self.today_is_save

    def is_first_pitcher(self):
        """
        is_선발
        :return:
        """
        return self.today_is_first

    def is_middle_pitcher(self):
        """
        is_중간
        :return:
        """
        return self.today_is_first == self.today_is_closing

    def is_closing_pitcher(self):
        """
        is_마무리
        :return:
        """
        return self.today_is_closing

    def is_perfect_game(self):
        """
        is_퍼펙트
        :return:
        """
        return self.today_is_sho and self.today_is_win and (self.today_hit + self.today_r + self.today_bb) == 0


    def is_no_hit_no_run(self):
        """
        is_노히트노런
        :return:
        """
        return self.today_is_sho and self.today_is_win and (self.today_hit + self.today_r) == 0

    def is_called_game(self):
        """
        콜드?
        :return:
        """
        if g.game_score.number_9t == -1:
            g.is_called = True
            result = True
        else:
            result = False
        return result

    def is_sho(self):
        """
        is_완봉
        :return:
        """
        return self.today_record.sho > 0

    def is_sho_win(self):
        """
        is_완봉승
        :return:
        """
        return self.today_record.sho > 0 and self.today_is_win

    def is_cg(self):
        """
        is_완투
        :return:
        """
        return self.today_record.cg > 0

    def is_cg_win(self):
        """
        is_완투승
        :return:
        """
        return self.today_record.cg > 0 and self.today_is_win

    def is_cg_lose(self):
        """
        is_완투패
        :return:
        """
        return self.today_record.cg > 0 and self.today_is_loss

    def is_qs_plus(self):
        """
        is_qs_plus
        :return:
        """
        return (self.today_inn2 / 3) >= 7 and self.today_er <= 3

    def is_qs(self):
        """
        is_qs
        :return:
        """
        return (self.today_inn2 / 3) >= 6 and self.today_er <= 3

    def is_hold(self):
        """
        is_홀드
        :return:
        """
        return self.today_is_hold

    def er(self):
        """
        자책점
        :return:
        """
        return self.today_er

    def r(self):
        """
        실점
        :return:
        """
        return self.today_r

    def inn2(self):
        """
        이닝수
        :return:
        """
        return self.today_inn2

    def inn_string(self):
        """
        이닝
        :return:
        """
        num_str = '' if int(self.today_inn2 / 3) == 0 else int(self.today_inn2 / 3)

        if self.today_inn2 % 3 == 1:
            decimal_str = '⅓'
        elif self.today_inn2 % 3 == 2:
            decimal_str = '⅔'
        else:
            decimal_str = ''

        if num_str and decimal_str:
            result = '%s %s' % (num_str, decimal_str)
        elif num_str:
            result = '%s' % num_str
        else:
            result = '%s' % decimal_str

        return result

    def bb(self):
        """
        볼넷수
        :return:
        """
        return self.today_bb

    def kk(self):
        """
        탈삼진수
        :return:
        """
        return self.today_kk

    def hit(self):
        """
        피안타수
        :return:
        """
        return self.today_hit

    def hr(self):
        """
        피홈런수
        :return:
        """
        return self.today_hr

    def game_num(self):
        """
        경기수
        :return:
        """
        return self.season_game_num

    def era(self):
        """
        평균자책점
        :return:
        """
        if self.today_num_of_inning > 0:
            return round(self.today_er * 9 / self.today_num_of_inning, 3)
        else:
            return 0

    def pitcher_take_the_plate_event(self):
        """
        등판
        :return:
        """
        return list(filter(lambda x: x.cause_event.pitcher == self.pitcher_code, g.EVENT_LIST))[0]

    def season_win(self):
        """
        승수
        :return:
        """
        return len(self.df_season_record[self.df_season_record['wls'] == 'W'].index)

    def season_lose(self):
        """
        패수
        :return:
        """
        return len(self.df_season_record[self.df_season_record['wls'] == 'L'].index)

    def season_save(self):
        """
        세이브수
        :return:
        """
        return len(self.df_season_record[self.df_season_record['wls'] == 'S'].index)

    def season_hold(self):
        """
        홀드수
        :return:
        """
        return self.season_hold

    def win_consecutive(self):
        """
        연승
        :return:
        """
        counter = 0
        last_game_date = g.GAME_DATE
        vs_team_code = ''
        for i, row in self.df_season_record.iterrows():
            if row['wls'] == 'L':
                break
            elif row['wls'] == 'W':
                counter += 1
                last_game_date = row['gday']
                vs_team_code = row['gmkey'][10:12] if row['tb'] == 'T' else row['gmkey'][8:10]
            else:
                continue

        _record = NamedVariable()
        if counter <= 1:
            setattr(_record, '존재', False)
            setattr(_record, '경기수', counter)
            return _record

        days_kor, days = g.get_diff_days(game_date=g.GAME_DATE, last_record_date=last_game_date)
        if counter > 1:
            vs_team_kor = self.team_kor_dict[vs_team_code]
            setattr(_record, '존재', True)
            setattr(_record, '날짜', days_kor)
            setattr(_record, '일수', days)
            setattr(_record, '상대팀', vs_team_kor)
            setattr(_record, '경기수', counter)
        else:
            setattr(_record, '존재', False)
            setattr(_record, '경기수', counter)

        return _record

    def n_game_w_consecutive(self):
        """
        n경기_연속_승리
        :return:
        """
        _wls = 'W'
        counter = 0
        last_game_date = g.GAME_DATE
        vs_team_code = ''
        for i, row in self.df_season_record.iterrows():
            if row['wls'] == _wls:
                counter += 1
                last_game_date = row['gday']
                vs_team_code = row['gmkey'][10:12] if row['tb'] == 'T' else row['gmkey'][8:10]
            else:
                break

        _record = NamedVariable()
        if counter <= 1:
            setattr(_record, '존재', False)
            setattr(_record, '경기수', counter)
            return _record

        days_kor, days = g.get_diff_days(game_date=g.GAME_DATE, last_record_date=last_game_date)
        if counter > 1 and days < 30:
            vs_team_kor = self.team_kor_dict[vs_team_code]
            setattr(_record, '존재', True)
            setattr(_record, '날짜', days_kor)
            setattr(_record, '일수', days)
            setattr(_record, '상대팀', vs_team_kor)
            setattr(_record, '경기수', counter)
        else:
            setattr(_record, '존재', False)
            setattr(_record, '경기수', counter)

        return _record

    def n_game_sv_consecutive(self):
        """
        n경기_연속_세이브
        :return:
        """
        _wls = 'S'
        counter = 0
        last_game_date = g.GAME_DATE
        vs_team_code = ''
        for i, row in self.df_season_record.iterrows():
            if row['wls'] == _wls:
                counter += 1
                last_game_date = row['gday']
                vs_team_code = row['gmkey'][10:12] if row['tb'] == 'T' else row['gmkey'][8:10]
            else:
                break

        _record = NamedVariable()
        if counter <= 1:
            setattr(_record, '존재', False)
            setattr(_record, '경기수', counter)
            return _record

        days_kor, days = g.get_diff_days(game_date=g.GAME_DATE, last_record_date=last_game_date)
        if counter > 1 and days < 30:
            vs_team_kor = self.team_kor_dict[vs_team_code]
            setattr(_record, '존재', True)
            setattr(_record, '날짜', days_kor)
            setattr(_record, '일수', days)
            setattr(_record, '상대팀', vs_team_kor)
            setattr(_record, '경기수', counter)
        else:
            setattr(_record, '존재', False)
            setattr(_record, '경기수', counter)

        return _record

    def n_game_hold_consecutive(self):
        """
        n경기_연속_홀드
        :return:
        """
        counter = 0
        last_game_date = g.GAME_DATE
        vs_team_code = ''
        for i, row in self.df_season_record.iterrows():
            if row['hold'] > 0:
                counter += 1
                last_game_date = row['gday']
                vs_team_code = row['gmkey'][10:12] if row['tb'] == 'T' else row['gmkey'][8:10]
            else:
                break

        _record = NamedVariable()
        if counter <= 1:
            setattr(_record, '존재', False)
            setattr(_record, '경기수', counter)
            return _record

        days_kor, days = g.get_diff_days(game_date=g.GAME_DATE, last_record_date=last_game_date)
        if counter > 1 and days < 30:
            vs_team_kor = self.team_kor_dict[vs_team_code]
            setattr(_record, '존재', True)
            setattr(_record, '날짜', days_kor)
            setattr(_record, '일수', days)
            setattr(_record, '상대팀', vs_team_kor)
            setattr(_record, '경기수', counter)
        else:
            setattr(_record, '존재', False)
            setattr(_record, '경기수', counter)

        return _record

    def n_game_w_last(self):
        """
        n경기_만에_승리
        :return:
        """
        _wls = 'W'
        counter = 0
        last_game_date = g.GAME_DATE
        vs_team_code = ''
        for i, row in self.df_season_record.iterrows():
            if i == 0 and row['wls'] == _wls:
                counter += 1
            elif i > 0 and row['wls'] != _wls:
                counter += 1
                last_game_date = row['gday']
                vs_team_code = row['gmkey'][10:12] if row['tb'] == 'T' else row['gmkey'][8:10]
            else:
                break

        _record = NamedVariable()
        if counter <= 1:
            setattr(_record, '존재', False)
            setattr(_record, '경기수', counter)
            return _record

        days_kor, days = g.get_diff_days(game_date=g.GAME_DATE, last_record_date=last_game_date)
        if counter > 1 and days < 30:
            vs_team_kor = self.team_kor_dict[vs_team_code]
            setattr(_record, '존재', True)
            setattr(_record, '날짜', days_kor)
            setattr(_record, '일수', days)
            setattr(_record, '상대팀', vs_team_kor)
            setattr(_record, '경기수', counter)
        else:
            setattr(_record, '존재', False)
            setattr(_record, '경기수', counter)

        return _record

    def n_game_sv_last(self):
        """
        n경기_만에_세이브
        :return:
        """
        _wls = 'S'
        counter = 0
        last_game_date = g.GAME_DATE
        vs_team_code = ''
        for i, row in self.df_season_record.iterrows():
            if i == 0 and row['wls'] == _wls:
                counter += 1
            elif i > 0 and row['wls'] != _wls:
                counter += 1
                last_game_date = row['gday']
                vs_team_code = row['gmkey'][10:12] if row['tb'] == 'T' else row['gmkey'][8:10]
            else:
                break

        _record = NamedVariable()
        if counter <= 1:
            setattr(_record, '존재', False)
            setattr(_record, '경기수', counter)
            return _record

        days_kor, days = g.get_diff_days(game_date=g.GAME_DATE, last_record_date=last_game_date)
        if counter > 1 and days < 30:
            vs_team_kor = self.team_kor_dict[vs_team_code]
            setattr(_record, '존재', True)
            setattr(_record, '날짜', days_kor)
            setattr(_record, '일수', days)
            setattr(_record, '상대팀', vs_team_kor)
            setattr(_record, '경기수', counter)
        else:
            setattr(_record, '존재', False)
            setattr(_record, '경기수', counter)

        return _record

    def n_game_hold_last(self):
        """
        n경기_만에_홀드
        :return:
        """
        counter = 0
        last_game_date = g.GAME_DATE
        vs_team_code = ''
        for i, row in self.df_season_record.iterrows():
            if i == 0 and row['hold'] > 0:
                counter += 1
            elif i > 0 and row['wls'] == 0:
                counter += 1
                last_game_date = row['gday']
                vs_team_code = row['gmkey'][10:12] if row['tb'] == 'T' else row['gmkey'][8:10]
            else:
                break

        _record = NamedVariable()
        if counter <= 1:
            setattr(_record, '존재', False)
            setattr(_record, '경기수', counter)
            return _record

        days_kor, days = g.get_diff_days(game_date=g.GAME_DATE, last_record_date=last_game_date)
        if counter > 1 and days < 30:
            vs_team_kor = self.team_kor_dict[vs_team_code]
            setattr(_record, '존재', True)
            setattr(_record, '날짜', days_kor)
            setattr(_record, '일수', days)
            setattr(_record, '상대팀', vs_team_kor)
            setattr(_record, '경기수', counter)
        else:
            setattr(_record, '존재', False)
            setattr(_record, '경기수', counter)

        return _record

    def pitcher_last_start_game(self):
        """
        최근선발등판
        :return:
        """
        _record = NamedVariable()
        setattr(_record, '존재', False)

        pitcher_start = g.b_models.Pitcher.objects.filter(gday__lte=g.GAME_DATE, pcode=self.pitcher_code, start='1').exclude(pcode__in=['T', 'B']).order_by('-gday')
        if pitcher_start.count() > 1:
            last_game = pitcher_start[1]
            last_gday = last_game.gday
            kor_last_gday = last_gday[:4] + '년 ' + last_gday[4:6].lstrip('0') + '월 ' + last_gday[6:].lstrip('0') + '일'
            current_gday = pitcher_start[0].gday
            how_long = (datetime.datetime(int(current_gday[:4]), int(current_gday[4:6]), int(current_gday[6:])) - datetime.datetime(int(last_gday[:4]), int(last_gday[4:6]), int(last_gday[6:]))).days
            vs_team_code = last_game.gmkey[10:12] if last_game.tb == 'T' else last_game.gmkey[8:10]
            vs_team_kor = self.team_kor_dict[vs_team_code]

            setattr(_record, '존재', True)
            setattr(_record, '날짜', kor_last_gday)
            setattr(_record, '상대팀', vs_team_kor)
            setattr(_record, '일자', how_long)

        return _record


    def pitcher_last_wsh_game(self):
        """
        최근승세홀
        :return:
        """
        _record = NamedVariable()
        setattr(_record, '존재', False)

        var = ''
        kor_var = ''

        if self.today_is_hold:
            pitcher_start = g.b_models.Pitcher.objects.filter(gday__lte=g.GAME_DATE, pcode=self.pitcher_code, hold=1).exclude(pcode__in=['T', 'B']).order_by('-gmkey')
            kor_var = '홀드'
        else:
            if self.today_is_win:
                var = 'W'
                kor_var = '승리'
            elif self.today_is_save:
                var = 'S'
                kor_var = '세이브'

            pitcher_start = g.b_models.Pitcher.objects.filter(gday__lte=g.GAME_DATE, pcode=self.pitcher_code, wls=var).exclude(pcode__in=['T', 'B']).order_by('-gmkey')

        if pitcher_start.count() > 1:

            last_game = pitcher_start[1]
            last_gday = last_game.gday
            kor_last_gday = last_gday[:4] + '년 ' + last_gday[4:6].lstrip('0') + '월 ' + last_gday[6:].lstrip('0') + '일'
            current_gday = pitcher_start[0].gday
            how_long = (datetime.datetime(int(current_gday[:4]), int(current_gday[4:6]), int(current_gday[6:])) - datetime.datetime(int(last_gday[:4]), int(last_gday[4:6]), int(last_gday[6:]))).days
            vs_team_code = last_game.gmkey[10:12] if last_game.tb == 'T' else last_game.gmkey[8:10]
            vs_team_kor = self.team_kor_dict[vs_team_code]

            setattr(_record, '존재', True)
            setattr(_record, '승세홀', kor_var)
            setattr(_record, '날짜', kor_last_gday)
            setattr(_record, '상대팀', vs_team_kor)
            setattr(_record, '일자', how_long)

        return _record


    def two_digit_kk(self):
        """
        두자릿수탈삼진
        :return:
        """

        list = ['첫', '두번째', '세번째', '네번째', '다섯번째', '여섯번째', '일곱번째', '여덟번째', '아홉번째', '열번째',
                '열한번째', '열두번째', '열세번째', '열네번째', '열다섯번째', '열여섯번째', '열일곱번째', '열여덟번째',
                '열아홉번째', '스무번째']

        _record = NamedVariable()
        setattr(_record, '존재', False)

        two_digit_kk_pitchers = g.b_models.Pitcher.objects.filter(gday__lte=g.GAME_DATE, gday__startswith=g.GAME_YEAR, kk__gte=10).exclude(pcode__in=['T', 'B'])
        if two_digit_kk_pitchers.count() > 0:
            th = list[len(two_digit_kk_pitchers)-1]
            setattr(_record, '존재', True)
            setattr(_record, '번째', th)

        return _record


    def inn_kk_records(self):
        """
        이닝탈삼진
        :return:
        """
        team_code = self.game_id[8:10] if self.today_record.tb == 'T' else self.game_id[10:12]

        _record = NamedVariable()
        setattr(_record, '존재', False)

        inn_kk_records = g.b_models.Pitcher.objects.filter(gday__lte=g.GAME_DATE, inn2__gte=24, kk__gte=9).exclude(pcode__in=['T', 'B']).extra(
            where=[
                "((substring(gmkey, 9, 2) = '{0}' and tb = 'T') or (substring(gmkey, 11, 2) = '{0}' and tb = 'B'))".format(
                    team_code),
            ]
        ).order_by('-gday')
        if inn_kk_records.count() == 1:
            setattr(_record, '존재', True)
            setattr(_record, '처음', True)


        if inn_kk_records.count() > 1:
            last_game = inn_kk_records[1]
            last_game_pitcher = last_game.name
            last_game_kk = last_game.kk
            last_game_inn = int(last_game.inn2 / 3) if int(last_game.inn2 / 3) > 0 else 1
            last_gday = last_game.gday
            current_gday = inn_kk_records[0].gday
            how_long = (datetime.datetime(int(current_gday[:4]), int(current_gday[4:6]), int(current_gday[6:])) - datetime.datetime(int(last_gday[:4]), int(last_gday[4:6]), int(last_gday[6:]))).days
            kor_last_gday = last_gday[:4] + '년 ' + last_gday[4:6].lstrip('0') + '월 ' + last_gday[6:].lstrip('0') + '일'
            vs_team_code = last_game.gmkey[10:12] if last_game.tb == 'T' else last_game.gmkey[8:10]
            team_code = last_game.gmkey[10:12] if last_game.tb == 'B' else last_game.gmkey[8:10]
            vs_team_kor = self.team_kor_dict[vs_team_code]
            team_kor = self.team_kor_dict[team_code]

            setattr(_record, '존재', True)
            setattr(_record, '처음', False)
            setattr(_record, '날짜', kor_last_gday)
            setattr(_record, '상대팀', vs_team_kor)
            setattr(_record, '팀', team_kor)
            setattr(_record, '일자', how_long)
            setattr(_record, '지난투수', last_game_pitcher)
            setattr(_record, '이닝수', last_game_inn)
            setattr(_record, '탈삼진수', last_game_kk)

        return _record

    def first_game_after_injury(self):
        """
        부상_후_첫등판
        :return:
        """
        gday = self.game_id[:8]
        _record = NamedVariable()
        setattr(_record, '존재', False)

        player_injury = PlayerInjury.objects.filter(pcode__exact=self.pitcher_code).order_by('-injury_start_dt')
        if player_injury.count() > 0:
            try:
                entry_off_day = list(filter(lambda x: len(x.entry_off_dt) > 0, player_injury))[0].entry_off_dt
                major_last_game = t_Pitcher.objects.filter(pcode__exact=self.pitcher_code).order_by('-gday')[0]
                if self.today_is_first:
                    start = 1
                else:
                    start = None
                minor_last_game = g.b_models.Pitcher.objects.filter(pcode__exact=self.pitcher_code, gday__lt=gday, start__exact=start).order_by('-gday')[0]
                if entry_off_day >= major_last_game.gday:
                    major_vs_team_code = major_last_game.gmkey[10:12] if major_last_game.tb == 'T' else major_last_game.gmkey[8:10]
                    kor_major_gday = major_last_game.gday[:4] + '년 ' + major_last_game.gday[4:6].lstrip('0') + '월 ' + major_last_game.gday[6:].lstrip('0') + '일'
                    major_vs_team_kor = self.team_kor_dict[major_vs_team_code]
                    if entry_off_day >= minor_last_game.gday:
                        minor_vs_team_code = minor_last_game.gmkey[10:12] if minor_last_game.tb == 'T' else minor_last_game.gmkey[8:10]
                        kor_minor_gday = minor_last_game.gday[:4] + '년 ' + minor_last_game.gday[4:6].lstrip('0') + '월 ' + minor_last_game.gday[6:].lstrip('0') + '일'
                        minor_vs_team_kor = self.team_kor_dict[minor_vs_team_code]
                        how_long = (datetime.datetime(int(gday[:4]), int(gday[4:6]), int(gday[6:])) - datetime.datetime(int(major_last_game.gday[:4]), int(major_last_game.gday[4:6]), int(major_last_game.gday[6:]))).days
                        setattr(_record, '존재', True)
                        setattr(_record, '휴식일자', how_long)
                        setattr(_record, '1군경기_날짜', kor_major_gday)
                        setattr(_record, '1군경기_상대팀', major_vs_team_kor)
                        setattr(_record, '퓨쳐스경기_날짜', kor_minor_gday)
                        setattr(_record, '퓨쳐스경기_상대팀', minor_vs_team_kor)
                    else:
                        setattr(_record, '존재', False)
                else:
                    setattr(_record, '존재', False)

                return _record

            except IndexError:
                setattr(_record, '존재', False)
                return _record

    def pitcher_rank_text(self):
        """
        투수_랭킹그래프
        :return:
        """

        try:
            _record = NamedVariable()
            if g.graph_exist:
                g_type = g.graph_type

                if g_type == 'rank':
                    setattr(_record, '존재', True)
                    setattr(_record, '이름', g.r_name)
                    setattr(_record, '스탯', g.r_stat_name)
                    setattr(_record, '랭크', g.r_target_ranking)
                    setattr(_record, 'is_공동', g.r_is_joint)
                    setattr(_record, '리그', g.r_league)
                    setattr(_record, '스코어', g.r_values)
                    return _record
            else:
                setattr(_record, '존재', False)
                return _record
        except:
            print('pitcher_record pitcher_rank_text 경기수 부족')
            pass

    def pitcher_stat_text(self):
        """
        투수_스탯그래프
        :return:
        """
        try:
            var = NamedVariable()
            if g.graph_exist:
                g_type = g.graph_type
                if g_type == 'stat':
                    inn = g.s_inn
                    if inn[-1] == str(3):
                        inn = inn[-len(inn):-2] + ' ⅓'
                    elif inn[-1] == str(6):
                        inn = inn[-len(inn):-2] + ' ⅔'
                    else:
                        inn = str(int(float(inn)))
                    setattr(var, '존재', g.s_is_exist)
                    setattr(var, '이름', g.s_name)
                    setattr(var, '스탯', g.s_stat_name)
                    setattr(var, '경기수', g.s_length)
                    setattr(var, '시즌스탯', g.s_today_score)
                    setattr(var, '이닝', inn)
                    if g.s_stat_name != '볼넷 당 삼진비':
                        setattr(var, '직전경기스탯', g.s_last_score)
                    return var
            else:
                setattr(var, '존재', False)
                return var
        except Exception as e:
            print(e, 'pitcher_record pitcher_stat_text 경기수 부족')
            pass

class NamedVariable:
    pass
