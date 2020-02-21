from django.core.exceptions import ObjectDoesNotExist
from collections import namedtuple, OrderedDict
from blog.lib import globals as g
from blog.lib.classes.player import Player
from blog.lib.classes.team import Team
from blog.lib.classes.event import Event
from blog.lib.sub_classes.event_scenes import ScoreScenes
from blog.lib.sub_classes.half_inning import HalfInning
from blog.lib.sub_classes.hitter_record import HitterRecord
from blog.lib.classes.pitcher import PitcherVariables
from blog.lib.classes.hitter_e import Hitter_e_Variables
import pandas as pd
from blog.lib.analysis.rank_graph import HitterRank
from blog.lib.analysis.stat_graph import HitterStat
# import warnings
# warnings.filterwarnings('ignore')

class GameVariables(object):
    def __init__(self, kinds_of_article=None, hitter_e_article=None, ):
        self.score_dict = g.game_score.__dict__
        self.away_team_info = None
        self.home_team_info = None
        self.winning_hit_dict = {}
        self.half_innings = OrderedDict()
        self.scenes = None
        self.top_player_list = []
        self.top_player_list_4_selection = []  # 기사비교용 탑플레이어 점수
        self.select_article = []
        self.top_pitcher_list = []
        self._top_player = None
        self._great_hitter = None
        self.last_pa_event = None
        self.top_pitcher = self.get_top_pitcher()  # 투수_탑플레이어
        self.game_year = 0
        self.is_winning_hit = None
        self.set_class_variables()
        self.set_player_record()  # 탑플레이어 점수 셋팅하는 함수
        self.is_called_game()
        self.today_weather()
        self.great_hitter()
        self.kinds_of_article = kinds_of_article
        self.hitter_e_article = hitter_e_article

        if kinds_of_article:
            self.top_pitcher = self.get_top_pitcher()
            self.pitcher_article = self.pitcher_event()
            self.hitter_exceptional_article = ''
        elif hitter_e_article:
            self.hitter_exceptional_article = self.hitter_e_event()
            self.pitcher_article = ''
            self.is_rare = self.is_rare_record()
        else:
            self.pitcher_article = ''
            self.hitter_exceptional_article = ''

        self._rare_hitter = ''
        self.init_event()

        g.define_method(self, g.game_method)

        for k, v in g.VARIABLE_DICT['common_dynamic_variable'].items():
            setattr(self, k, v)

    def pitcher_event(self):
        pitcher_cd = ''
        for top_player in self.top_pitcher_list:
            if top_player['tb'] == g.WIN_TB:
                pitcher_cd = top_player['pcode']
                break
            elif g.WIN_TB is None:
                pitcher_cd = top_player['pcode']
                break

        pitcher_event = PitcherVariables(pitcher_cd)
        result_list = pitcher_event.get_sentence()
        return result_list

    def hitter_e_event(self):
        is_rare_record = self.is_rare_record()
        is_total_rare_record = self.hitter_total_rare_record()
        if is_rare_record.존재:
            hitter_cd = is_rare_record.hitter_code
            hitter_event = Hitter_e_Variables(hitter_cd)
            result_list = hitter_event.get_sentence()
        elif is_total_rare_record.통산기록 or is_total_rare_record.통산루타:
            hitter_cd = is_total_rare_record.코드
            hitter_event = Hitter_e_Variables(hitter_cd)
            result_list = hitter_event.get_sentence()
        else:
            result_list = ''
        return result_list

    def get_dict_var(self):
        return self.__dict__

    def away_team(self):
        """
        원정팀
        :return:
        """
        return self.away_team_info

    def home_team(self):
        """
        홈팀
        :return:
        """
        return self.home_team_info

    def lose_team(self):
        """
        패배팀
        :return:
        """
        if g.HOME_SCORE < g.AWAY_SCORE:
            return self.home_team_info
        elif g.HOME_SCORE > g.AWAY_SCORE:
            return self.away_team_info
        else:
            return self.away_team_info

    def win_team(self):
        """
        승리팀
        :return:
        """
        if g.HOME_SCORE > g.AWAY_SCORE:
            return self.home_team_info
        elif g.HOME_SCORE < g.AWAY_SCORE:
            return self.away_team_info
        else:
            return self.home_team_info

    @staticmethod
    def is_home_win():
        if g.HOME_SCORE > g.AWAY_SCORE:
            return True
        else:
            return False

    def top_player(self):
        """
        탑플레이어
        :return:
        """
        if self._top_player is None:
            _top_player = self.top_player_list[0]
            self._top_player = Player(_top_player['pcode'], _top_player['team_code'])
        return self._top_player

    def get_top_pitcher(self):
        """
        게임_투수_탑플레이어
        :return:
        """
        top_pitcher = None
        for pitcher in g.pitchers_today:
            top_point = g.get_pitcher_top_point_4_article(pitcher)

            self.top_pitcher_list.append({
                'pcode': pitcher.pcode,
                'point': round(top_point, 3),
                'tb': pitcher.tb,
                'team_code': g.AWAY_ID if pitcher.tb == 'T' else g.HOME_ID,
            })

        self.top_pitcher_list.sort(key=lambda k: k['point'], reverse=True)

        for pitcher in self.top_pitcher_list:
            if pitcher['tb'] == g.WIN_TB:
                top_pitcher = Player(pitcher['pcode'], pitcher['team_code'])
                g.top_pitcher_cd = pitcher['pcode']
                break
            elif g.WIN_TB is None:
                top_pitcher = Player(pitcher['pcode'], pitcher['team_code'])
                g.top_pitcher_cd = pitcher['pcode']
                break

        return top_pitcher

    def winner_team_top_player(self):
        """
        승리팀_탑플레이어
        :return:
        """
        top_player = {}
        for player in self.top_player_list:
            if player['tb'] == g.WIN_TB:
                top_player = player
                break
        winner_team_top_player = Player(top_player['pcode'], top_player['team_code'])
        return winner_team_top_player

    def great_hitter(self):
        """
        우수타자
        :return:
        """
        if self._great_hitter:
            return self._great_hitter

        for t_player in self.top_player_list:
            if t_player['posi'] == 'hitter' and t_player['tb'] == g.WIN_TB:
                self._great_hitter = Player(t_player['pcode'], t_player['team_code'])
                _hitter = self._great_hitter.hitter()
                hit = _hitter.hit()
                hr = _hitter.hr()
                rbi = _hitter.rbi()
                result = hit >= 3 or hr >= 2 or rbi >= 3 or (hit >= 2 and hr >= 1) or (hit >= 2 and rbi >= 2)
                if result:
                    g.great_hitter = t_player['pcode']
                    return self._great_hitter
                else:
                    top_hitter_code = g.models.TopPlayerHitter.objects.filter(game_id=g.GAME_ID, tb=g.WIN_TB).values_list(
                        'pcode').latest('top_point')
                    team = g.GAME_ID[8:10] if g.WIN_TB == 'T' else g.GAME_ID[10:12]
                    self._great_hitter = Player(top_hitter_code[0], team)
                    return self._great_hitter


    def get_hitter_top_point(self, hitter):
        # hitter_records = self.record_matrix_mix.filter(bat_p_id=hitter.pcode).values_list('how_id', flat=True)
        hitter_records = g.gamecontapp.filter(hitter=hitter.pcode, rturn='').values_list('how', flat=True)

        result_point = 0
        for record in hitter_records:
            result_point += g.H_R_POINT[g.H_R_TOP_RANK_POINT_DICT[record]]

        result_point += (
                hitter.ab * 0.5 +
                hitter.run * 2 +
                hitter.rbi * 4 +
                hitter.err * -5
        )
        if hitter.hit > 3 and \
                hitter.hr > 0 and \
                hitter.h2 > 0 and \
                hitter.h3 > 0 and \
                hitter.hit > hitter.hr + hitter.h2 + hitter.h3:
            result_point += 40

        if self.is_winning_hit and self.winning_hit_dict['hitter'] == hitter.pcode:
            result_point += 7
        return result_point

    @staticmethod
    def get_pitcher_top_point(pitcher):
        pitcher_penalty = 0.6
        # pitcher_records = self.record_matrix_mix.filter(pit_p_id__exact=pitcher.pcode)
        pitcher_records = g.gamecontapp.filter(pitcher=pitcher.pcode)

        result_point = 0
        for i, record in enumerate(pitcher_records):
            out_cn = 2 if record.ocount == '4' else int(record.ocount)
            b1 = record.base1b if record.base1b else ''
            b2 = record.base2b if record.base2b else ''
            b3 = record.base3b if record.base3b else ''
            base_list = [b1, b2, b3]
            base_tf = list(map(lambda x: len(x) > 0, base_list))
            base_str = [str(i + 1) for i, v in enumerate(base_tf) if v]
            runner_sc = int(''.join(base_str)) if base_str else 0
            score_gap = record.bscore - record.tscore
            if score_gap > 15:
                score_gap = 15
            elif score_gap < -15:
                score_gap = -15
            try:
                li_rt = g.matrix_detail.get(
                    inn_no=record.inn,
                    tb_sc=record.tb,
                    out_cn=out_cn,
                    runner_sc=runner_sc,
                    score_gap_cn=score_gap
                ).li_rt
            except ObjectDoesNotExist:
                raise ObjectDoesNotExist('get_pitcher_top_point')
            li = 1.5 if li_rt >= 2 else 1
            result_point += g.PITCHER_POINT[g.P_TOP_RANK_POINT_DICT[record.how]] * li

        if pitcher.wls == 'W':
            result_point += 30 if pitcher.start else 20

        if pitcher.sho > 0 and \
                pitcher.wls == 'W' and \
                (pitcher.hit + pitcher.r + pitcher.bb) == 0:
            result_point += 10000
        elif pitcher.sho > 0 and \
                pitcher.wls == 'W' and \
                (pitcher.hit + pitcher.r) == 0:
            result_point += 5000
        elif pitcher.sho:
            result_point += 2000
        elif pitcher.cg:
            result_point += 1600
        elif pitcher.inn2 >= 7 and pitcher.er <= 3:
            result_point += 10
        elif pitcher.inn2 >= 6 and pitcher.er <= 3:
            result_point += 8

        if pitcher.wls == 'L':
            result_point -= 20
        elif pitcher.wls == 'S':
            result_point += 24

        result_point += (pitcher.hold * 16 + pitcher.er * -6 +
                         (pitcher.r - pitcher.er) * -3 + (
                                     pitcher.inn2 / 3) * 9.6)

        result_point *= pitcher_penalty

        return result_point

    @staticmethod
    def is_draw():
        """
        is_무승부
        :return:
        """
        return g.IS_DRAW

    def last_inning_num(self):
        """
        마지막이닝_회
        :return:
        """
        return g.gamecontapp.values().last()['inn']

    def last_inning_tb(self):
        """
        마지막이닝_초말
        :return:
        """
        return g.gamecontapp.values().last()['tb']

    def last_event(self):
        """
        마지막타석
        :return:
        """

        return g.EVENT_LIST[-1]

    def hr_players(self):
        """
        홈런선수들
        :return:
        """
        return False

    def hr_players_num(self):
        '''
        홈런선수명수
        :return:
        '''
        return 1

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

    def today_weather(self):
        """
        날씨
        :return:
        """
        result = ''
        for row in g.live_text.filter(textstyle=7):
            if '콜드' in row.livetext:
                if '강우' in row.livetext:
                    g.today_weather = '강우 '
                    result = '강우 '
                elif '강우' in row.livetext:
                    g.today_weather = '폭염 '
                    result = '폭염 '
                break
        return result

    def is_reversal_any(self):
        """
        is_역전존재
        :return:
        """
        if g.AWAY_SCORE == g.HOME_SCORE == 0:
            return False
        game = g.gamecontapp[::-1]
        # record_matrix_desc = g.record_matrix_mix.order_by('seqno')

        plus_flag = False
        result = False

        for i, d in enumerate(game):
            score_gap_cn = d.bscore - d.tscore

            if i == 0:
                if score_gap_cn > 0:
                    plus_flag = True
                elif score_gap_cn == 0:
                    plus_flag = True
            else:
                if plus_flag and score_gap_cn < 0:
                    result = True
                    break
                elif not plus_flag and score_gap_cn > 0:
                    result = True
                    break

        return result

    def is_reversal_any_old(self):
        """
        역전존재?
        :return:
        """
        if g.AWAY_SCORE == g.HOME_SCORE == 0:
            return False

        record_matrix_desc = g.record_matrix_mix.order_by('seqno')

        lead_team = ''
        follow_count = 0
        reversal_count = 0
        for i, d in enumerate(record_matrix_desc):
            if d.after_score_gap_cn < 0:
                if not lead_team:
                    lead_team = g.AWAY_ID

                if follow_count > 0:
                    if lead_team != g.AWAY_ID:
                        reversal_count += 1
                        lead_team = g.AWAY_ID
            if d.after_score_gap_cn == 0:
                if not lead_team:
                    continue
                if d.before_score_gap_cn != 0:
                    follow_count += 1  # 동점
            if d.after_score_gap_cn > 0:
                # Home Team 앞서감
                if not lead_team:
                    lead_team = g.HOME_ID

                if follow_count > 0:
                    if lead_team != g.HOME_ID:
                        reversal_count += 1
                        lead_team = g.HOME_ID

        return reversal_count > 0

    #  메소드명 변경 가능
    def is_rare_record(self):
        """
        is_진기록
        :return:
        """
        _record = NamedVariable()
        setattr(_record, '존재', False)
        setattr(_record, '사이클링', False)
        setattr(_record, '아까운사이클링', False)
        is_cycling = self.is_cycling()

        if is_cycling.사이클링:
            setattr(_record, '존재', True)
            setattr(_record, '사이클링', True)
            setattr(_record, 'hitter_code', is_cycling.hitter_code)
            setattr(_record, '타자이름', is_cycling.타자이름)
            setattr(_record, '팀', is_cycling.팀)
            setattr(_record, '상대팀', is_cycling.상대팀)
            setattr(_record, '플레이어', is_cycling.플레이어)
            g.kinds_of_rare = '사이클링'

            cycling_records = g.b_models.RareRecords.objects.filter(record_name__exact='cycling_hit', gday__lte=g.GAME_DATE)
            cycling_this_season = g.b_models.RareRecords.objects.filter(record_name__exact='cycling_hit', gday__startswith=g.GAME_YEAR, gday__lte=g.GAME_DATE)
            recent_records = cycling_records[len(cycling_records)-2]
            setattr(_record, '최근사이클링년도', int(recent_records.gday[:4]))
            setattr(_record, '몇번째', cycling_records[len(cycling_records)-1].record_order)
            setattr(_record, '최근사이클링이름', recent_records.name)
            setattr(_record, '최근사이클링팀', g.team_kor_dict[recent_records.player_team])
            setattr(_record, '최근사이클링상대팀', g.team_kor_dict[recent_records.versus_team])
            setattr(_record, '올시즌몇번째', len(cycling_this_season))
            gday = recent_records.gday[4:6].lstrip('0') + '월 ' \
                   + recent_records.gday[6:].lstrip('0') + '일'
            setattr(_record, '최근사이클링날짜', gday)

        elif is_cycling.아까운사이클링:
            setattr(_record, '존재', True)
            setattr(_record, '아까운사이클링', True)
            setattr(_record, 'hitter_code', is_cycling.hitter_code)
            setattr(_record, '타자이름', is_cycling.타자이름)
            setattr(_record, '팀', is_cycling.팀)
            setattr(_record, '상대팀', is_cycling.상대팀)
            setattr(_record, '플레이어', is_cycling.플레이어)
            setattr(_record, '부족한하우', is_cycling.부족한하우)
            g.kinds_of_rare = '아까운사이클링'

        if is_cycling.존재:
            Team._rare_hitter = is_cycling.플레이어
            self._rare_hitter = is_cycling.플레이어

        return _record

    def rare_hitter(self):
        """
        진기록타자
        :return:
        """
        return self._rare_hitter

    def is_cycling(self):
        _record = NamedVariable()
        setattr(_record, '존재', False)
        setattr(_record, '사이클링', False)
        setattr(_record, '아까운사이클링', False)
        for hitter in g.hitters_today:
            hit_dict = {'H1': 0, 'H2': 0, 'H3': 0, 'HR': 0}
            if hitter.hr > 0:
                hit_dict['HR'] = 1
            if hitter.h3 > 0:
                hit_dict['H3'] = 1
            if hitter.h2 > 0:
                hit_dict['H2'] = 1
            if hitter.hit > hitter.hr+hitter.h3+hitter.h2:
                hit_dict['H1'] = 1

            team = self.away_team_info if hitter.tb == 'T' else self.home_team_info
            team_code = hitter.gmkey[8:10] if hitter.tb == 'T' else hitter.gmkey[10:12]
            vs_team = self.home_team_info if hitter.tb == 'T' else self.away_team_info
            # vs_team_code = hitter.gmkey[10:12] if hitter.tb == 'T' else hitter.gmkey[8:10]
            # 사이클링히트
            if sum(hit_dict.values()) == 4:
                setattr(_record, '존재', True)
                setattr(_record, '사이클링', True)
                setattr(_record, 'hitter_code', hitter.pcode)
                setattr(_record, '타자이름', hitter.name)
                setattr(_record, '팀', team)
                setattr(_record, '상대팀', vs_team)
                setattr(_record, '플레이어', Player(hitter.pcode, team_code))
                break

            # 아까운사이클링히트
            if sum(hit_dict.values()) == 3:
                setattr(_record, '존재', True)
                setattr(_record, '아까운사이클링', True)
                setattr(_record, 'hitter_code', hitter.pcode)
                setattr(_record, '타자이름', hitter.name)
                setattr(_record, '팀', team)
                setattr(_record, '상대팀', vs_team)
                setattr(_record, '플레이어', Player(hitter.pcode, team_code))
                g.scarce_how = g.HOW_KOR_DICT[[how for how, value in hit_dict.items() if value == 0][0]]
                setattr(_record, '부족한하우', g.scarce_how)
                break

        return _record
    
    def hitter_total_rare_record(self):
        """
        is_통산진기록
        :return:
        """
        #TODO 그날 경기의 몇번째 HOW에서 통산기록이 수립됐는지 추가해야함 (06/10)

        # 안타, 타점, 홈런, 득점, 루타 / 우선순위 / 100 이상, 50단위 /

        _record = NamedVariable()
        hit_cate = {'hr': '홈런', 'hit': '안타', 'h2': '2루타', 'h3': '3루타', 'rbi': '타점', 'run': '득점'}

        hitter = pd.DataFrame(g.b_models.Hitter.objects.filter(gday__lte=g.GAME_DATE).exclude(name='합계').values(
            'pcode', 'name', 'tb', 'hr', 'hit', 'h2', 'h3', 'rbi', 'run','gmkey'))
        entry = pd.DataFrame(g.b_models.Entry.objects.filter(gmkey=g.GAME_ID).exclude(posi__iendswith='1').values(
            'pcode', 'name', 'team', 'turn', 'posi'))

        df_hitter = hitter.groupby(['pcode', 'name'], as_index=False).sum()
        setattr(_record, '통산기록', False)
        setattr(_record, '통산루타', False)
        for pcode in entry.pcode:
            before_game_record = pd.DataFrame(g.b_models.Hitter.objects.filter(gday__lte=g.GAME_DATE, pcode=pcode).values(
                    'gmkey', 'gday', 'pcode', 'name', 'hr', 'hit', 'h2', 'h3', 'rbi', 'run').order_by('-gmkey'))
            for category in hit_cate.keys():
                before_num = before_game_record[category][1:].sum()
                df_rank = df_hitter.sort_values(by=category, ascending=False)
                temp_df_rank = df_rank[df_rank['pcode'] == pcode]
                record_list = []
                if temp_df_rank[category].values[0] > before_num:
                    record_list = [before_num + i for i in range(1, temp_df_rank[category].values[0] - before_num + 1)]
                else:
                    pass
                for record in record_list:
                    if record >= 100 and record % 50 == 0:
                        setattr(_record, '통산기록', True)
                        setattr(_record, '통산종류', hit_cate[category])
                        setattr(_record, '통산개수', record)
                        setattr(_record, '이전경기통산개수', before_num)
                        setattr(_record, '코드', temp_df_rank.pcode.values[0])
                        setattr(_record, '이름', temp_df_rank.name.values[0])
                        setattr(_record, '팀', g.team_kor_dict[
                            g.GAME_ID[8:10] if entry[entry.pcode==pcode].team.values[0] == 'T' else g.GAME_ID[10:12]])
                        setattr(_record, '상대팀이름', g.team_kor_dict[
                            g.GAME_ID[8:10] if entry[entry.pcode==pcode].team.values[0] == 'B' else g.GAME_ID[10:12]])
                        setattr(_record, '플레이어', Player(_record.코드, g.GAME_ID[8:10] if entry[entry.pcode == pcode].team.values[0] == 'T' else g.GAME_ID[10:12]))
                        if not g.kinds_of_rare:
                            g.kinds_of_rare = '통산기록'
                            g.total_rare_cate = _record.통산종류
                            g.total_rare_nums = _record.통산개수
                            g.total_rare_before_nums = _record.이전경기통산개수
                            if _record.통산기록:
                                Team._rare_hitter = _record.플레이어
                                self._rare_hitter = _record.플레이어

            temp_df = df_hitter[df_hitter['pcode']==pcode]
            before_base = pd.DataFrame(before_game_record)[1:].groupby(['pcode'], as_index=False).sum()
            before_base_num = sum((2*before_base.h2)+(3*before_base.h3)+(4*before_base.hr)+(before_base.hit-before_base.h2-before_base.h3-before_base.hr))

            current_base_num = sum((2*temp_df.h2)+(3*temp_df.h3)+(4*temp_df.hr)+(temp_df.hit-temp_df.h2-temp_df.h3-temp_df.hr))
            base_record_list = [before_base_num + i for i in range(1, current_base_num - before_base_num + 1) if current_base_num > before_base_num]
            for base_record in base_record_list:
                if base_record >= 100 and base_record % 50 == 0:
                    setattr(_record, '통산루타', True)
                    setattr(_record, '통산루타개수', base_record)
                    setattr(_record, '이전경기통산루타', before_base_num)
                    setattr(_record, '코드', temp_df.pcode.values[0])
                    setattr(_record, '이름', temp_df.name.values[0])
                    setattr(_record, '팀', g.team_kor_dict[
                        g.GAME_ID[8:10] if entry[entry.pcode == pcode].team.values[0] == 'T' else g.GAME_ID[10:12]])
                    setattr(_record, '상대팀이름', g.team_kor_dict[
                        g.GAME_ID[8:10] if entry[entry.pcode == pcode].team.values[0] == 'B' else g.GAME_ID[10:12]])
                    setattr(_record, '플레이어', Player(_record.코드, g.GAME_ID[8:10] if entry[entry.pcode == pcode].team.values[0] == 'T' else g.GAME_ID[10:12]))
                    if not g.kinds_of_rare:
                        g.kinds_of_rare = '통산루타'
                        g.total_rare_base_nums = _record.통산루타개수
                        g.total_rare_base_before_nums = _record.이전경기통산루타
                        if _record.통산루타:
                            Team._rare_hitter = _record.플레이어
                            self._rare_hitter = _record.플레이어

        print(getattr(_record, '통산기록'),)

        print(getattr(_record, '통산루타'),)
        
        return _record

    def game_date(self):
        """
        당일날짜
        :return:
        """

        Date = namedtuple('game_date', ['월', '일'])
        g_day = Date("%d" % int(g.GAME_ID[4:6]), "%d" % int(g.GAME_ID[6:8]))
        return g_day

    def set_class_variables(self):
        """
        변수 셋팅
        :return:
        """
        self.away_team_info = Team(g.AWAY_ID)
        self.home_team_info = Team(g.HOME_ID)
        self.game_year = g.GAME_YEAR  # 당일년도
        self.is_winning_hit = self.get_winning_hit()

    @staticmethod
    def stadium_kor():
        """
        구장이름
        :return:
        """
        return g.game_info.stadium

    def league_name(self):
        """
        리그명
        :return:
        """
        return g.LEAGUE_KOR

    def get_winning_hit(self):
        # if g.AWAY_SCORE == g.HOME_SCORE:
        #     return False

        if g.b_models.KboEtcgame.objects.filter(gmkey__exact=g.GAME_ID, how='결승타').get().result == '없음':
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
                if d.how in g.HIT or d.how in g.sacrifice:
                    record = d
                    winning_hit_flag = True
                elif game[i - 1].how in g.HIT or game[i - 1].how in g.sacrifice:
                    record = game[i - 1]
                    winning_hit_flag = True
                else:
                    hitter_cd = d.hitter
                    # 10개의 이벤트를 보자 한타석에 10개 이벤트는 안나오겠지
                    for j in range(1, 10):
                        record = game[i + j]
                        if record.hitter == hitter_cd:
                            if record.how in g.HIT or record.how in g.sacrifice:
                                winning_hit_flag = True
                                break
                        else:
                            break

                if winning_hit_flag and record:
                    self.winning_hit_dict = {
                        'hitter': str(record.hitter),
                        'inning': record.inn,
                        'how_kor': g.HOW_KOR_DICT[record.how],
                        'how': record.how,
                        'tb': record.tb,
                    }
                    return True
                else:
                    return False
        return False

    def winning_hit(self):
        """
        결승타
        :return:
        """
        if not self.is_winning_hit:
            return False

        if self.winning_hit_dict:
            WinningHitter = namedtuple('WinningHitter', ['타자'])
            return WinningHitter(HitterRecord(hitter_code=self.winning_hit_dict['hitter']))
        else:
            return False

    def winning_hit_kor(self):
        """
        결승타_종류
        :return:
        """
        if not self.is_winning_hit:
            return False

        if self.winning_hit_dict:
            return self.winning_hit_dict['how_kor']
        else:
            return False

    def winning_hit_inning(self):
        """
        결승타이닝
        :return:
        """
        if not self.is_winning_hit:
            return False

        if self.winning_hit_dict:
            return self.winning_hit_dict['inning']
        else:
            return False

    def winning_point_inning(self):
        """
        결승점이닝
        :return:
        """
        if not g.IS_DRAW:
            game = g.gamecontapp[::-1]

            for i, d in enumerate(game):
                score_gap_count = d.bscore - d.tscore
                if score_gap_count == 0:
                    return d.inn
        return False

    def set_player_record(self):
        """
        탑플레이어 셋팅
        :return:
        """
        for pos, queryset in [('hitter', g.hitters_today.filter(hit__gte=1)), ('pitcher', g.pitchers_today)]:
            for player in queryset:
                if pos == 'hitter':
                    top_point = self.get_hitter_top_point(player)  # 타자 탑포인트
                else:
                    top_point = self.get_pitcher_top_point(player)  # 투수 탑포인트

                self.top_player_list_4_selection.append({
                    'game_id': g.GAME_ID,
                    'pcode': player.pcode,
                    'point': round(top_point, 1),
                    'name': player.name,
                    'posi': pos,
                    'tb': player.tb,
                    'team_code': g.AWAY_ID if player.tb == 'T' else g.HOME_ID,
                })

                top_point = top_point if pos == 'hitter' else 0

                self.top_player_list.append({
                    'game_id': g.GAME_ID,
                    'pcode': player.pcode,
                    'point': round(top_point, 3),
                    'name': player.name,
                    'posi': pos,
                    'tb': player.tb,
                    'team_code': g.AWAY_ID if player.tb == 'T' else g.HOME_ID,
                })

        self.top_player_list_4_selection.sort(key=lambda k: k['point'], reverse=True)
        self.top_player_list.sort(key=lambda k: k['point'], reverse=True)
        get_top_pitcher = self.get_top_pitcher()
        compare_point = list(filter(lambda x: x['pcode'] == get_top_pitcher.player_code, self.top_player_list_4_selection))[0]['point']
        if self.top_player_list[0]['point'] < compare_point:
            if get_top_pitcher.first == '1':
                if get_top_pitcher.win == 'W' and get_top_pitcher.inn2 >= 15 and get_top_pitcher.r <= 3:
                    g.highlight = 2
                else:
                    g.highlight = 1
            else:
                if get_top_pitcher.r == 0:
                    g.highlight = 2
                else:
                    g.highlight = 1
        else:
            g.highlight = 1

        # 기사를 비교하기 위한 투수 탑플레이어와 투수기사를 생성하기 위한 투수 탑플레이어가 다름
        # 생성된 투수 탑플레이어를 기준으로 비교
        top_player_hitter_list = list(filter(lambda x: x['posi'] == 'hitter', self.top_player_list))
        top_player_pitcher_list = list(filter(lambda x: x['posi'] == 'pitcher', self.top_player_list_4_selection))
        g.save_hitter_top_player_to_db(top_player_hitter_list, g.GAME_ID)
        g.save_pitcher_top_player_to_db(top_player_pitcher_list, g.GAME_ID)
        return True

    @staticmethod
    def get_attribute_value(arg):
        try:
            return arg
        except AttributeError:
            return None

    def init_event(self):
        score_place = ['E', 'R', 'H', 'F', 'S', 'I']
        # 지속적인 추가 필요
        ignore = ['RF', 'TO', 'FD', 'FO']
        pa_gamecontapp = []
        number = 0
        temp_gamecontapp = list(g.gamecontapp)
        temp_gamecontapp.reverse()
        while True:
            if number > len(temp_gamecontapp) - 1:
                break
            temp = []
            game = temp_gamecontapp[number]
            temp.append(game)
            if game.place in score_place:
                while True:
                    if game.how == 'HR':
                        break
                    if len(game.bcount) > 0:
                        #  상대 실책
                        if game.bcount[-1] in ['X', 'Y', 'Z']:
                            break
                    number += 1
                    game = temp_gamecontapp[number]
                    if temp[0].how == 'WP':
                        if temp[0].hitter != game.hitter:
                            break

                    if game.how == 'W2':
                        if game.place not in score_place:
                            break

                    if game.how == 'BH':
                        temp.append(game)
                    elif game.how in ignore:
                        continue
                    elif game.how in ['ER', 'SD']:
                        if game.hitname == temp_gamecontapp[number+1].hitname:
                            temp.append(game)
                        else:
                            temp.append(game)
                            break
                    else:
                        temp.append(game)
                        break

            if len(temp) > 0:
                temp.reverse()
                pa_gamecontapp.append(temp)
            number += 1
        pa_gamecontapp.reverse()

        # linked_list
        prev_event = Event()
        event_list = [prev_event]
        for i, pa_game in enumerate(pa_gamecontapp):
            e = Event(pa_game)
            e.prev = prev_event
            prev_event.next = e
            event_list.append(e)
            prev_event = e

        g.EVENT_LIST = event_list[1:]
        g.SCORE_EVENT_DICT = g.get_score_event(g.EVENT_LIST)
        curr_win_tb = ''
        t_score = 0
        b_score = 0
        t_last_score_inn = 0
        b_last_score_inn = 0
        t_score_after = 0
        b_score_after = 0
        win_flow = ''
        for inn in range(1, 26):
            for tb in ['T', 'B']:
                h_inn = "%d%s" % (inn, tb.lower())
                score = self.score_dict["number_%s" % h_inn]
                if score < 0:
                    break
                elif score == 0:
                    continue

                self.half_innings[h_inn] = ScoreScenes(inn, tb)
                self.half_innings[h_inn].score = score
                self.half_innings[h_inn].score_kor = score if score > 1 else ''
                if curr_win_tb == '':
                    self.half_innings[h_inn].first_score = True  # 선취점

                if tb == 'T':  # T의 득점
                    self.half_innings[h_inn].team_score_before = t_score
                    self.half_innings[h_inn].vs_team_score_before = b_score
                    t_last_score_inn = inn
                    t_score_after = t_score + score
                    self.half_innings[h_inn].run_away = (curr_win_tb != 'B')  # 달아남
                    if win_flow == 'B'and t_score_after >= b_score_after and t_score_after != b_score_after:
                        self.half_innings[h_inn].reversal = True  # 역전
                        g.reversal_num += 1
                        g.reversal_inn.append([inn,tb.lower()])
                    self.half_innings[h_inn].chase = (curr_win_tb == 'B' and t_score_after < b_score_after)  # 추격
                    self.half_innings[h_inn].follow = (curr_win_tb == 'B' and t_score_after == b_score_after)  # 따라잡음
                else:  # B의 득점
                    self.half_innings[h_inn].team_score_before = b_score
                    self.half_innings[h_inn].vs_team_score_before = t_score
                    b_last_score_inn = inn
                    b_score_after = b_score + score
                    self.half_innings[h_inn].run_away = (curr_win_tb != 'T')  # 달아남
                    if win_flow == 'T' and t_score_after <= b_score_after and t_score_after != b_score_after:
                        self.half_innings[h_inn].reversal = True  # 역전
                        g.reversal_num += 1
                        g.reversal_inn.append([inn, tb.lower()])
                    self.half_innings[h_inn].chase = (curr_win_tb == 'T' and t_score_after > b_score_after)  # 추격
                    self.half_innings[h_inn].follow = (curr_win_tb == 'T' and t_score_after == b_score_after)  # 따라잡음
                    self.half_innings[h_inn].walk_off = (inn == 9 and t_score >= b_score and t_score_after < b_score_after)  # 끝내기

                self.half_innings[h_inn].t_score = t_score_after
                self.half_innings[h_inn].b_score = b_score_after
                t_score = t_score_after
                b_score = b_score_after
                self.half_innings[h_inn].big_inning = True if score >= 5 else False
                self.half_innings[h_inn].t_final_score = t_score
                self.half_innings[h_inn].b_final_score = b_score
                self.half_innings[h_inn].team_score_after = t_score if tb == 'T' else b_score
                self.half_innings[h_inn].vs_team_score_after = b_score if tb == 'T' else t_score
                self.half_innings[h_inn].score_gap_after = abs(t_score - b_score)
                curr_win_tb = 'T' if t_score > b_score else 'B'
                if t_score > b_score:
                    win_flow = 'T'
                elif t_score < b_score:
                    win_flow = 'B'
                else:
                    pass
                self.half_innings[h_inn].set_define_method()

            if score < 0:
                break
        if t_last_score_inn > b_last_score_inn:
            last_inn = "%dt" % t_last_score_inn
        elif t_last_score_inn < b_last_score_inn:
            last_inn = "%db" % b_last_score_inn
        else:
            last_inn = "%db" % b_last_score_inn
        if self.half_innings:
            self.half_innings[last_inn].last_score_team = True
            self.half_innings[last_inn].last_score = True
        try:
            wr_type = g.b_models.EtcGame.objects.filter(gmkey__exact=g.GAME_ID, how='WR').get().etc1.split(' ')[-1]
            if wr_type == '사구' or wr_type == '4구':
                self.half_innings[last_inn].final_score = True
            self.half_innings[last_inn].set_define_method()
        except ObjectDoesNotExist:
            # self.half_innings[last_inn].final_score = False
            pass

    def get_select_inning(self):
        """
        1. 시작이닝
        2. 마지막이닝
        3. 득점이 가장 많이 발생한 이닝 (시작, 마지막이닝 포함)
        4. WPA로 정렬하여 가장 큰 이닝 (중복x)
        """
        # region [이닝선택]
        half_inning_size = len(self.half_innings)
        selected_inn_list = []
        if half_inning_size >= 4:
            biggest_score_inn = ''
            max_temp = 0
            wpa_list = []

            for k, v in self.half_innings.items():
                # 득점이 가장 많이 발생한 이닝
                if v.score > max_temp:
                    biggest_score_inn = k
                    max_temp = v.score
                # wpa 로 정렬하기 위한 리스트
                wpa_list.append({k: v.wpa_rt})

            selected_inn_list.append(list(self.half_innings.keys())[0])
            selected_inn_list.append(list(self.half_innings.keys())[-1])

            if biggest_score_inn not in selected_inn_list:
                selected_inn_list.append(biggest_score_inn)

            wpa_list.sort(key=lambda x: list(x.values())[0], reverse=True)
            for wpa in wpa_list:
                _inn_key = list(wpa.keys())[0]
                # if _inn_key == biggest_score_inn:
                #     break
                if _inn_key not in selected_inn_list:
                    selected_inn_list.append(_inn_key)
                    break

        elif half_inning_size == 3:
            selected_inn_list = list(self.half_innings.keys())
        elif half_inning_size == 2:
            selected_inn_list.append(list(self.half_innings.keys())[0])
            selected_inn_list.append(list(self.half_innings.keys())[1])
        elif half_inning_size == 1:
            selected_inn_list.append(list(self.half_innings.keys())[0])
        # 20190826 무승부일 경우
        else:
            pass
        # region [결승타 정보]
        if self.winning_hit_dict or self.is_winning_hit:
            winning_hit_inn = '%d%s' % (self.winning_hit_dict['inning'], self.winning_hit_dict['tb'].lower())
            if winning_hit_inn not in selected_inn_list:
                selected_inn_list.append(winning_hit_inn)
        # endregion [결승타 정보]
        # endregion [이닝선택]

        _selected_inn_list = sorted(selected_inn_list, key=lambda x: x[1], reverse=True)
        selected_inn_list = sorted(_selected_inn_list, key=lambda x: x[0])
        return selected_inn_list

    def make_half_inning(self):
        """
        하프이닝
        :param :
        :return:
        """
        result_list = []
        inning_team_list = []
        inning_team_kor_list = []
        jump_list = []
        selected_inn_list = self.get_select_inning()
        if self.winning_hit_dict or self.is_winning_hit:
            _wining_hitter_code = self.winning_hit_dict['hitter']
        else:
            _wining_hitter_code = ''

        winning_hit_used = False
        prev_scene_value = None
        half_inning_scene = HalfInning()
        start_half_inning_list = []
        used_dict = {}
        consecutive_flag_dict = {'t': False, 'b': False}
        away_consecutive_run_inning = self.get_consecutive_run_inning('t', selected_inn_list)
        home_consecutive_run_inning = self.get_consecutive_run_inning('b', selected_inn_list)
        for select_idx, half_inning_key in enumerate(selected_inn_list):
            jump_list.append(False)
            record_string_list = []
            # inn_total_score = 0
            hidden_inning = None
            scene_value = self.half_innings[half_inning_key]
            half_inning_var = NamedVariable()
            if scene_value.reversal:
                jump_list[-1] = True
            setattr(half_inning_var, '득점장면', scene_value)
            setattr(half_inning_var, '이전장면', prev_scene_value)

            # region [연속 득점 표현]
            if not consecutive_flag_dict[half_inning_key[-1]]:
                cons_inning = away_consecutive_run_inning if half_inning_key[-1] == 't' else home_consecutive_run_inning
                if getattr(cons_inning, 'exist') and half_inning_key in getattr(cons_inning, 'list'):
                    consecutive_flag_dict[half_inning_key[-1]] = True
                    setattr(half_inning_var, '연속득점', cons_inning)
            # endregion [연속 득점 표현]

            # region [타선 침묵 표현]
            if select_idx > 0:
                silence_inning = self.get_silence_inning(selected_inn_list[select_idx - 1], half_inning_key)
                if getattr(silence_inning, 'exist'):
                    setattr(half_inning_var, '침묵', silence_inning)
            # endregion [타선 침묵 표현]

            # region [생략이닝 표현]
            if select_idx > 0:
                hidden_inning = self.get_hidden_inning_event(selected_inn_list[select_idx - 1], half_inning_key)
                setattr(half_inning_var, '생략이닝', hidden_inning)
            # endregion [생략이닝 표현]

            # Half inning 표현
            _hitter_record = half_inning_scene.get_player_record_text_v2('개인기록', scene_value.events, used_dict)
            if _hitter_record and True not in list(filter(lambda x: x not in record_string_list, _hitter_record)):
                record_string_list.extend(_hitter_record)

            if not winning_hit_used and not g.IS_DRAW:
                for e in scene_value.events:
                    if e.hitter_code() == _wining_hitter_code and \
                            e.how == self.winning_hit_dict['how'] and \
                            e.inning_num() == self.winning_hit_dict['inning']:
                        setattr(half_inning_var, '결승타존재', True)
                        setattr(half_inning_var, '선수명', e.hitter_name())
                        setattr(half_inning_var, '타격종류', self.winning_hit_dict['how_kor'])
                        setattr(half_inning_var, '타자개인기록_존재', True)
                        winning_hit_used = True
                        scene_value.final_bat = True
                        jump_list[-1] = True
            else:
                setattr(half_inning_var, '결승타존재', False)
                setattr(half_inning_var, '타자개인기록_존재', False)
                scene_value.final_bat = False

            half_text = half_inning_scene.get_half_inning_player_structure(scene_value, used_dict)

            # region [하프이닝 한 문단 생성]
            start_half_inning = g.get_by_name(half_inning_var, '_하프이닝_생략이닝', 'half_inning_dynamic_variable', used_dict)
            if start_half_inning not in start_half_inning_list:
                start_half_inning_list.append(start_half_inning)
                if hidden_inning and select_idx % 2 == 1:
                    setattr(half_inning_var, '하프이닝_생략이닝', '이후 ' + start_half_inning)
                    setattr(half_inning_var, '하프이닝_생략이닝', start_half_inning)
                else:
                    setattr(half_inning_var, '하프이닝_생략이닝', start_half_inning)
            if len(start_half_inning) > 0:
                jump_list[-1] = True
            hitter_record_string = g.get_hitter_record_sentence(record_string_list)
            # setattr(half_inning_var, '이닝총득점', inn_total_score)
            setattr(half_inning_var, '하프이닝_문장', half_text)
            setattr(half_inning_var, '타자개인기록', hitter_record_string)
            if len(hitter_record_string) > 0:
                setattr(half_inning_var, '타자개인기록_존재', True)
                g.used_personal_record = True
                jump_list[-1] = True
            g.set_half_inning_variable(half_inning_var, 'base_half_inning', used_dict)
            v_string = getattr(half_inning_var, '_하프이닝_이닝_문장')
            record_string_list.clear()
            # endregion [하프이닝 한 문단 생성]

            result_list.append(v_string)
            inning_team_list.append(scene_value.team_code)
            inning_team_kor_list.append(scene_value.team_kor)
            prev_scene_value = half_inning_var

        # 문단 연결
        win_team = self.win_team().team_code
        jump = 0
        temp = 0
        used_after = False
        for j in range(1, len(result_list)):
            inn = selected_inn_list[j]
            # if j == 1:
            #     continue
            i = j - temp
            if jump == 1:
                jump = 0
                if '이후' not in result_list[i]:
                    result_list[i] = '이후 ' + result_list[i]
                    used_after = True
                else:
                    pass
                continue
            prev_jump_state = jump_list[i - 1]
            jump_state = jump_list[i]
            prev_team = inning_team_list[i-1]
            team = inning_team_list[i]
            prev_text = result_list[i-1]
            text = result_list[i]

            if prev_jump_state:
                # result_list[i] = '이후 ' + result_list[i]
                continue
            elif len(text) >= 90 or len(prev_text) >= 90:
                continue
            elif jump_state:
                continue

            if prev_team != team:
                if win_team != prev_team:
                    result_list[i - 1] = result_list[i - 1][:-3] + '지만, ' + text
                else:
                    # result_list[i - 1] = result_list[i - 1][:-3] + '고, ' + text
                    continue
                del result_list[i]
                del jump_list[i]
                del inning_team_list[i]
                del inning_team_kor_list[i]
                temp += 1
                jump += 1
            else:
                compare_text = text.split()
                if compare_text[0][:-1] == inning_team_kor_list[i]:
                    compare_text = compare_text[1:]
                compare_text[0] = compare_text[0]+'에는'
                text = " ".join(compare_text)
                if '동점' in text and '동점' in result_list[i-1]:
                    text = text.replace('동점', '다시 동점')
                    current_inn = self.half_innings[inn]
                    prev_score_sentence = "{팀_이전점수}-{홈팀_득점}#로 뒤지던 ".format(팀_이전점수=current_inn.팀_이전점수, 홈팀_득점=current_inn.홈팀_득점) \
                        if inn[-1] == 't' else \
                        "{원정팀_득점}-{팀_이전점수}#로 뒤지던 ".format(원정팀_득점=current_inn.원정팀_득점, 팀_이전점수=current_inn.팀_이전점수)
                    text = prev_score_sentence + text

                if result_list[i - 1][-6:] == '만들었다. ':
                    result_list[i - 1] = result_list[i - 1][:-8] + ', ' + text
                elif result_list[i - 1][-2:] == '로 ':
                    result_list[i - 1] = result_list[i - 1][:-1] + ', ' + text
                else:
                    if '-' in result_list[i-1].split(' ')[-2] or '-' in result_list[i-1].split(' ')[-1]:
                        result_list[i - 1] = result_list[i-1] + text
                    else:
                        if '선취점' in result_list[i - 1]:
                            result_list[i - 1] = result_list[i - 1][:-3] + '고, ' + text
                        else:
                            result_list[i - 1] = result_list[i - 1][:-2] + '고, ' + text
                del result_list[i]
                del jump_list[i]
                del inning_team_list[i]
                del inning_team_kor_list[i]
                temp += 1
                jump += 1

        try:
            if not used_after and '이후' not in result_list[-1]:
                if '이후' in result_list[-2].split('.')[-1] or '이후' in result_list[-2].split('.')[-2]:
                    result_list[-1] = result_list[-1]
                else:
                    result_list[-1] = '이후 ' + result_list[-1]
        except IndexError:
            pass

        try:
            h_graph_text, g.graph_type = self.get_hitter_analysis_data()
            if h_graph_text and self.great_hitter() is not None:
                g.h_graph_exist = True
                result_list.append('[graph]')
        except Exception as e:
            print(e, 'hitter make_half_inning')
        return '\n\n'.join(result_list)

    def get_keep_run_away_inning(self, prev_inning, curr_inning):
        """
        한팀이 계속 리드
        :param prev_inning:
        :param curr_inning:
        :return:
        """
        keep_lead_var = NamedVariable()
        keep_lead_var.exist = False

        half_inning_list = ['%d%s' % (inn, tb) for inn in range(1, 26) for tb in ['t', 'b']]
        curr_inning_idx = half_inning_list.index(curr_inning)
        prev_inning_idx = half_inning_list.index(prev_inning)
        inning_list = half_inning_list[prev_inning_idx: curr_inning_idx]
        prev_inning_list = half_inning_list[:prev_inning_idx]
        prev_t_inning_list = list(filter(lambda x: x[1] == 't', prev_inning_list))
        prev_b_inning_list = list(filter(lambda x: x[1] == 'b', prev_inning_list))
        prev_t_sum_score = sum(list(map(lambda x: int(self.score_dict["number_%s" % x]), prev_t_inning_list)))
        prev_b_sum_score = sum(list(map(lambda x: int(self.score_dict["number_%s" % x]), prev_b_inning_list)))

        lead_tb = 't' if prev_t_sum_score >= prev_b_sum_score else 'b'
        keep_lead = True
        for inning in inning_list:
            _score = self.score_dict["number_%s" % inning]
            if inning[-1] == 't':
                prev_t_sum_score += _score
            else:
                prev_b_sum_score += _score

            _lead_tb = 't' if prev_t_sum_score >= prev_b_sum_score else 'b'

            if lead_tb != _lead_tb:
                keep_lead = False

        if abs(prev_t_sum_score - prev_b_sum_score) < 3 or not keep_lead:
            return keep_lead_var

        keep_lead_var.exist = True
        setattr(keep_lead_var, '존재', True)
        setattr(keep_lead_var, '점수차', abs(prev_t_sum_score - prev_b_sum_score))
        setattr(keep_lead_var, '리드팀', inning_list[-1][0:-1])
        return keep_lead_var

    def get_consecutive_run_inning(self, tb, selected_inning):
        """
        연속득점
        ex) 1b, 4b, 7b 가 뽑혔고 4~7사이가 연속득점일 때,
        앞에있는 이닝일 때만 쓴다. 곧, 4b에 curr_inning 이 해당될 때만 쓴다.
        :return:
        """
        half_inning_list = list(self.half_innings.keys())
        vs_tb = 't' if tb == 'b' else 'b'
        selected_inn = [inn[0] for inn in selected_inning if inn[1] == vs_tb]
        select_inn = [int(inn[0]) for inn in half_inning_list if inn[1] == tb]
        _arr = []
        consecutive_innings = []
        flag = False
        for i, idx in enumerate(range(len(select_inn) - 1)):
            inning = "%d%s" % (select_inn[idx], tb)
            if select_inn[idx] == select_inn[idx + 1] - 1:
                _arr.append(inning)
                if i == len(select_inn) - 2:
                    inning = "%d%s" % (select_inn[idx + 1], tb)
                    _arr.append(inning)
                    flag = True
            elif i > 0 and select_inn[idx] == select_inn[idx - 1] + 1:
                _arr.append(inning)
                flag = True

            if flag:
                consecutive_innings.append(_arr)
                _arr = []
                flag = False

        consecutive_innings.sort(key=lambda x: len(x), reverse=True)

        consecutive_inning_var = NamedVariable()
        consecutive_inning_var.exist = False

        if not consecutive_innings:
            return consecutive_inning_var

        result = consecutive_innings[0]
        vs_inning_contain = list(filter(lambda x: x[0] in selected_inn, result))

        if result and len(vs_inning_contain) == 0:
            consecutive_inning_var.exist = True
            setattr(consecutive_inning_var, '존재', True)
            setattr(consecutive_inning_var, 'list', result)
            setattr(consecutive_inning_var, '시작이닝', result[0][0])
            setattr(consecutive_inning_var, '끝이닝', result[-1][0])
            setattr(consecutive_inning_var, '연속이닝수', len(result))

        return consecutive_inning_var

    def get_silence_inning_V2(self, prev_inning, curr_inning):
        half_inning_list = ['%d%s' % (inn, tb) for inn in range(1, 26) for tb in ['t', 'b']]
        silence_inning_var = NamedVariable()
        s_idx = half_inning_list.index(prev_inning)
        e_idx = half_inning_list.index(curr_inning)
        inning_list = half_inning_list[s_idx + 1:e_idx]

        if len(inning_list) >= 6:
            silence_inning_var.exist = True
            setattr(silence_inning_var, '존재', True)

            early_inning = False not in list(
                map(lambda x: x in inning_list, ['1t', '1b', '2t', '2b', '3t', '3b'])
            )
            middle_inning = False not in list(
                map(lambda x: x in inning_list, ['4t', '4b', '5t', '5b', '6t', '6b'])
            )

            if early_inning:
                setattr(silence_inning_var, '초중반_존재', True)
                setattr(silence_inning_var, '초중반', '초반')
            elif middle_inning:
                setattr(silence_inning_var, '초중반_존재', True)
                setattr(silence_inning_var, '초중반', '중반')

            _start = inning_list[0]
            _end = inning_list[-1]
            silence_inning_var.start_inn = _start
            silence_inning_var.end_inn = _end
            setattr(silence_inning_var, '시작이닝', _start[0:-1])
            setattr(silence_inning_var, '시작초말', '초' if _start[-1] == 't' else '말')
            setattr(silence_inning_var, '끝이닝', _end[0:-1])
            setattr(silence_inning_var, '끝초말', '초' if _end[-1] == 't' else '말')
        else:
            silence_inning_var.exist = False

        return silence_inning_var

    def get_silence_inning(self, prev_inning, curr_inning):
        silence_inning_var = NamedVariable()

        half_inning_list = list(self.half_innings.keys())
        curr_half_inning_idx = half_inning_list.index(curr_inning)
        prev_half_inning_idx = half_inning_list.index(prev_inning)
        hidden_inning_list = half_inning_list[prev_half_inning_idx + 1:curr_half_inning_idx]

        half_inning_list = ['%d%s' % (inn, tb) for inn in range(1, 26) for tb in ['t', 'b']]
        s_idx = half_inning_list.index(prev_inning)
        e_idx = half_inning_list.index(curr_inning)
        inning_list = half_inning_list[s_idx + 1:e_idx]

        if hidden_inning_list:
            silence_inning_var.exist = False
            return silence_inning_var
        else:
            all_half_inning_list = ['%d%s' % (inn, tb) for inn in range(1, 26) for tb in ['t', 'b']]
            s_idx = all_half_inning_list.index(prev_inning)
            e_idx = all_half_inning_list.index(curr_inning)
            silence_inning_list = half_inning_list[s_idx + 1:e_idx]

            if len(silence_inning_list) < 6:
                silence_inning_var.exist = False
                return silence_inning_var

            silence_inning_var.exist = True
            setattr(silence_inning_var, '존재', True)

            early_inning = False not in list(
                map(lambda x: x in inning_list, ['1t', '1b', '2t', '2b', '3t', '3b'])
            )
            middle_inning = False not in list(
                map(lambda x: x in inning_list, ['4t', '4b', '5t', '5b', '6t', '6b'])
            )

            if early_inning:
                setattr(silence_inning_var, '초중반_존재', True)
                setattr(silence_inning_var, '초중반', '초반')
            elif middle_inning:
                setattr(silence_inning_var, '초중반_존재', True)
                setattr(silence_inning_var, '초중반', '중반')

            _start = inning_list[0]
            _end = inning_list[-1]
            silence_inning_var.start_inn = _start
            silence_inning_var.end_inn = _end
            setattr(silence_inning_var, '시작이닝', _start[0:-1])
            setattr(silence_inning_var, '시작초말', '초' if _start[-1] == 't' else '말')
            setattr(silence_inning_var, '끝이닝', _end[0:-1])
            setattr(silence_inning_var, '끝초말', '초' if _end[-1] == 't' else '말')

        return silence_inning_var

    def get_hidden_inning_event(self, prev_inning, curr_inning):
        """
        생략이닝
        :param prev_inning:
        :param curr_inning:
        :return:
        """
        hidden_inning_event = NamedVariable()
        hidden_inning_event.exist = False

        half_inning_list = list(self.half_innings.keys())
        curr_half_inning_idx = half_inning_list.index(curr_inning)
        prev_half_inning_idx = half_inning_list.index(prev_inning)
        hidden_inning_list = half_inning_list[prev_half_inning_idx + 1:curr_half_inning_idx]
        # region 침묵
        if len(hidden_inning_list) == 0:
            setattr(hidden_inning_event, '침묵', True)
            return hidden_inning_event
        # else:

        # endregion 침묵

        # region 양팀득점
        t_get_scored = False
        b_get_scored = False
        for inning in hidden_inning_list:
            if self.half_innings[inning].tb == 'T' and self.half_innings[inning].score > 0:
                t_get_scored = True
            elif self.half_innings[inning].tb == 'B' and self.half_innings[inning].score > 0:
                b_get_scored = True

        if t_get_scored and b_get_scored:
            setattr(hidden_inning_event, '양팀득점', True)
        else:
            setattr(hidden_inning_event, '양팀득점', False)
        # endregion 양팀득점
        # region 상대팀득점
        if curr_inning[-1] == 't' and b_get_scored:
            setattr(hidden_inning_event, '상대팀득점', True)
        elif curr_inning[-1] == 'b' and t_get_scored:
            setattr(hidden_inning_event, '상대팀득점', True)
        else:
            setattr(hidden_inning_event, '상대팀득점', False)
        # endregion 상대팀득점

        hidden_last_inning = self.half_innings[hidden_inning_list[-1]]
        setattr(hidden_inning_event, '득점장면', hidden_last_inning)
        hidden_inning_event.exist = True
        if len(hidden_inning_list) > 1:
            hidden_second_last_inning = self.half_innings[hidden_inning_list[-2]]
            setattr(hidden_inning_event, '이전득점장면', hidden_second_last_inning)
        setattr(hidden_inning_event, '승리팀', self.win_team())
        return hidden_inning_event

    def get_hitter_analysis_data(self):
        hitter_2019 = g.b_models.Hitter.objects.filter(gday__startswith=g.GAME_YEAR, gday__lte=g.GAME_DATE).exclude(
            name="합계")
        # if g.WIN_TB is None:  # 무승부일때 표출할지말지
        #     top_hitter_code, htp = g.models.TopPlayerHitter.objects.filter(game_id=g.GAME_ID).values_list(
        #         'pcode', 'top_point').latest('top_point')
        # else:
        #     top_hitter_code, htp = g.models.TopPlayerHitter.objects.filter(game_id=g.GAME_ID, tb=g.WIN_TB).values_list(
        #         'pcode', 'top_point').latest('top_point')
        # top_pitcher_code, ptp = g.models.TopPlayerPitcher.objects.filter(game_id=g.GAME_ID, tb=g.WIN_TB).values_list(
        # 'pcode', 'top_point').latest('top_point')
        df_hitter_2019 = pd.DataFrame(hitter_2019.values())
        threshold = len(df_hitter_2019.gmkey.unique().tolist())
        game_id = g.GAME_ID
        if threshold > 30:
            rank_is_exist = self.get_hitter_rank_graph(df_hitter_2019, game_id, g.great_hitter)
            if rank_is_exist:
                return rank_is_exist, 'rank'
            else:
                hitter = g.b_models.Hitter.objects.filter(pcode=g.great_hitter, gday__lte=g.GAME_DATE,
                                                          gmkey__startswith=g.GAME_YEAR)
                df_hitter = pd.DataFrame(hitter.values())
                stat_is_exist = self.get_hitter_stat_graph(df_hitter, game_id, g.great_hitter)
                return stat_is_exist, 'stat'

    def get_hitter_rank_graph(self, df_hitter_2019, game_id, hitter_code):
        try:
            rank = HitterRank(df_hitter_2019, game_id, hitter_code)
            is_exist = rank.text()
            return is_exist
        except:
            is_exist = False
            return is_exist

    def get_hitter_stat_graph(self, df_hitter, game_id, top_hitter_code):
        try:
            stat = HitterStat(df_hitter, game_id, top_hitter_code)
            is_exist = stat.text()
            return is_exist
        except:
            is_exist = False
            return is_exist

class NamedVariable:
    pass
