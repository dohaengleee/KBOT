from blog.lib import globals as g
import pandas as pd

class HitterRecord(object):
    def __init__(self, hitter_code, recent_games=None, season=None, total=None, how=None):
        self.hitter_code = hitter_code
        self.recent_games = recent_games
        self.season = season
        self.total = total
        self.today = True if recent_games == season == total else False
        self.game_id = g.GAME_ID
        self.consecutive_hr = []
        self.record_matrix_mix = g.record_matrix_mix
        self._name = None
        self._game_num = None
        self.record = None
        self.df_record_matrix = None
        self._winning_hit_kor = None
        self._is_winning_hit = None
        self.how = how
        self._hit = self._rbi = self._bb = self._pa = self._h1 = self._h2 = self._h3 = self._ops = None
        self._hr = self._ab = self._hp = self._sf = self._kk = self._run = self._err = None
        self.set_hitter_record()
        self.winteam_flag()

        g.define_method(self, g.hitter_method)
        for k, v in g.VARIABLE_DICT['hitterrecord_dynamic_variable'].items():
            setattr(self, k, v)

    def set_hitter_record(self):
        if self.recent_games:
            result = g.b_models.Hitter.objects\
                .filter(pcode__exact=self.hitter_code)\
                .filter(gmkey__in=self.recent_games)
        elif self.season:
            result = g.b_models.Hitter.objects \
                .filter(gmkey__startswith=g.GAME_YEAR) \
                .filter(pcode__exact=self.hitter_code) \
                .filter(gday__lte=g.GAME_DATE).order_by('-gday')
        elif self.total:
            result = g.b_models.Hitter.objects \
                .filter(gday__lte=g.GAME_DATE) \
                .filter(pcode__exact=self.hitter_code)
        else:
            result = g.hitters_today.filter(pcode__exact=self.hitter_code)

        self.record = pd.DataFrame(list(result.values()))

    def name(self):
        """
        이름
        :return:
        """
        if self._name:
            return self._name
        self._name = self.record.iloc[0]['name']
        return self._name

    def code(self):
        """
        타자코드
        :return:
        """
        return self.hitter_code

    def great_hitter_code(self):
        """
        우수타자코드
        :return:
        """
        return g.great_hitter

    def used_personal_record(self):
        """
        used_타자개인기록
        :return:
        """
        return g.used_personal_record

    def game_num(self):
        """
        경기수
        :return:
        """
        if self._game_num:
            return self._game_num

        self._game_num = self.record.shape[0]
        return self._game_num

    def recent_15_days(self):
        pass

    def is_great(self):
        """
        is_우수
        :return:
        """
        if self.recent_games:
            return float(self.avg()) >= 0.4 or float(self.ops()) >= 1.0
        else:
            return float(self.avg()) >= 0.3 and float(self.ops()) >= 0.8

    def is_enough(self):
        """
        is_충분
        :return:
        """
        pa = self._pa if self._pa else self.pa()
        game_num = self._game_num if self._game_num else self.game_num()
        try:
            # r = pa / (self.how_many_games_in('futures') * 3.1)
            # is_enough = game_num >= 3 and pa > 10 and ((pa > 100) or (r > 1 / 3.0))
            r = pa / (game_num * 2.7)
            is_enough = game_num >= 3 and pa > 10 and (r >= 1)
        except ZeroDivisionError as e:
            is_enough = False
        return is_enough

    def how_many_games_in(self, league):
        game_num = self._game_num if self._game_num else self.game_num()
        if league == 'futures':
            result = game_num / 6
        else:
            result = game_num / 5
        return result

    # region [Day기록]
    def avg(self):
        """
        타율
        :return:
        """
        try:
            ab = self._ab if self._ab else self.ab()
            hit = self._hit if self._hit else self.hit()
            temp = round(hit / ab, 5)
            if len(str(temp)) <= 4:
                if len(str(temp).split('.')) == 2:
                    return str(temp) + '00'
                else:
                    return float(temp)
            elif str(temp)[-1] == '5' and int(str(temp)[-2]) % 2 == 0:
                temp = float(str(temp + 0.001)[:-1])
                return float(str(temp)[:5])
            else:
                temp = round(hit / ab, 3)
                return temp if len(str(temp).split('.')[1]) == 3 else str(temp) + '0'
        except ZeroDivisionError as e:
            result = 0
        return result

    def slg(self):
        try:
            h1 = self._h1 if self._h1 else self.h1()
            h2 = self._h2 if self._h2 else self.h2()
            h3 = self._h3 if self._h3 else self.h3()
            hr = self._hr if self._hr else self.hr()
            ab = self._ab if self._ab else self.ab()
            slg = "%.3f" % round((h1 + 2 * h2 + 3 * h3 + 4 * hr) / ab, 3)
        except ZeroDivisionError as e:
            slg = 0
        return slg

    def ops(self):
        """
        ops
        :return:
        """
        if self._ops:
            return self._ops
        self._ops = "%.3f" % (float(self.slg()) + float(self.obp()))
        return self._ops

    def obp(self):
        """

        :return:
        """
        try:
            hit = self._hit if self._hit else self.hit()
            bb = self._bb if self._bb else self.bb()
            hp = self._hp if self._hp else self.hp()
            ab = self._ab if self._ab else self.ab()
            sf = self._sf if self._sf else self.sf()
            obp = "%.3f" % round((hit + bb + hp)/(ab + bb + hp + sf), 3)
        except ZeroDivisionError as e:
            obp = 0
        return obp

    def ab(self):
        """
        타수
        :return:
        """
        if self._ab:
            return self._ab

        self._ab = self.record['ab'].sum()
        return self._ab

    def bb(self):
        """
        볼넷수
        :return:
        """
        if self._bb:
            return self._bb

        self._bb = self.record['bb'].sum()

        return self._bb

    def hit(self):
        """
        안타수
        :return:
        """
        if self._hit:
            return self._hit
        try:
            self._hit = self.record['hit'].sum()
        except Exception as e:
            print(e)

        return self._hit

    def h1(self):
        hit = self._hit if self._hit else self.hit()
        h2 = self._h2 if self._h2 else self.h2()
        h3 = self._h3 if self._h3 else self.h3()
        hr = self._hr if self._hr else self.hr()
        return hit - (h2 + h3 + hr)

    def h2(self):
        if self._h2:
            return self._h2

        self._h2 = self.record['h2'].sum()
        return self._h2

    def h3(self):
        if self._h3:
            return self._h3

        self._h3 = self.record['h3'].sum()
        return self._h3

    def hr(self):
        """
        홈런수
        :return:
        """
        if self._hr:
            return self._hr

        self._hr = self.record['hr'].sum()
        return self._hr

    def winteam_flag(self):
        """
        is_승리팀_타자
        :return:
        """
        lose_team = g.LOSE_TEAM
        record = self.record
        if record.tb[0] == 'T':
            team = g.team_kor_dict[record.gmkey[0][8:10]]
        else:
            team = g.team_kor_dict[record.gmkey[0][10:12]]

        if team == lose_team:
            return False
        else:
            return True

    def kk(self):
        """
        삼진수
        :return:
        """
        if self._kk:
            return self._kk
        self._kk = self.record['kk'].sum()
        return self._kk

    def pa(self):
        """
        타석수
        :return:
        """
        if self._pa:
            return self._pa

        self._pa = self.record['pa'].sum()
        return self._pa

    def rbi(self):
        """
        타점수
        :return:
        """
        if self._rbi:
            return self._rbi

        self._rbi = self.record['rbi'].sum()
        return self._rbi

    def run(self):
        """
        득점수
        :return:
        """
        if self._run:
            return self._run

        self._run = self.record['run'].sum()
        return self._run

    def err(self):
        if self._err:
            return self._err

        self._err = self.record['err'].sum()
        return self._err

    def hp(self):
        if self._hp:
            return self._hp

        self._hp = self.record['hp'].sum()
        return self._hp

    def sf(self):
        if self._sf:
            return self._sf

        self._sf = self.record['sf'].sum()
        return self._sf

    def obn(self):
        """
        출루수
        :return:
        """
        hit = self._hit if self._hit else self.hit()
        bb = self._bb if self._bb else self.bb()
        hp = self._hp if self._hp else self.hp()
        return hit + bb + hp

    def tb(self):
        return self.record.iloc[0]['tb']

    def oneturn(self):
        """
        타순
        :return:
        """
        if self.today:
            return self.record.iloc[0]['oneturn']
        else:
            return False

    def is_cycling_hit(self):
        """
        is_사이클링히트
        :return:
        """

        var = NamedVariable()
        today_is_exist = False

        if self.today:
            hit = self._hit if self._hit else self.hit()
            hr = self._hr if self._hr else self.hr()
            h2 = self._h2 if self._h2 else self.h2()
            h3 = self._h3 if self._h3 else self.h3()

            if hit > 3:
                if hr > 0 and h2 > 0 and h3 > 0 and (hit > hr + h2 + h3):
                    today_is_exist = True
                else:
                    today_is_exist = False
            else:
                today_is_exist = False
        else:
            today_is_exist = False

        setattr(var, 'today', today_is_exist)

        if today_is_exist:
            article_list = []
            gamecontapp = g.b_models.Gamecontapp.objects.filter(gmkey=self.game_id, hitter=self.hitter_code)
            gamecontapp_df = pd.DataFrame(gamecontapp.values())

            for i in range(len(gamecontapp_df)):
                if gamecontapp_df.how[i] == 'H1':
                    article_list.append(''.join('1루타 ({inn})'.format(inn=gamecontapp_df.inn[i])))
                elif gamecontapp_df.how[i] == 'H2':
                    article_list.append(''.join('2루타 ({inn})'.format(inn=gamecontapp_df.inn[i])))
                elif gamecontapp_df.how[i] == 'H3':
                    article_list.append(''.join('2루타 ({inn})'.format(inn=gamecontapp_df.inn[i])))
                elif gamecontapp_df.how[i] == 'HR':
                    article_list.append(''.join('2루타 ({inn})'.format(inn=gamecontapp_df.inn[i])))

            setattr(var, '내용', ', '.join([i for i in article_list]))

        return var

    def is_consecutive_hr(self):
        """
        is_연타석_홈런
        :return:
        """
        hr = self._hr if self._hr else self.hr()
        if self.today and hr > 0:
            hitter_records = g.gamecontapp.filter(hitter=self.hitter_code, rturn='').values_list('how', flat=True)

            self.consecutive_hr = []
            counter = 0
            for how in hitter_records:
                if how == 'HR':
                    counter += 1
                else:
                    counter = 0

                if counter >= 2:
                    self.consecutive_hr.append(counter)

            if self.consecutive_hr:
                return True
            else:
                return False
        else:
            return False

    def is_consecutive_hr_old(self):
        """
        is_연타석_홈런
        :return:
        """
        hr = self._hr if self._hr else self.hr()
        if self.today and hr > 0:

            hitter_hr_record = self.record_matrix_mix.filter(bat_p_id=self.hitter_code).values('how_id')

            self.consecutive_hr = []
            counter = 0
            for how in hitter_hr_record:
                if how['how_id'] == 'HR':
                    counter += 1
                else:
                    counter = 0

                if counter >= 2:
                    self.consecutive_hr.append(counter)

            if self.consecutive_hr:
                return True
            else:
                return False
        else:
            return False

    def consecutive_hr_num(self):
        """
        연타석홈런_연타수
        :return:
        """
        hr = self._hr if self._hr else self.hr()
        if self.today and hr > 0:
            if self.is_consecutive_hr():
                return max(self.consecutive_hr)
            else:
                return 0
        else:
            return False

    def is_winning_hit(self):
        """
        is_결승타
        :return:
        """
        if self.today:

            if g.AWAY_SCORE == g.HOME_SCORE:
                return False

            score_gap = True if g.AWAY_SCORE < g.HOME_SCORE else False
            score_flag = False
            winning_hit_flag = False
            record = None

            game = g.gamecontapp[::-1]

            for i, d in enumerate(game):
                score_gap_count = d.bscore - d.tscore
                if score_gap and score_gap == (score_gap_count <= 0):
                    score_flag = True
                elif not score_gap and score_gap == (score_gap_count < 0):
                    score_flag = True

                if score_flag:
                    # 안타성 hit 이였으면 이 이벤트가 결승타
                    if d.how in g.HIT:
                        record = d
                        winning_hit_flag = True
                    elif game[i - 1].how in g.HIT:
                        record = game[i - 1]
                        winning_hit_flag = True
                    else:
                        hitter_cd = d.hitter
                        # 10개의 이벤트를 보자 한타석에 10개 이벤트는 안나오겠지
                        for j in range(1, 10):
                            record = game[i + j]
                            if record.hitter == hitter_cd:
                                if record.how in g.HIT:
                                    winning_hit_flag = True
                                    break
                            else:
                                break

                    if winning_hit_flag and record:
                        self._winning_hit_kor = g.HOW_KOR_DICT[record.how]
                        self._is_winning_hit = record.hitter == self.hitter_code
                        return True
                    else:
                        return False
        return False

    def is_winning_hit_old(self):
        """
        is_결승타
        :return:
        """
        if self.today:
            record_matrix_desc = self.record_matrix_mix.order_by('-seqno').values()

            if g.AWAY_SCORE == g.HOME_SCORE:
                return False

            for i, d in enumerate(record_matrix_desc):
                if d['after_score_gap_cn'] == 0:
                    record = record_matrix_desc[i - 1]

                    if '실책으로' in record['livetext_if']:
                        return False

                    if record['how_id'] not in g.HIT:
                        return False
                    else:
                        self._winning_hit_kor = g.HOW_KOR_DICT[record['how_id']]
                        self._is_winning_hit = record['bat_p_id'] == self.hitter_code
                        return True

    def how_winning_hit(self):
        """
        결승타_종류
        :return:
        """
        if self.today:
            if self._is_winning_hit is None:
                self.is_winning_hit()

            if self._is_winning_hit:
                return self._winning_hit_kor

    # endregion [Day기록]

    # region [시즌기록]
    def n_game_hr_consecutive(self):
        """
        n경기_연속_홈런
        :return:
        """
        _how = 'hr'
        counter = 0
        last_game_date = g.GAME_DATE
        vs_team_code = ''
        for i, row in self.record.iterrows():
            if row[_how] > 0:
                counter = i + 1
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
        if counter > 1:
            vs_team_kor = g.team_kor_dict[vs_team_code]
            setattr(_record, '존재', True)
            setattr(_record, '날짜', days_kor)
            setattr(_record, '일수', days)
            setattr(_record, '상대팀', vs_team_kor)
            setattr(_record, '경기수', counter)
        else:
            setattr(_record, '존재', False)


        return _record

    def n_game_hit_consecutive(self):
        """
        n경기_연속_안타
        :return:
        """
        counter = 0
        last_game_date = g.GAME_DATE
        vs_team_code = ''
        for i, row in self.record.iterrows():
            if row['hit'] - row['hr'] > 0:
                counter = i + 1
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
        if counter > 1:
            vs_team_kor = g.team_kor_dict[vs_team_code]
            setattr(_record, '존재', True)
            setattr(_record, '날짜', days_kor)
            setattr(_record, '일수', days)
            setattr(_record, '상대팀', vs_team_kor)
            setattr(_record, '경기수', counter)
        else:
            setattr(_record, '존재', False)
            setattr(_record, '경기수', counter)

        return _record

    def n_game_h2_consecutive(self):
        """
        n경기_연속_2루타
        :return:
        """
        _how = 'h2'
        counter = 0
        last_game_date = g.GAME_DATE
        vs_team_code = ''
        for i, row in self.record.iterrows():
            if row[_how] > 0:
                counter = i + 1
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
        if counter > 1:
            vs_team_kor = g.team_kor_dict[vs_team_code]
            setattr(_record, '존재', True)
            setattr(_record, '날짜', days_kor)
            setattr(_record, '일수', days)
            setattr(_record, '상대팀', vs_team_kor)
            setattr(_record, '경기수', counter)
        else:
            setattr(_record, '존재', False)
            setattr(_record, '경기수', counter)

        return _record

    def n_game_h3_consecutive(self):
        """
        n경기_연속_3루타
        :return:
        """
        _how = 'h3'
        counter = 0
        last_game_date = g.GAME_DATE
        vs_team_code = ''
        for i, row in self.record.iterrows():
            if row[_how] > 0:
                counter = i
                last_game_date = row['gday']
                vs_team_code = row['gmkey'][10:12] if row['tb'] == 'T' else row['gmkey'][8:10]
            else:
                break

        _record = NamedVariable()
        if counter <= 1:
            setattr(_record, '존재', False)
            setattr(_record, '경기수', counter)
            return _record

        if counter > 1:
            days_kor, days = g.get_diff_days(game_date=g.GAME_DATE, last_record_date=last_game_date)
            vs_team_kor = g.team_kor_dict[vs_team_code]
            setattr(_record, '존재', True)
            setattr(_record, '날짜', days_kor)
            setattr(_record, '일수', days)
            setattr(_record, '상대팀', vs_team_kor)
            setattr(_record, '경기수', counter)
        else:
            setattr(_record, '존재', False)
            setattr(_record, '경기수', counter)

        return _record

    def n_game_hr_last(self):
        """
        n경기_만에_홈런
        :return:
        """
        _how = 'hr'
        counter = 0
        last_game_date = g.GAME_DATE
        vs_team_code = ''
        """
        // 190218 N경기 만에 날짜 수정
        FROM. 
        for i, row in self.record.iterrows():
            if i == 0 and row[_how] > 0:
                counter += 1
            elif i > 0 and row[_how] == 0:
                counter += 1
                last_game_date = row['gday']
                vs_team_code = row['gmkey'][10:12] if row['tb'] == 'T' else row['gmkey'][8:10]
            else:
                break

        """
        for i, row in self.record.iterrows():
            if i > 0 and row[_how] > 0:
                counter = i
                last_game_date = row['gday']
                vs_team_code = row['gmkey'][10:12] if row['tb'] == 'T' else row['gmkey'][8:10]
                break

        _record = NamedVariable()
        if counter <= 1:
            setattr(_record, '존재', False)
            setattr(_record, '경기수', counter)
            return _record

        if counter > 1:
            days_kor, days = g.get_diff_days(game_date=g.GAME_DATE, last_record_date=last_game_date)
            vs_team_kor = g.team_kor_dict[vs_team_code]
            setattr(_record, '존재', True)
            setattr(_record, '날짜', days_kor)
            setattr(_record, '일수', days)
            setattr(_record, '상대팀', vs_team_kor)
            setattr(_record, '경기수', counter)
        else:
            setattr(_record, '존재', False)
            setattr(_record, '경기수', counter)

        return _record

    def n_game_hit_last(self):
        """
        n경기_만에_안타
        :return:
        """
        counter = 0
        last_game_date = g.GAME_DATE
        vs_team_code = ''
        for i, row in self.record.iterrows():
            if i == 0 and row['hit'] - row['hr'] > 0:
                counter += 1
            # 안타에 홈런 포함
            # elif i > 0 and row['hit'] - row['hr'] == 0:
            #     counter += 1
            else:
                last_game_date = row['gday']
                vs_team_code = row['gmkey'][10:12] if row['tb'] == 'T' else row['gmkey'][8:10]
                break

        _record = NamedVariable()
        if counter <= 1:
            setattr(_record, '존재', False)
            setattr(_record, '경기수', counter)
            return _record

        #  임시, 에러나는 이유 파악 필요
        elif vs_team_code == '':
            setattr(_record, '존재', False)
            setattr(_record, '경기수', counter)

        elif counter > 1:
            days_kor, days = g.get_diff_days(game_date=g.GAME_DATE, last_record_date=last_game_date)
            vs_team_kor = g.team_kor_dict[vs_team_code]
            setattr(_record, '존재', True)
            setattr(_record, '날짜', days_kor)
            setattr(_record, '일수', days)
            setattr(_record, '상대팀', vs_team_kor)
            setattr(_record, '경기수', counter)
        else:
            setattr(_record, '존재', False)
            setattr(_record, '경기수', counter)

        return _record

    def season_avg(self):
        """
        시즌_타율
        :return:
        """
        return 0

    def season_obn(self):
        """
        시즌_출루
        :return:
        """
        return 0

    def season_obp(self):
        """
        시즌_출루율
        :return:
        """
        return 0

    def season_slg(self):
        """
        시즌_장타율
        :return:
        """
        return 0
    # endregion [시즌기록]

    # region [퓨처스 핫이슈 기록]
    def get_first_position(self):
        """
        첫포지션
        :return:
        """
        var = NamedVariable()
        setattr(var, '존재', False)

        today_hitter_entry = g.entry_obj.filter(pcode=self.hitter_code, posi__startswith='1')
        if today_hitter_entry.count() > 0:
            posi = today_hitter_entry[0].posi
            hitter_total_entry = g.b_models.Entry.objects.filter(pcode=self.hitter_code, gday__lt=g.GAME_DATE)
            hitter_total_entry_posi = g.b_models.Entry.objects.filter(pcode=self.hitter_code, gday__lt=g.GAME_DATE,
                                                                      posi__startswith=posi)

            # f_year = hitter_total_entry
            if hitter_total_entry.count() > 10:  # 퓨처스출전 10경기 이상일 때
                if hitter_total_entry_posi.count() == 0:
                    if posi[-1] in ['D', 'H', 'R']:
                        setattr(var, '존재', False)
                    else:
                        setattr(var, '존재', True)
                        setattr(var, '포지션', g.POS_KOR[posi[-1]])
                        setattr(var, '첫년도', hitter_total_entry[0].gyear)
                else:
                    setattr(var, '존재', False)

        return var

    def get_record_combination_hr_h3(self):
        """
        만루홈런_3루타
        :return:
        """
        var = NamedVariable()
        setattr(var, '존재', False)
        hitter_list = []
        hitter_name_list = []
        hitter_4_hr = g.gamecontapp.filter(hitter=self.hitter_code, how='HR').exclude(base1b='').exclude(base2b='').exclude(base3b='')
        today_hitter_h3 = g.hitters_today.filter(pcode=self.hitter_code, h3__gt=0)
        if hitter_4_hr.count() > 0 and today_hitter_h3.count() > 0:
            setattr(var, '존재', True)
            all_four_hr_hitters = g.b_models.Gamecontapp.objects.filter(how='HR', gday__lt=g.GAME_DATE).exclude(base1b='').exclude(base2b='').exclude(base3b='')
            for hitter in all_four_hr_hitters:
                hitter_h3 = g.b_models.Hitter.objects.filter(gmkey=hitter.gmkey, pcode=hitter.hitter, h3__gt=0)
                if hitter_h3.count() > 0:
                    hitter_name_list.append(hitter.hitname)
                    if hitter.tb == 'T':
                        team = hitter.gmkey[8:10]
                        vs_team = hitter.gmkey[10:12]
                        # 경찰팀이 DB에 없어서 하드코딩
                        if team == 'PL':
                            team_kor = '경찰'
                        else:
                            team_kor = g.team_kor_dict[team]
                        if vs_team == 'PL':
                            vs_team_kor = '경찰'
                        else:
                            vs_team_kor = g.team_kor_dict[vs_team]
                    else:
                        team = hitter.gmkey[10:12]
                        vs_team = hitter.gmkey[8:10]
                        if team == 'PL':
                            team_kor = '경찰'
                        else:
                            team_kor = g.team_kor_dict[team]
                        if vs_team == 'PL':
                            vs_team_kor = '경찰'
                        else:
                            vs_team_kor = g.team_kor_dict[vs_team]

                    when_kor = "%s년 %s월 %s일 %s전 %s(%s)" % (hitter.gday[0:4], int(hitter.gday[4:6]), int(hitter.gday[6:8]), vs_team_kor, hitter.hitname, team_kor)
                    hitter_list.append(when_kor)

            hitter_name_list.append(hitter_4_hr[0].hitname)
            when_kor = "오늘 %s" % hitter_4_hr[0].hitname
            hitter_list.append(when_kor)
            setattr(var, '타자들', ', '.join(hitter_list))
            setattr(var, '몇명', len(set(hitter_name_list)))

        return var

    def get_first_hitter_hr(self):
        """
        선두타자홈런
        :return:
        """
        var = NamedVariable()
        setattr(var, '존재', False)

        first_hitter = g.gamecontapp.filter(hitter=self.hitter_code, inn=1, turn='11', how='HR', ocount='0')
        if first_hitter.count() > 0:
            setattr(var, '존재', True)
            tb_kor = '초' if first_hitter[0].tb == 'T' else '말'
            setattr(var, '초말', tb_kor)
            team_cd = first_hitter[0].gmkey[8:10] if tb_kor == '초' else first_hitter[0].gmkey[10:12]

            first_hitters = g.b_models.Gamecontapp.objects.filter(gday__lte=g.GAME_DATE, inn=1, turn='11', how='HR', ocount='0').extra(
                where=[
                    "((substring(gmkey, 9, 2) = '{0}' and tb = 'T') or (substring(gmkey, 11, 2) = '{0}' and tb = 'B'))".format(
                        team_cd),
                ]
            )
            if first_hitter[0].bcnt == '0-0':
                setattr(var, 'is_초구', True)

            setattr(var, '몇번째', first_hitters.count())

        return var

    def is_rookie(self):
        """
        is_신인
        :return:
        """

        var = NamedVariable()
        is_rookie = False
        from blog.baseball_models import Gamecontapp
        first_league = Gamecontapp.objects.filter(hitter__exact=self.hitter_code)
        if first_league.count() == 0:
            person = g.b_models.Person.objects.filter(indate__exact='201901', pcode__exact=self.hitter_code)
            if person and int(person[0].birth) > 19980000:
                is_rookie = True
                _hitter = g.hitters_today.filter(pcode=self.hitter_code)[0]
                hit = _hitter.hit
                hr = _hitter.hr
                rbi = _hitter.rbi
                is_outstanding = hit >= 4 or hr >= 2 or rbi >= 4 or (hit >= 4 and hr >= 1) or (hit >= 4 and rbi >= 3)
                setattr(var, 'is_신인', is_rookie)
                setattr(var, 'is_대활약', is_outstanding)
                return var
        else:
            setattr(var, 'is_신인', is_rookie)
            return var

    def most_hits(self):
        """
        개인최다안타
        :return:
        """
        var = NamedVariable()
        for hitter in g.hitters_today:
            today_hit = hitter.hit
            records = pd.DataFrame(g.b_models.Hitter.objects.filter(name=hitter.name).values())[:-1]
            records_2019 = pd.DataFrame(g.b_models.Hitter.objects.filter(name=hitter.name, gday__startswith='2019').values())[:-1]
            setattr(var, '존재', False)
            if records.hit.max() < today_hit and len(records) > 20 and g.great_hitter == hitter.pcode:
                setattr(var, '존재', True)
                setattr(var, '개수', today_hit)
                setattr(var, '이름', hitter.name)
            elif records_2019.hit.max() < today_hit and len(records_2019) > 20 and g.great_hitter == hitter.pcode:
                setattr(var, '존재', True)
                setattr(var, '개수', today_hit)
                setattr(var, '이름', hitter.name)
                setattr(var, '올시즌최다', True)
        return var

    # endregion [퓨처스 핫이슈 기록]

    def hitter_rank_text(self):
        """
        타자_랭킹그래프
        :return:
        """

        try:
            _record = NamedVariable()
            if g.h_graph_exist:
                g_type = g.graph_type
                if g_type == 'rank':
                    setattr(_record, '존재', True)
                    setattr(_record, '이름', g.h_name)
                    setattr(_record, '스탯', g.h_stat_name)
                    setattr(_record, 'is_공동', g.h_is_joint)
                    setattr(_record, '랭크', g.h_target_ranking)
                    setattr(_record, '리그', g.h_league)
                    setattr(_record, '스코어', g.h_values)
                    return _record
            else:
                setattr(_record, '존재', False)
                return _record
        except:
            print('hitter_record hitter_rank_text')

    def hitter_stat_text(self):
        """
        타자_스탯그래프
        :return:
        """

        try:
            _record = NamedVariable()
            if g.h_graph_exist:
                g_type = g.graph_type
                if g_type == 'stat':
                    setattr(_record, '존재', True)
                    setattr(_record, '이름', g.h_s_name)
                    setattr(_record, '스탯', g.h_s_stat_name)
                    setattr(_record, '이번달스코어', g.h_s_today_score)
                    setattr(_record, '저번달스코어', g.h_s_last_score)
                    setattr(_record, '경기수', g.h_s_game_num)
                    setattr(_record, '저번달경기수', g.h_s_last_game_num)
                    setattr(_record, '이번달', g.h_s_current_month)
                    setattr(_record, '저번달', g.h_s_last_month)
                    setattr(_record, '이번달타수', g.h_s_today_ab)
                    setattr(_record, '이번달안타수', g.h_s_today_hit)
                    setattr(_record, '저번달타수', g.h_s_last_ab)
                    setattr(_record, '저번달안타수', g.h_s_last_hit)
                    return _record
            else:
                setattr(_record, '존재', False)
                return _record
        except:
            print('hitter_record hitter_stat_text')
    
class NamedVariable:
    pass
