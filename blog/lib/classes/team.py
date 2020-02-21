from blog.lib import globals as g
from blog.lib.classes.event import Event
from blog.lib.sub_classes.vs_team import VsTeam
from blog.lib.classes.player import Player
import pandas as pd
from collections import Counter


class Team(object):
    def __init__(self, team_cd):
        self.team_code = team_cd
        self.game_id = g.GAME_ID
        self.tb = 'T' if self.game_id[8:10] == team_cd else 'B'
        self.gamecontapp = g.gamecontapp
        self.today_hitters = g.hitters_today.filter(tb__exact=self.tb)
        self.today_pitchers = g.pitchers_today.filter(tb__exact=self.tb)
        self.game_scores = None
        self.team_kor = None
        self.vs_team = None
        self.first_run_event = None
        self._win_pitcher = None
        self._first_pitcher = None
        self._save_pitcher = None
        self._is_win_hold_save_all = None
        self._hold_pitchers = None
        self._great_hitter = None
        self.top_pitcher = None  # 투수_탑플레이어
        self._blown_save_pitcher = None
        self.all_players_hit = False  # 전원안타
        self.all_players_run = False  # 전원득점
        self.all_players_rbi = False  # 전원타점
        if g.kinds_of_article:
            self.top_pitcher = self.get_top_pitcher()
        self.name()
        self.set_first_players_all_hit_record()
        self._rare_hitter = ''

        g.define_method(self, g.team_method)

    def set_today_hitters(self):
        self.today_hitters = g.hitters_today.filter(tb__exact=self.tb)

    def set_today_pitchers(self):
        self.today_pitchers = g.pitchers_today.filter(tb__exact=self.tb)

    def set_game_scores(self):
        self.game_scores = g.get_scores_obj(self.team_code).order_by('-gday')

    def name(self):
        """
        이름
        :return:
        """
        if self.team_kor:
            return self.team_kor

        self.team_kor = g.team_kor_dict[self.team_code]
        return self.team_kor

    def win_counter(self):
        """
        승수
        :return:
        """
        counter = 0
        if self.game_scores is None:
            self.set_game_scores()
        for game_count, score in enumerate(self.game_scores):
            if score.gmkey[8:10] == self.team_code and score.tpoint > score.bpoint:
                counter += 1
            elif score.gmkey[10:12] == self.team_code and score.bpoint > score.tpoint:
                counter += 1

        return counter

    def lose_counter(self):
        """
        패수
        :return:
        """
        counter = 0
        if self.game_scores is None:
            self.set_game_scores()
        for game_count, score in enumerate(self.game_scores):
            if score.gmkey[8:10] == self.team_code and score.tpoint < score.bpoint:
                counter += 1
            elif score.gmkey[10:12] == self.team_code and score.bpoint < score.tpoint:
                counter += 1

        return counter

    def consecutive_win(self):
        """
        연승수
        :return:
        """
        counter = 0
        if self.game_scores is None:
            self.set_game_scores()
        for game_count, score in enumerate(self.game_scores):
            if score.gmkey[8:10] == self.team_code and score.tpoint > score.bpoint:
                counter += 1
            elif score.gmkey[10:12] == self.team_code and score.bpoint > score.tpoint:
                counter += 1

            if score.gmkey[8:10] == self.team_code and score.tpoint < score.bpoint:
                break
            elif score.gmkey[10:12] == self.team_code and score.bpoint < score.tpoint:
                break

            # if (game_count + 1) != counter:
            #     break

        return counter

    def consecutive_lose(self):
        """
        연패수
        :return:
        """
        counter = 0
        if self.game_scores is None:
            self.set_game_scores()
        for game_count, score in enumerate(self.game_scores):
            if score.gmkey[8:10] == self.team_code and score.tpoint < score.bpoint:
                counter += 1
            elif score.gmkey[10:12] == self.team_code and score.bpoint < score.tpoint:
                counter += 1

            if score.gmkey[8:10] == self.team_code and score.tpoint > score.bpoint:
                break
            elif score.gmkey[10:12] == self.team_code and score.bpoint > score.tpoint:
                break
            # if (game_count + 1) != counter:
            #     break

        return counter

    def previous_consecutive_win(self):
        """
        직전_연승수
        :return:
        """
        counter = 0
        if self.game_scores is None:
            self.set_game_scores()
        for game_count, score in enumerate(self.game_scores):
            if game_count == 0:
                continue
            if score.gmkey[8:10] == self.team_code and score.tpoint > score.bpoint:
                counter += 1
            elif score.gmkey[10:12] == self.team_code and score.bpoint > score.tpoint:
                counter += 1

            if score.gmkey[8:10] == self.team_code and score.tpoint < score.bpoint:
                break
            elif score.gmkey[10:12] == self.team_code and score.bpoint < score.tpoint:
                break
            else:
                pass

        return counter

    def previous_consecutive_win_draw(self):
        """
        직전_연승_무승부수
        :return:
        """
        counter = 0
        if self.game_scores is None:
            self.set_game_scores()
        draw = False
        for game_count, score in enumerate(self.game_scores):
            if game_count == 0:
                continue
            if score.gmkey[8:10] == self.team_code and score.tpoint > score.bpoint:
                draw = False
                pass
            elif score.gmkey[10:12] == self.team_code and score.bpoint > score.tpoint:
                draw = False
                pass

            if score.gmkey[8:10] == self.team_code and score.tpoint < score.bpoint:
                break
            elif score.gmkey[10:12] == self.team_code and score.bpoint < score.tpoint:
                break
            elif score.tpoint == score.bpoint:
                draw = True
                counter += 1

        counter = counter if not draw else counter - 1

        return counter

    def win_after_games(self):
        """
        승_이후_경기수
        :return:
        """
        counter = 0
        if self.game_scores is None:
            self.set_game_scores()
        for game_count, score in enumerate(self.game_scores):
            if game_count == 0:
                counter += 1
                continue
            if score.gmkey[8:10] == self.team_code and score.tpoint > score.bpoint:
                break
            elif score.gmkey[10:12] == self.team_code and score.bpoint > score.tpoint:
                break
            counter += 1

        return counter

    def win_include_draw(self):
        """
        무승부포함_연승수
        :return:
        """
        var = NamedVariable()
        result_dict = {}
        if self.game_scores is None:
            self.set_game_scores()
        for game_count, score in enumerate(self.game_scores):
            if game_count == 0:
                if g.WIN_TEAM == g.team_kor_dict[self.team_code]:
                    result_dict[score.gmkey] = '승'
                elif g.LOSE_TEAM == g.team_kor_dict[self.team_code]:
                    result_dict[score.gmkey] = '패'
                else:
                    result_dict[score.gmkey] = '무'
                continue
            if score.gmkey[8:10] == self.team_code:
                result_dict[score.gmkey] = '승' if score.tpoint > score.bpoint else '패' if score.tpoint < score.bpoint \
                                           else '무' if score.tpoint == score.bpoint else None
            else:
                result_dict[score.gmkey] = '승' if score.tpoint < score.bpoint else '패' if score.tpoint > score.bpoint \
                    else '무' if score.tpoint == score.bpoint else None
        draw = 0
        win = 0
        for idx, (k, v) in enumerate(result_dict.items()):
            if idx == 0:
                continue
            if v == '무':
                draw += 1
            elif v == '승':
                win += 1
            else:
                break
        temp = list(result_dict.values())[1:idx]
        for i in temp[::-1]:
            if i == '무':
                temp.pop()
            else:
                break

        setattr(var, '승수', Counter(temp)['승'] + 1 if list(result_dict.values())[0] == '승' else Counter(temp)['승'])
        setattr(var, '무승부수', Counter(temp)['무'])

        return var

    def lose_include_draw(self):
        """
        무승부포함_연패수
        :return:
        """
        var = NamedVariable()
        result_dict = {}
        if self.game_scores is None:
            self.set_game_scores()
        for game_count, score in enumerate(self.game_scores):
            if game_count == 0:
                if g.WIN_TEAM == g.team_kor_dict[self.team_code]:
                    result_dict[score.gmkey] = '승'
                elif g.LOSE_TEAM == g.team_kor_dict[self.team_code]:
                    result_dict[score.gmkey] = '패'
                else:
                    result_dict[score.gmkey] = '무'
                continue
            if score.gmkey[8:10] == self.team_code:
                result_dict[score.gmkey] = '승' if score.tpoint > score.bpoint else '패' if score.tpoint < score.bpoint \
                                           else '무' if score.tpoint == score.bpoint else None
            else:
                result_dict[score.gmkey] = '승' if score.tpoint < score.bpoint else '패' if score.tpoint > score.bpoint \
                    else '무' if score.tpoint == score.bpoint else None
        draw = 0
        lose = 0
        for idx, (k, v) in enumerate(result_dict.items()):
            if idx == 0:
                continue
            if v == '무':
                draw += 1
            elif v == '패':
                lose += 1
            else:
                break
        temp = list(result_dict.values())[1:idx]
        for i in temp[::-1]:
            if i == '무':
                temp.pop()
            else:
                break

        setattr(var, '패수', Counter(temp)['패'] + 1 if list(result_dict.values())[0] == '패' else Counter(temp)['패'])
        setattr(var, '무승부수', Counter(temp)['무'])
        return var

    def win_after_draw_games(self):
        """
        승_이후_무승부수
        :return:
        """
        counter = 0
        if self.game_scores is None:
            self.set_game_scores()
        last_draw = 0
        for game_count, score in enumerate(self.game_scores):
            if game_count == 0:
                continue
            if score.gmkey[8:10] == self.team_code and score.tpoint < score.bpoint:
                if last_draw == game_count-1:
                    counter -= 1
                break
            elif score.gmkey[10:12] == self.team_code and score.bpoint < score.tpoint:
                if last_draw == game_count-1:
                    counter -= 1
                break

            if score.bpoint == score.tpoint:
                counter += 1
                last_draw = game_count
            else:
                continue

        return counter

    def lose_after_draw_games(self):
        """
        패_이후_무승부수
        :return:
        """
        counter = 0
        if self.game_scores is None:
            self.set_game_scores()
        last_draw = 0
        for game_count, score in enumerate(self.game_scores):
            if game_count == 0:
                continue
            if score.gmkey[8:10] == self.team_code and score.tpoint > score.bpoint:
                if last_draw == game_count-1:
                    counter -= 1
                break
            elif score.gmkey[10:12] == self.team_code and score.bpoint > score.tpoint:
                if last_draw == game_count-1:
                    counter -= 1
                break

            if score.bpoint == score.tpoint:
                counter += 1
                last_draw = game_count
            else:
                continue

        return counter

    def lose_after_games(self):
        """
        패_이후_경기수
        :return:
        """
        counter = 0
        if self.game_scores is None:
            self.set_game_scores()
        for game_count, score in enumerate(self.game_scores):
            if game_count == 0:
                counter += 1
                continue
            if score.gmkey[8:10] == self.team_code and score.tpoint < score.bpoint:
                break
            elif score.gmkey[10:12] == self.team_code and score.bpoint < score.tpoint:
                break

            counter += 1

        return counter

    def previous_consecutive_lose(self):
        """
        직전_연패수
        :return:
        """
        counter = 0
        if self.game_scores is None:
            self.set_game_scores()
        for game_count, score in enumerate(self.game_scores):
            if game_count == 0:
                continue
            if score.gmkey[8:10] == self.team_code and score.tpoint > score.bpoint:
                break
            elif score.gmkey[10:12] == self.team_code and score.bpoint > score.tpoint:
                break
            else:
                pass

            if score.gmkey[8:10] == self.team_code and score.tpoint < score.bpoint:
                counter += 1
            elif score.gmkey[10:12] == self.team_code and score.tpoint > score.bpoint:
                counter += 1

        return counter

    def previous_consecutive_lose_draw(self):
        """
        직전_연패_무승부수
        :return:
        """

        counter = 0
        if self.game_scores is None:
            self.set_game_scores()
        draw = False
        for game_count, score in enumerate(self.game_scores):
            if game_count == 0:
                continue
            if score.gmkey[8:10] == self.team_code and score.tpoint > score.bpoint:
                break
            elif score.gmkey[10:12] == self.team_code and score.bpoint > score.tpoint:
                break

            if score.gmkey[8:10] == self.team_code and score.tpoint < score.bpoint:
                draw = False
                pass
            elif score.gmkey[10:12] == self.team_code and score.tpoint > score.bpoint:
                draw = False
                pass
            elif score.tpoint == score.bpoint:
                draw = True
                counter += 1

        counter = counter if not draw else counter - 1

        return counter

    def teamrank_daily(self):
        """
        시즌기록
        :return:
        """
        team_name = self.team_kor if self.team_kor != '넥센' else '우리'
        teamrank_daily = g.teamrank_daily_obj.get(team__exact=team_name)
        return teamrank_daily

    def all_players_total_kk(self):
        return

    def get_score(self):
        """
        득점
        :return:
        """
        if self.tb == 'T':
            return g.AWAY_SCORE
        else:
            return g.HOME_SCORE

    def first_run(self):
        """
        첫득점
        :return:
        """
        if self.first_run_event is None:
            for d in self.gamecontapp:
                if self.tb == 'B':
                    if d.bscore > 0:
                        self.first_run_event = Event([d])
                        break
                else:
                    if d.tscore > 0:
                        self.first_run_event = Event([d])
                        break

        return self.first_run_event

    def highest_hit_rbi(self):
        """
        최고안타타점
        :return:
        """
        if self.today_hitters is None:
            self.set_today_hitters()

        return self.today_hitters.order_by('-rbi').values()[0]['rbi']

    def highest_hit_rbi_hitters(self):
        """
        최고안타타점선수들
        :return:
        """
        if self.today_hitters is None:
            self.set_today_hitters()

        names = self.today_hitters.filter(rbi__exact=self.highest_hit_rbi()).values('name')
        result_list = []
        for n in names:
            result_list.append(n['name'])
        return ', '.join(result_list)

    def game_ab(self):
        """
        타수
        :return:
        """
        if self.today_hitters is None:
            self.set_today_hitters()

        result_list = self.today_hitters.values('ab')
        total = 0
        for d in result_list:
            total += d['ab']

        return total

    def game_rbi(self):
        """
        타점
        :return:
        """
        if self.today_hitters is None:
            self.set_today_hitters()

        result_list = self.today_hitters.values('rbi')
        total = 0
        for d in result_list:
            total += d['rbi']

        return total

    def game_hr(self):
        """
        홈런수
        :return:
        """
        if self.today_hitters is None:
            self.set_today_hitters()

        result_list = self.today_hitters.values('hr')
        total = 0
        for d in result_list:
            total += d['hr']

        return total

    def game_hit(self):
        """
        안타수
        :return:
        """
        if self.today_hitters is None:
            self.set_today_hitters()

        result_list = self.today_hitters.values('hit')
        total = 0
        for d in result_list:
            total += d['hit']

        return total

    @staticmethod
    def is_draw():
        """
        is_무승부
        :return:
        """
        return g.IS_DRAW

    def is_win(self):
        """
        is_승리
        :return:
        """
        return self.team_kor == g.WIN_TEAM

    def is_lose(self):
        """
        is_패배
        :return:
        """
        return self.team_kor == g.LOSE_TEAM

    def hr_players_num(self):
        """
        홈런선수명수
        :return:
        """
        result_list = self.today_hitters.values('hr')
        counter = 0
        for d in result_list:
            if d['hr'] > 0:
                counter += 1

        return counter

    def vs_team_info(self):
        """
        상대전적
        :return:
        """
        if self.vs_team:
            return self.vs_team

        if self.game_scores is None:
            self.set_game_scores()

        if self.tb == 'B':
            vs_team_code = self.game_id[8:10]
        else:
            vs_team_code = self.game_id[10:12]
        self.vs_team = VsTeam(self.team_code, vs_team_code, self.game_scores)
        return self.vs_team

    def get_top_pitcher(self):
        """
        투수_탑플레이어
        :return:
        """
        top_pitcher = None
        top_player_list = []
        for pitcher in g.pitchers_today:
            top_point = g.get_pitcher_top_point_4_article(pitcher)

            top_player_list.append({
                'pcode': pitcher.pcode,
                'point': round(top_point, 3),
                'tb': pitcher.tb,
                'team_code': g.AWAY_ID if pitcher.tb == 'T' else g.HOME_ID,
            })

        top_player_list.sort(key=lambda k: k['point'], reverse=True)

        for pitcher in top_player_list:
            if pitcher['tb'] == self.tb:
                top_pitcher = Player(pitcher['pcode'], pitcher['team_code'])
                break

        return top_pitcher

    def win_pitcher(self):
        """
        승리투수
        :return:
        """
        if self._win_pitcher:
            return self._win_pitcher
        else:
            if self.today_pitchers is None:
                self.set_today_pitchers()

            if self.is_draw():
                return False
            else:
                w_pitcher = self.today_pitchers.get(wls__exact='W')
                if w_pitcher:
                    self._win_pitcher = Player(w_pitcher.pcode, self.team_code)
                    return self._win_pitcher

        return False

    def first_pitcher(self):
        """
        선발투수
        :return:
        """
        if self._first_pitcher is None:
            if self.today_pitchers is None:
                self.set_today_pitchers()
            first_pitcher = self.today_pitchers.filter(tb__exact=self.tb).get(start__exact='1')
            self._first_pitcher = Player(first_pitcher.pcode, self.team_code)

        return self._first_pitcher

    def great_pitcher(self):
        """
        우수투수
        :return:
        """
        if self._first_pitcher is None:
            first_pitcher = self.first_pitcher()
        else:
            first_pitcher = self._first_pitcher

        if first_pitcher.pitcher().inn2() <= 15:
            return self.win_pitcher() if self._win_pitcher is None else self._win_pitcher
        else:
            return self._first_pitcher

    def is_great_hitter(self):
        """
        is_우수타자
        :return: 
        """
        if self._great_hitter is None:
            self.great_hitter()
        
        if self._great_hitter is None:
            return False
        else:
            return True

    def great_hitter(self):
        """
        우수타자
        :return:
        """
        if self._great_hitter is not None:
            return self._great_hitter
        
        great_list = []
        for hitter in self.today_hitters:
            hit = hitter.hit
            hr = hitter.hr
            rbi = hitter.rbi
            result = hit >= 3 or hr >= 2 or rbi >= 3 or (hit >= 2 and hr >= 1) or (hit >= 2 and rbi >= 2) # TODO 조건정리 19.06.20
            if result:
                great_list.append({
                    'pcode': hitter.pcode,
                    'point': hit + (rbi * 1.2) + (hr * 1.5)
                })
                g.great_hitter = hitter.pcode
        if great_list:
            great_list.sort(key=lambda x: x['point'], reverse=True)
            self._great_hitter = Player(great_list[0]['pcode'], self.team_code)
            return self._great_hitter

    def rare_hitter(self):
        """
        진기록타자
        :return:
        """
        return self._rare_hitter

    def is_win_hold_save_all(self):
        """
        is_승홀세
        :return:
        """
        if self._is_win_hold_save_all is None:
            if self.today_pitchers is None:
                self.set_today_pitchers()
            sv_pitcher = self.today_pitchers.filter(wls__exact='S')
            hold_pitcher = self.today_pitchers.filter(hold__exact=1)
            w_pitcher = self.win_pitcher()
            self._is_win_hold_save_all = sv_pitcher.count() > 0 and hold_pitcher.count() > 0 and w_pitcher is not None
        return self._is_win_hold_save_all

    def hold_pitchers(self):
        """
        홀드투수목록
        :return:
        """

        if self._hold_pitchers is None:
            if self.today_pitchers is None:
                self.set_today_pitchers()
            self._hold_pitchers = []
            hold_pitchers_data = self.today_pitchers.filter(hold__exact=1).order_by('pos')
            if hold_pitchers_data.count() > 0:
                for hold_pitcher in hold_pitchers_data:
                    self._hold_pitchers.append(Player(hold_pitcher.pcode, self.team_code))

        return self._hold_pitchers

    def hold_pitcher(self):
        return self._hold_pitchers[0]

    def hold_pitchers_sentence(self):
        """
        홀드투수목록_문장
        :return:
        """
        s_list = []
        for hold_pitcher in self._hold_pitchers:
            er = hold_pitcher.pitcher().er()
            name = hold_pitcher.name()
            inn2 = str(round(hold_pitcher.inn2 / 3, 1))
            r = hold_pitcher.r
            if inn2[-1] == str(3):
                if float(inn2) < 1:
                    inn2 = '⅓'
                else:
                    inn2 = inn2[-len(inn2):-2] + ' ⅓'
            elif inn2[-1] == str(6) or inn2[-1] == str(7):
                if float(inn2) < 1:
                    inn2 = '⅔'
                else:
                    inn2 = inn2[-len(inn2):-2] + ' ⅔'
            else:
                inn2 = str(int(float(inn2)))
            if er > 0:
                s_list.append("{}({}이닝 {}실점({}자책))".format(
                    name,
                    inn2,
                    r if r > 0 else '무',
                    er,
                ))
            else:
                s_list.append("{}({}이닝 {}실점)".format(
                    name,
                    inn2,
                    r if r > 0 else '무',
                ))
        if len(s_list) == 2:
            result = ', '.join(['#과 '.join(s_list[:2])]) + '의 홀드, '
        else:
            result = ', '.join(['#과 '.join(s_list[:2]), ', '.join(s_list[2:])]) + '의 홀드, '
        result = g.get_josa(result)
        return result


    def hold_pitchers_size(self):
        """
        홀드투수목록수
        :return:
        """
        return len(self.hold_pitchers())

    def save_pitcher(self):
        """
        세이브투수
        :return:
        """
        if self._save_pitcher is None:
            if self.today_pitchers is None:
                self.set_today_pitchers()
            sv_pitcher = self.today_pitchers.get(wls__exact='S')
            if sv_pitcher:
                self._save_pitcher = Player(sv_pitcher.pcode, self.team_code)  # g.PLAYERS_DICT[sv_pitcher.pcode]

        return self._save_pitcher
    
    def blown_save(self):
        """
        블론세이브투수
        :return:
        """
        var = NamedVariable()
        if self._save_pitcher is None:
            if self.today_pitchers is None:
                self.set_today_pitchers()
            bsv_pitcher = self.today_pitchers.get(score__exact=1)
            if bsv_pitcher:
                self._blown_save_pitcher = Player(bsv_pitcher, self.team_code)
                this_season_bsv = g.b_models.Pitcher.objects.filter(name=bsv_pitcher.name, score__exact=1,
                                                                    gday__startswith='2019')
                setattr(var, '올시즌개수', len(this_season_bsv))
        return self._blown_save_pitcher

    def set_first_players_all_hit_record(self):
        """
        선발전원_안타_득점_타점
        :return:
        """
        hit_dict = {'hit': True, 'run': True, 'rbi': True}
        for hitter in self.today_hitters:
            if hitter.turn[0] == '1':
                if hitter.hit == 0:
                    hit_dict['hit'] = False

                if hitter.run == 0:
                    hit_dict['run'] = False

                if hitter.rbi == 0:
                    hit_dict['rbi'] = False

        self.all_players_hit = hit_dict['hit']
        self.all_players_run = hit_dict['run']
        self.all_players_rbi = hit_dict['rbi']

    def get_all_players_record_kor(self):
        """
        전원기록
        :return:
        """
        var = NamedVariable()
        result_kor = []
        if self.all_players_hit:
            result_kor.append('안타')
        if self.all_players_rbi:
            result_kor.append('타점')
        if self.all_players_run:
            result_kor.append('득점')

        setattr(var, '무엇', ', '.join(result_kor))

        team_hitters = g.b_models.Hitter.objects.filter(gday__lte=g.GAME_DATE, turn__startswith='1').exclude(pcode__in=['T', 'B']).extra(
            where=[
                "((substring(gmkey, 9, 2) = '{0}' and tb = 'T') or (substring(gmkey, 11, 2) = '{0}' and tb = 'B'))".format(self.team_code),
                ]
        )

        p_teams = g.b_models.Pitcher.objects.filter(gmkey=g.GAME_ID, tb__exact=g.WIN_TB).exclude(name='합계')
        team_kk = sum([p_teams[i].kk for i in range(len(p_teams))]) if len(p_teams) > 0 else 0
        p_other_teams = g.b_models.Pitcher.objects.filter(gday__lte=g.GAME_DATE, name='합계', gday__startswith='2019')
        # p_other_teams = g.b_models.Pitcher.objects.filter(gday__lte=g.GAME_DATE, name='합계')
        df_p_other_teams = pd.DataFrame(list(p_other_teams.values()))
        max_kk = df_p_other_teams.kk.max()
        setattr(var, '최다팀삼진', False)
        if team_kk >= max_kk:
            setattr(var, '최다팀삼진', True)
            setattr(var, '삼진수', team_kk)
            setattr(var, '투수몇명', len(p_teams))
            if team_kk == max_kk:
                setattr(var, '최다타입', '최다 타이')
            else:
                setattr(var, '최다타입', '최다')

        result_count = 0
        df_team_group = pd.DataFrame(list(team_hitters.values())).groupby(['gmkey'])
        for df_team in df_team_group:
            # var_name = d[0][1]  # name key
            df_data = df_team[1]

            if self.all_players_hit and self.all_players_run and self.all_players_rbi:
                if False not in list(df_data['hit'] > 0) and False not in list(df_data['run'] > 0) and False not in list(df_data['rbi'] > 0):
                    if result_count == 0:
                        setattr(var, '첫번째기록날짜', self.get_all_players_record_first_gmkey(df_data))
                    result_count += 1
            elif self.all_players_hit and self.all_players_run:
                if False not in list(df_data['hit'] > 0) and False not in list(df_data['run'] > 0):
                    if result_count == 0:
                        setattr(var, '첫번째기록날짜', self.get_all_players_record_first_gmkey(df_data))
                    result_count += 1
            elif self.all_players_hit and self.all_players_rbi:
                if False not in list(df_data['hit'] > 0) and False not in list(df_data['rbi'] > 0):
                    if result_count == 0:
                        setattr(var, '첫번째기록날짜', self.get_all_players_record_first_gmkey(df_data))
                    result_count += 1
            elif self.all_players_run and self.all_players_rbi:
                if False not in list(df_data['run'] > 0) and False not in list(df_data['rbi'] > 0):
                    if result_count == 0:
                        setattr(var, '첫번째기록날짜', self.get_all_players_record_first_gmkey(df_data))
                    result_count += 1
            elif self.all_players_hit:
                if False not in list(df_data['hit'] > 0):
                    if result_count == 0:
                        setattr(var, '첫번째기록날짜', self.get_all_players_record_first_gmkey(df_data))
                    result_count += 1
            elif self.all_players_run:
                if False not in list(df_data['run'] > 0):
                    if result_count == 0:
                        setattr(var, '첫번째기록날짜', self.get_all_players_record_first_gmkey(df_data))
                    result_count += 1
            elif self.all_players_rbi:
                if False not in list(df_data['rbi'] > 0):
                    if result_count == 0:
                        setattr(var, '첫번째기록날짜', self.get_all_players_record_first_gmkey(df_data))
                    result_count += 1

        setattr(var, '몇번', result_count)

        return var

    def get_all_players_record_first_gmkey(self, df):
        first_record_gmkey = df['gmkey'].values[0]
        frg = '%s년 %s월 %s일 %s전' % (first_record_gmkey[:4], first_record_gmkey[5:6],
                                   first_record_gmkey[6:8],
                                   g.team_kor_dict[first_record_gmkey[8:10]] if first_record_gmkey[
                                                                                   8:10] != g.WIN_TEAM else
                                   g.team_kor_dict[first_record_gmkey[10:12]])
        return frg
    
    def slugfest(self):
        """
        타격전
        :return:
        """
        var = NamedVariable()

        hitter_df = pd.DataFrame(g.b_models.Hitter.objects.filter(gmkey__exact=g.GAME_ID).exclude(name='합계').values())
        is_slugfest = True if hitter_df.hit.sum() >= 30 else False
        setattr(var, '타격전', is_slugfest)
        setattr(var, '안타수', hitter_df.hit.sum())

        return var

class NamedVariable:
    pass
