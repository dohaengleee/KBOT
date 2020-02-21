from blog.lib import globals as g
from blog.lib.sub_classes.hitter_record import HitterRecord
from blog.lib.sub_classes.pitcher_record import PitcherRecord
# from blog.lib.sub_classes.exceptional_record import ExceptionalRecord

class Event:
    def __init__(self, event_list=None):
        self.prev = None
        self.next = None
        self.how = None
        self.how_list = []
        self.er_list = []
        self.er_index = []
        self.er_place_list = []
        self.cause_event = None
        self.last_event = None
        self.raw_event_list = event_list
        # setattr(self, '이벤트', g.EVENT)
        if self.raw_event_list:
            try:
                self.set_event()
            except Exception as e:
                print(e)
            g.define_method(self, g.event_method)
            for k, v in g.VARIABLE_DICT['event_dynamic_variable'].items():  #todo 속도저하 부분 Update 필요
                setattr(self, k, v)

    # 구조 변경이 필요하다.!!!! 이벤트는 점수별로 나누고, 하프이닝은 이닝별이다.
    def set_event(self):
        _event_list = []
        if len(self.raw_event_list) == 1:
            self.cause_event = self.raw_event_list[0]
            self.last_event = self.raw_event_list[-1]
            self.how = self.cause_event.how
            return

        for i, e in enumerate(self.raw_event_list):
            _how = e.how
            _place = e.place
            _field = e.field

            if _how in g.hitter_ignore_list:
                continue

            if _how == 'SB' and _place not in ['E', 'R', 'H', 'F', 'S', 'I']:
                continue

            # if _how == 'SD' and _place not in ['E', 'R', 'H', 'F', 'S', 'I']:
            #     continue

            if (_how != 'ER'and _how in g.HITTER_HOW_KOR2 and _place not in ['E', 'R', 'H', 'F', 'S', 'I']) or (_how == 'ER' and _place in ['E', 'R', 'H', 'F', 'S', 'I']) and 'E' in e.field:
                # if _event_list:
                self.er_list.append(_how)
                self.er_index.append(i)
                self.er_place_list.append(_place)
                # self.how_list.append(e.how)
                # continue

            self.how_list.append(_how)

            # daehyuk 20190812 - 20190811KTOB0 - '선택수비' 이전 상황 확인 및 적용
            if _how == 'RF' and len(self.raw_event_list) > 1 and self.raw_event_list[0].how != 'RF':
                self.how_list.append(self.raw_event_list[0].how)

            _event_list.append(e)
        if _event_list:
            self.cause_event = _event_list[0]
            self.last_event = _event_list[-1]
            self.how = self.cause_event.how
        else:
            self.cause_event = self.raw_event_list[-1]
            self.last_event = self.raw_event_list[-1]
            self.how = self.cause_event.how

        if self.how in ['BK', 'B2', 'W2', 'WP']:
            while self.er_list and self.er_list[-1] in ['BK', 'B2', 'W2', 'WP']:
                self.er_list.pop()

    def hitter(self):
        return HitterRecord(self.cause_event.hitter)

    def hitter_recorder(self):
        """
        타자기록
        :return:
        """
        return HitterRecord(self.cause_event.hitter, season=True, how=self.how)

    def hitter_name(self):
        return self.cause_event.hitname

    def tb(self):
        return self.cause_event.tb

    def score_diff(self):
        """
        득점
        :return:
        """
        score = 0
        for e in self.raw_event_list:
            if e.place in ['E', 'R', 'H', 'F', 'S', 'I']:
                score += 1
        return score

        # try:
        #     if self.last_event.tb == 'T':
        #         curr_score = self.last_event.tscore
        #     else:
        #         curr_score = self.last_event.bscore
        #
        #     if self.prev.last_event is None:
        #         prev_score = 0
        #     else:
        #         if self.last_event.tb == 'T':
        #             prev_score = self.prev.last_event.tscore
        #         else:
        #             prev_score = self.prev.last_event.bscore
        #
        #     return curr_score - prev_score
        # except AttributeError:
        #     return False

    def hitter_code(self):
        return self.cause_event.hitter

    def pitcher_code(self):
        return self.cause_event.pitcher

    def pitcher_recorder(self):
        """
        투수기록
        :return:
        """
        return PitcherRecord(self.cause_event.pitcher)

    def is_hit(self):
        """
        is_안타
        :return:
        """
        return self.cause_event.how in ['H1', 'H2', 'H3', 'HI', 'HB']

    def is_hr(self):
        """
        is_홈런
        :return:
        """
        return self.cause_event.how == 'HR'

    def rbi(self):
        """
        타점
        :return:
        """
        pass

    def hit_name(self):
        """
        타격종류
        :return:
        """
        if self.how in g.HITTER_HOW_KOR:
            return g.HITTER_HOW_KOR[self.how]

    def how_hash(self):
        if self.how in g.HITTER_HOW_KOR2:
            return g.HITTER_HOW_KOR2[self.how]

    def prev_score_this_event_attack(self):
        """
        직전_공격팀점수
        :return:
        """
        pass

    def prev_score_this_event_defense(self):
        """
        직전_수비팀점수
        :return:
        """
        pass

    def prev_score_win(self):
        """
        직전_승리팀점수
        :return:
        """
        pass

    def prev_score_lose(self):
        """
        직전_패배팀점수
        :return:
        """
        pass

    def start_out_count_to_kor(self):
        """
        직전_아웃상황
        :return:
        """
        if self.cause_event.ocount == '0':
            result = '무'
        elif self.cause_event.ocount == '4':
            result = str(g.get_event_out_count(self))
        else:
            result = self.cause_event.ocount
        if result == '0':
            result = '무'
        return result

    def start_out_count(self):
        """
        직전_아웃숫자
        :return:
        """
        return self.cause_event.ocount

    def base_before(self):
        base_list = []
        if self.cause_event.base1b:
            base_list.append(1)
        if self.cause_event.base2b:
            base_list.append(2)
        if self.cause_event.base3b:
            base_list.append(3)
        return base_list

    def base_before_str(self):
        """
        직전_주루상황
        :return:
        """
        base_list = self.base_before()
        base_sum = sum(base_list)
        if base_sum == 0:
            return '주자 없는'
        elif base_sum == 6:
            return '만루'
        else:
            return ', '.join(list(map(str, base_list))) + '루'

    def base_before_runner_count(self):
        """
        직전_주자숫자
        :return:
        """
        base_list = self.base_before()
        return len(base_list)

    def tb_to_kor(self):
        """
        직전_초말
        :return:
        """
        return '초' if self.cause_event.tb == 'T' else '말'

    def inning_num(self):
        """
        직전_회
        :return:
        """
        return self.cause_event.inn

    def end_score_attack(self):
        """
        공격팀점수
        :return:
        """
        pass

    def end_score_defense(self):
        """
        수비팀점수
        :return:
        """
        pass

    def end_score_win(self):
        """
        승리팀점수
        :return:
        """
        pass

    def end_score_lose(self):
        """
        패배팀점수
        :return:
        """
        pass

    def how_name(self):
        """
        타석이름
        :return:
        """
        how_list = []
        er_kor_list = []
        how_kor = ''
        if self.er_list:
            for er in self.er_list:
                er_kor_list.append(g.HITTER_HOW_KOR2[er])

        if self.how in g.HITTER_HOW_KOR:
            how_list.append(g.HITTER_HOW_KOR[self.how])
            how_kor = g.HITTER_HOW_KOR[self.how]
        elif self.how in g.HOW_KOR_DICT:
            how_list.append(g.HOW_KOR_DICT[self.how])
            how_kor = g.HOW_KOR_DICT[self.how]

        if self.er_list:
            if list(filter(lambda x: x in ['E', 'R', 'H', 'F', 'S', 'I'], self.er_place_list)):
                how_idx = self.how_list.index(self.how)
                er_before_how = False
                er_after_how = False
                for i, _ in enumerate(self.er_list):
                    if self.er_index[i] < how_idx:
                        er_before_how = True
                    elif self.er_index[i] > how_idx+1:
                        er_after_how = True

                # daehyuk 20190819 - 20190817NCSK0 - 볼넷으로 시작해 실책으로 끝난 경우 BH 개수에 따라 '밀어내기 볼넷', '볼넷' 구분
                if self.how == 'BB' and self.how_list.count('BH') < 3:
                    how_kor = '볼넷'

                if len(er_kor_list) >= 2 and er_after_how:
                    if er_kor_list[0] == how_kor == er_kor_list[-1]:
                        er_string = '연속 %s' % how_kor
                    elif er_kor_list[0] == how_kor:
                        er_string = '연속 %s 이은 %s' % (how_kor, er_kor_list[-1])
                    elif er_kor_list[-1] == how_kor:
                        er_string = '%s#과 연속 %s' % (how_kor, er_kor_list[-1])
                    elif how_idx < self.how_list.index(self.er_list[0], 0):
                        er_string = "%s에 이은 상대 연속 %s" % (how_kor, er_kor_list[-1])
                    else:
                        er_string = "%s#과 %s에 이은 상대 %s" % (er_kor_list[0], how_kor, er_kor_list[-1])
                elif er_kor_list and er_before_how and how_kor:
                    if er_kor_list[0] == how_kor:
                        er_string = '연속 %s' % how_kor
                    else:
                        er_string = '%s#과 상대 %s' % (er_kor_list[0], how_kor)
                elif er_kor_list and er_after_how:
                    if er_kor_list[0] == how_kor:
                        er_string = '%s' % how_kor
                        pass
                    else:
                        er_string = '%s에 이은 상대 %s' % (how_kor, er_kor_list[0])
                elif len(how_list) > 1:
                    er_string = '#과 '.join(how_list)
                else:
                    er_string = how_list[0]
                text = g.get_josa(er_string)
                return text
            else:
                return how_list[0]
        else:
            return how_list[0]

        # if self.cause_event.place not in [1, 2, 3]:
        #     pos = self.cause_event.field.split()[-1][0]
        #     return '%s%s' % (g.POS_KOR[pos], '의 실책')

    def get_wpa_old(self):
        """
        WPA_RT
        :return:
        """
        try:
            hitter_code = self.hitter_code()
            wpa_rt = g.record_matrix_mix.filter(inn_no=self.cause_event.inn) \
                .filter(tb_sc=self.cause_event.tb) \
                .filter(bat_p_id=hitter_code)[0].wpa_rt

            return wpa_rt
        except Exception as e:
            raise Exception('RECORD_MATRIX data Error', e)

    def get_wpa(self):
        result = g.df_record_matrix[
            # (g.df_record_matrix['pitcher'] == self.cause_event.pitcher) & \
            (g.df_record_matrix['hitter'] == self.cause_event.hitter) & \
            (g.df_record_matrix['inn2'] == self.cause_event.inn2) & \
            (g.df_record_matrix['inn'] == self.cause_event.inn) & \
            (g.df_record_matrix['turn'] == self.cause_event.turn) & \
            (g.df_record_matrix['tb'] == self.cause_event.tb)
        ].wpa_rt

        return result.values[0]
        # prev_e = self.prev if self.prev else None
        #
        # curr_we = g.get_we_li(self, 'we')
        # prev_we = g.get_we_li(prev_e, 'we') if prev_e.cause_event else 0
        #
        # if prev_we == 0:
        #     result = 0
        # else:
        #     result = curr_we - prev_we
        #
        # return result
