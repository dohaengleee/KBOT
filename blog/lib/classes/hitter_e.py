from blog.lib import globals as g
import pandas as pd
import random
import re


class Hitter_e_Variables:
    def __init__(self, hitter_code):
        self.hitter_code = hitter_code
        _today_record = g.hitters_today.filter(pcode__exact=self.hitter_code)
        self.today_record = _today_record[0]
        self.tb = self.today_record.tb
        ##############################################
        self.hitter_name = self.today_record.name
        self.index = 1
        self.last_index = self.today_record.hit
        self.ab = self.today_record.ab
        self.hit = self.today_record.hit
        self.hr = self.today_record.hr
        self.rbi = self.today_record.rbi
        self.bb = self.today_record.bb
        ##############################################
        self.pos_events = []
        # self.neg_events = []

    def set_events(self):
        df_gamecontapp = pd.DataFrame(g.gamecontapp.filter(hitter=self.hitter_code).values()).groupby(
            ['hitter', 'inn', 'tb', 'inn2'])

        for (hitter_cd, inn, tb, inn2), game_rows in df_gamecontapp:
            hitter_st = Hitter_e_Structure(game_rows, hitter_cd, inn, inn2, tb, self.hitter_name, self.index, self.last_index,
                                           self.ab, self.hit, self.hr, self.rbi, self.bb)
            if hitter_st.situation == 'hit':
                self.index += 1
                self.pos_events.append(hitter_st)
            else:
                continue
        return

    def get_sentence(self):
        """
        최종문장 생성
        :return:
        """
        self.set_events()
        pos_result = []
        result_list = []
        used_index_list = []
        used_variable_dict = {}
        for idx, e_struct in enumerate(self.pos_events):
            self.set_template(e_struct, used_index_list, used_variable_dict)
            sentence = e_struct.sentence
            pos_result.append(sentence)

        length = len(pos_result)
        for idx, row in enumerate(pos_result):
            if idx == 0:
                result_list.append(row+' ')
            elif idx == length-1:
                result_list.append('\n\n'+row)
            elif idx == length-2:
                result_list.append(g.get_josa(row+'#를 기록했다.'))
            else:
                result_list.append(row+', ')
        return ''.join([result for result in result_list if result])

    def set_template(self, var, used_index_list, used_variable_dict):
        """
        템플릿에 연결하여 문장 생성
        :param var:
        :param used_index_list:
        :return:
        """
        # 나중에 수정
        model = g.MODEL_DICT['base_exceptional']
        dynamic = model.objects
        df_dynamic_group = pd.DataFrame(list(dynamic.values())).groupby(['group', 'name', 'rank'])
        param_dict = {}
        _stop = False
        for d in df_dynamic_group:
            var_name = d[0][1]  # name key
            var_list = d[1].to_dict('record')  # data value list
            random.shuffle(var_list)
            used_key = "%s-%s" % (d[0][1], d[0][2])

            if var_name in var.__dict__:
                continue

            # 중복 검사하는 Dictionary 를 생성한다.
            if var_name != '하프이닝':
                if used_key not in used_variable_dict:
                    used_variable_dict[used_key] = []

            for item in var_list:
                selected_var_dict = item
                # 중복제거
                if var_name == '하프이닝':
                    if selected_var_dict['index'] in used_index_list:
                        continue
                else:
                    if selected_var_dict['index'] in used_variable_dict[used_key]:
                        continue
                if selected_var_dict['use'] == 'F':
                    used_variable_dict[used_key].append(selected_var_dict['index'])
                    continue

                condition = self.get_hitter_e_condition(param_dict, selected_var_dict['condition'], var)

                if condition:
                    # 사용된 index 추가
                    if var_name == '하프이닝':
                        used_index_list.append(selected_var_dict['index'])
                        _stop = True
                    else:
                        used_variable_dict[used_key].append(selected_var_dict['index'])
                        # 중복 저장 리스트 Flush
                        variable_list_length = len(var_list)
                        used_list_length = len(used_variable_dict[used_key])
                        if variable_list_length == used_list_length:
                            used_variable_dict[used_key] = []

                    str_sentence = self.get_hitter_e_string(param_dict, selected_var_dict['sentence'], var)
                    if selected_var_dict['eval'] == 'T':
                        result = eval(str_sentence)
                        setattr(var, selected_var_dict['name'], result)
                    else:
                        result = g.get_josa(str_sentence)
                        setattr(var, selected_var_dict['name'], result)
                    var.sentence = result
                    break
            if _stop and var_name =='하프이닝':
                _stop = False
                break


    @staticmethod
    def get_hitter_e_condition(param_dict, condition, var):
        split_condition = cond = condition
        reg = r"\{(.+?)\}"
        param_list = re.findall(reg, cond)

        if not param_list and condition != 'True':
            return False

        for param in param_list:
            if param not in param_dict:
                p = param.split('.')
                value = g.get_attr(var, p)
                if value == '':
                    value = False

                param_dict.update({param: value})

        for param in param_list:
            split_condition = split_condition.replace("{%s}" % param, "%s" % param_dict[param])

        if eval(split_condition):
            return True
        else:
            return False

    def get_hitter_e_string(self, param_dict, sentence, var):
        result = sentence
        reg = r"\{(.+?)\}"
        param_list = re.findall(reg, result)

        if param_list:
            for param in param_list:
                if param not in param_dict:
                    p = param.split('.')

                    if param == '생략':
                        param_dict.update({param: ''})
                    else:
                        param_dict.update({param: g.get_attr(var, p)})

            for param in param_list:
                result = result.replace("{%s}" % param, "%s" % param_dict[param])

            result = self.get_eval_value(result)

        return result

    @staticmethod
    def get_eval_value(replaced_sentence):
        reg = r"\<(.+?)\>"
        result = replaced_sentence
        s_list = re.findall(reg, replaced_sentence)
        _s_dict = {}
        for s in s_list:
            try:
                result = result.replace("<%s>" % s, "%s" % eval(s))
            except Exception as e:
                print(e)

        return result


class Hitter_e_Structure:
    def __init__(self, df, hitter_cd, inning, inn2, tb, hitter_name, index, last_index, ab, hit, hr, rbi, bb):
        self.hitter = hitter_cd  # 타자코드
        self.hitter_name = hitter_name  # 이름
        self.inning = inning  # 회
        self.scored_scene = []
        self.vs_team = g.team_kor_dict[g.HOME_ID] if tb == 'T' else g.team_kor_dict[g.AWAY_ID]
        self.team = g.team_kor_dict[g.AWAY_ID] if tb == 'T' else g.team_kor_dict[g.HOME_ID]
        self.ab = ab
        self.hit = hit
        self.hr = hr
        self.rbi = rbi
        self.bb = bb
        self.tb = '초' if tb == 'T' else '말'  # 초말
        self.event = self.get_event(df)
        ########################################
        self.score = self.event['score']  # 이닝득점
        self.situation = self.event['situation']  # 상황
        self.outcount = self.event['아웃카운트']  # 아웃카운트
        self.base = self.event['루상황']  # 루상황
        self.turn = self.event['타자번호']  # 타자번호
        self.how = self.event['하우']  # 하우

        self.index = index  # 인덱스
        self.last_index = last_index  # 마지막
        self.scarce_how = g.scarce_how  # 부족한하우
        self.kinds_of_rare = g.kinds_of_rare
        self.total_rare_nums = g.total_rare_nums
        self.total_rare_before_nums = g.total_rare_before_nums
        self.total_rare_cate = g.total_rare_cate
        self.total_rare_base_nums = g.total_rare_base_nums
        self.total_rare_base_before_nums = g.total_rare_base_before_nums
        self.init_kor_caller()

    # region [EVENT]
    def get_event(self, df_data):
        get_scored = ['E', 'R', 'H', 'F', 'S', 'I']
        score = 0
        df_orderd_hitter = df_data.groupby(['hitter'], sort=False)
        hitter_name = ''
        ball_count = ''
        how = ''
        place = ''
        kor_base = ''
        kor_outcount = ''
        kor_turn = ''
        kor_field = ''
        situation = ''

        for hitter_cd, ser_hitter in df_orderd_hitter:
            for idx, ser_data in ser_hitter.iterrows():
                if ser_data['place'] in get_scored:
                    score += 1

                # 득점이지만 how로 고려되지 않을 리스트로 변경 필요
                if ser_data['how'] == 'BH':
                    continue

                # 연속상황 고려할 필요 없음
                if ser_data['ocount'] == '4':
                    continue

                hitter_name = ser_data['hitname']
                ball_count = len(ser_data['bcount'])
                place = ser_data['place']
                how = ser_data['how']
                outcount = str(ser_data['ocount'])
                b1 = '1' if ser_data['base1b'] else ''
                b2 = '2' if ser_data['base2b'] else ''
                b3 = '3' if ser_data['base3b'] else ''
                base = b1 + b2 + b3
                kor_turn = str(ser_data['turn'][-1]) + '번타자'
                # field와 수비 추가
                field = ser_data['field'].strip()
                if len(field) > 0:
                    # 삼진은 수비 없음
                    if how == 'KK':
                        kor_field = ''
                    else:
                        field = re.findall(r'\d', field)[0]
                        kor_field = g.defense_kor_dict[field]
                else:
                    kor_field = ''

                # 아웃카운트 한글화
                if outcount == '0':
                    kor_outcount = '무사'
                else:
                    kor_outcount = str(outcount) + '사'

                # 주자 상황
                if len(base) == 1:
                    kor_base = str(base) + '루'
                elif len(base) == 2:
                    kor_base = str(base)[0] + ', ' + str(base)[1] + '루'
                elif len(base) == 3:
                    kor_base = '만루'
                elif len(base) == 0:
                    kor_base = '주자 없는 상황'

                if place in ['0', '1', '2', '3']:
                    situation = 'out'
                elif how in g.HIT:
                    situation = 'hit'

            scene_dict = dict()
            scene_dict['타자이름'] = hitter_name
            scene_dict['ball_count'] = ball_count
            scene_dict['루상황'] = kor_base
            scene_dict['아웃카운트'] = kor_outcount
            scene_dict['하우'] = g.pitcher_how_kor_dict[how]
            scene_dict['how'] = how
            scene_dict['place'] = place
            scene_dict['score'] = score
            scene_dict['타자번호'] = kor_turn
            scene_dict['수비'] = kor_field
            scene_dict['situation'] = situation
            if score > 0:
                self.scored_scene.append(scene_dict)
            score = 0
        return scene_dict
    # endregion [EVENT]

    # region [FUNCTION]
    def init_kor_caller(self):
        kor_dict = {
            '타자코드': 'hitter',
            '이름': 'hitter_name',
            '회': 'inning',
            '초말': 'tb',
            '이닝득점': 'score',
            '팀이름': 'team',
            '상대팀이름': 'vs_team',
            '상황': 'situation',
            '진기록종류': 'kinds_of_rare',
            '인덱스': 'index',
            '마지막': 'last_index',
            '부족한하우': 'scarce_how',
            '아웃카운트': 'outcount',
            '루상황': 'base',
            '타자번호': 'turn',
            '하우': 'how',
            '타수': 'ab',
            '안타': 'hit',
            '홈런': 'hr',
            '타점': 'rbi',
            '볼넷': 'bb',
            '통산개수': 'total_rare_nums',
            '이전통산개수': 'total_rare_before_nums',
            '통산종류': 'total_rare_cate',
            '통산루타': 'total_rare_base_nums',
            '이전통산루타': 'total_rare_base_before_nums',
        }
        for k, v in kor_dict.items():
            setattr(self, k, getattr(self, v))
    # endregion [FUNCTION]