from blog.lib import globals as g
from blog import minor_baseball_models as b_models
from blog.lib.analysis.stat_graph import Stats
from blog.lib.analysis.rank_graph import Rank
import pandas as pd
import random
import re
from collections import OrderedDict


class PitcherVariables:
    def __init__(self, pitcher_code):
        self.pitcher_code = pitcher_code
        _today_record = g.pitchers_today.filter(pcode__exact=self.pitcher_code)
        self.today_record = _today_record[0]
        self.today_is_first = self.today_record.start == '1'
        self.total_score = self.today_record.r
        self.pitcher_name = self.today_record.name
        self.tb = self.today_record.tb
        self.start = self.today_record.start
        self.quit = self.today_record.quit
        if self.quit == '1':
            self.next_pitcher_name = ''
        else:
            self.next_pitcher_name = g.pitchers_today.filter(pos=str(int(self.today_record.pos[0]) + 1) + '1', tb=self.tb)[0].name
        self.today_weather = g.today_weather
        self.game_last_row = g.gamecontapp.filter(gmkey=g.GAME_ID).order_by('-serno').values()[0]
        self.first_inn = 0
        self.events = []
        self.s_dict = dict()

    def set_events(self):
        df_gamecontapp = pd.DataFrame(g.gamecontapp.filter(pitcher=self.pitcher_code).values()).groupby(
            ['pitcher', 'inn', 'tb'])

        first_inn = list(df_gamecontapp.inn.groups.items())[0][0][1]
        self.first_inn = first_inn
        last_inn = list(df_gamecontapp.inn.groups.items())[-1][0][1]

        for (pitcher_cd, inn, tb), game_rows in df_gamecontapp:
            pitcher_st = PitcherStructure(game_rows, pitcher_cd, inn, tb, self.next_pitcher_name, last_inn, first_inn, self.pitcher_name, self.total_score, self.game_last_row)
            self.events.append(pitcher_st)

        return self.events

    def get_sentence(self):
        """
        최종문장 생성
        :return:
        """
        self.set_events()
        result_list = []
        temp_list = []
        used_index_list = []
        used_variable_dict = {}
        ps = []
        inning_idx_123 = []
        inning_123 = []
        idx_number = 0
        s_dict_list = []
        for idx, e_struct in enumerate(self.events):
            self.s_dict = dict()
            self.set_template(e_struct, used_index_list, used_variable_dict)
            sentence = e_struct.sentence

            #  DB조건에 따라 생략되는 문장일 경우 건너뜀
            if len(sentence) == 0:
                continue

            #  문장에서 사용된 타자이름, 하우 ...의 정보
            s_dict_list.append(self.s_dict)

            # 삼자범퇴
            # TODO 190804 삼자범퇴 판별 20190803NCKT0 5회말 outcnt : 4 / HOW : 'GR', 'FL', 'H2', 'TO'
            # is_sjbt = True
            # for i in e_struct.how_list:
            #     if i in g.HIT:
            #         is_sjbt = False
            if e_struct.situation_list == ['out', 'out', 'out'] and e_struct.삼자범퇴:
                inning_idx_123.append(idx_number)
                inning_123.append(e_struct.inning)
            ps.append(e_struct.pos_neg)
            idx_number += 1
            temp_list.append(sentence)

        #  삼자범퇴 연속이닝 판별
        skip = []
        temp = 0
        skip_num = 0
        front_text = ''
        skip_used = False
        if len(inning_idx_123) > 1:
            for i in range(1, len(inning_idx_123)):
                before = inning_idx_123[i - 1]
                current = inning_idx_123[i]
                if before + 1 == current:
                    b_idx = before - temp
                    c_idx = current - temp
                    if before == 0:
                        text = temp_list[b_idx].split()
                        if self.today_is_first:
                            #  {팀이름} 선발투수 {투수이름}#은
                            front_text = " ".join(text[:3]) + " "
                            temp_list[b_idx] = " ".join(text[3:])
                        else:
                            #  {팀이름} {투수이름}#은
                            front_text = " ".join(text[:2]) + " "
                            temp_list[b_idx] = " ".join([text[2][:-1]]+text[3:])
                    if inning_123[i-1]+1 == inning_123[i] and not skip_used:
                        temp_list[b_idx] = temp_list[b_idx].split(" ")[0] + " " + temp_list[c_idx].split(" ")[0] + " 삼자범퇴"
                    else:
                        temp_list[b_idx] = temp_list[b_idx].split(" ")[0] + " " + temp_list[c_idx].split(" ")[0] + " 생략삼자범퇴"
                        skip_used = True
                    del temp_list[c_idx]
                    del ps[c_idx]
                    temp += 1
                    skip_num += 1
                else:
                    if skip_num != 0:
                        skip.append(skip_num)
                        skip_num = 0
                    continue
            if skip_num != 0:
                skip.append(skip_num)
        
        if len(skip) > 0:
            temp_num = 0
            for r_idx, row in enumerate(temp_list):
                if temp_num >= len(skip):
                    result_list.append(row)
                    continue
                if skip[temp_num] == 1:
                    row = row.split(' ')
                    if row[-1] == '삼자범퇴':
                        row[0] = row[0][:-2] + ', '
                        if row[0][0] == str(self.first_inn):
                            row[1] = row[1][:-1] + '를 '
                        else:
                            row[1] = row[1][:-1] + '는 '
                        if r_idx + 1 == len(temp_list):
                            if self.events[-1].next_pitcher != '':
                                row[-1] = """연속 삼자범퇴로 좋은 구위를 보여주었고, {next_inn}회{tb} {next_pitcher}#로 교체되며 마운드에서 물러났다.""".format(
                                    next_inn=self.events[-1].next_inning, tb=self.events[-1].tb,
                                    next_pitcher=self.events[-1].next_pitcher)
                            else:
                                if g.is_called:
                                    row[-1] = "연속 삼자범퇴로 좋은 구위를 보여주었고, {날씨}#로 인한 콜드 게임으로 경기가 마무리 됐다.".format(날씨=self.today_weather)
                                else:
                                    row[-1] = "연속 삼자범퇴로 좋은 구위를 보여주며 경기를 마무리 했다. "
                        elif r_idx == 0:
                            row[-1] = '연속 삼자범퇴로 막아내며 기분 좋은 출발을 했다.'

                        else:
                            row[-1] = '연속 삼자범퇴로 좋은 구위를 보여주었다.'
                        temp_num += 1

                    elif row[-1] == '생략삼자범퇴':
                        row[0] = row[0] + '부터'
                        row[1] = row[1] + '까지'
                        if r_idx + 1 == len(temp_list):
                            if self.events[-1].next_pitcher != '':
                                row[-1] = """실점을 허용하지 않았고, {next_inn}회{tb} {next_pitcher}#로 교체되며 마운드에서 물러났다.""".format(
                                    next_inn=self.events[-1].next_inning, tb=self.events[-1].tb,
                                    next_pitcher=self.events[-1].next_pitcher)
                            else:
                                if g.is_called:
                                    row[-1] = "실점을 허용하지 않았고, {날씨}#로 인한 콜드 게임으로 경기가 마무리 됐다.".format(날씨=self.today_weather)
                                else:
                                    row[-1] = "실점을 허용하지 않고 경기를 마무리 했다."
                        elif r_idx == 0:
                            row[-1] = '실점을 허용하지 않으며 기분 좋은 출발을 했다.'
                        else:
                            row[-1] = '실점을 허용하지 않았다.'
                        temp_num += 1
                    row = g.get_josa(" ".join(row))
                    result_list.append(front_text+row)
                    front_text = ''

                else:
                    row = row.split(' ')
                    if row[-1] == '삼자범퇴':
                        row[0] = row[0] + '부터'
                        row[1] = row[1] + '까지'
                        if r_idx + 1 == len(temp_list):

                            row[0] = '이후 ' + row[0]

                            if self.events[-1].next_pitcher != '':
                                row[-1] = """삼자범퇴로 상대 타선을 막아냈고, {next_inn}회{tb} {next_pitcher}#로 교체되며 마운드에서 물러났다.""".format(
                                    next_inn=self.events[-1].next_inning, tb=self.events[-1].tb,
                                    next_pitcher=self.events[-1].next_pitcher)
                            else:
                                if g.is_called:
                                    row[-1] = "삼자범퇴로 상대 타선을 막아냈고, {날씨}#로 인한 콜드 게임으로 경기가 마무리 됐다.".format(날씨=self.today_weather)
                                else:
                                    row[-1] = "삼자범퇴로 상대 타선을 막아내며 경기를 마무리 했다."
                        elif r_idx == 0:
                            row[-1] = '삼자범퇴로 상대 타선을 막아내며 기분 좋은 출발을 했다.'
                        else:
                            row[-1] = '삼자범퇴로 상대 타선을 막아냈다.'
                        temp_num += 1
                    elif row[-1] == '생략삼자범퇴':
                        row[0] = row[0] + '부터'
                        row[1] = row[1] + '까지'
                        if r_idx + 1 == len(temp_list):
                            if self.events[-1].next_pitcher != '':
                                row[-1] = """실점을 허용하지 않았고, {next_inn}회{tb} {next_pitcher}#로 교체되며 마운드에서 물러났다.""".format(
                                    next_inn=self.events[-1].next_inning, tb=self.events[-1].tb,
                                    next_pitcher=self.events[-1].next_pitcher)
                            else:
                                if g.is_called:
                                    row[-1] = "실점을 허용하지 않았고, {날씨}#로 인한 콜드 게임으로 경기가 마무리 됐다.".format(날씨=self.today_weather)
                                else:
                                    row[-1] = "실점을 허용하지 않고 경기를 마무리 했다."
                        elif r_idx == 0:
                            row[-1] = '실점을 허용하지 않으며 기분 좋은 출발을 했다.'
                        else:
                            row[-1] = '실점을 허용하지 않았다.'
                        temp_num += 1
                    row = g.get_josa(" ".join(row))
                    result_list.append(front_text+row)
                    front_text = ''
        else:
            result_list = temp_list

        # 문단 연결
        temp = 0
        jump = 0
        after_used = False
        for i in range(1, len(ps)):
            true_num = i
            i = i - temp
            #  이전 문단이 연결되었을 경우 건너뜀
            if jump == 1:
                jump = 0
                continue
            if len(result_list[i-1]) > 70:
                continue
            before = ps[i - 1]
            current = ps[i]
            if before == current:
                temp_result = result_list[i].split()
                if temp_result[0][-1] == ('초' or '말'):
                    ran_num = random.random()
                    if ran_num <= 0.5:
                        temp_result[0] = temp_result[0]+'에는 ' if temp_result[0][-1] != ',' else temp_result[0]
                    else:
                        pass
                elif temp_result[0][-1] == ',':
                    temp_result[1] = temp_result[1][:-1]+'에는 '
                result_list[i] = " ".join(temp_result)

                if before == 'N' and '내줬지만' in result_list[i-1]:
                    continue

                #  문장 축약, 이상하면 즉시 주석 or 제거
                elif '타자이름' in s_dict_list[i-1] and '타자이름' in s_dict_list[i]:
                    if s_dict_list[i-1]['타자이름'] == s_dict_list[i]['타자이름']:
                        if '하우' in s_dict_list[i-1] and '하우' in s_dict_list[i]:
                            if s_dict_list[i-1]['하우'] == s_dict_list[i]['하우']:
                                if (' 때 ' in result_list[i-1] and ' 때 ' in result_list[i]) or (' 때 ' not in result_list[i-1] and ' 때 ' not in result_list[i]):
                                    if '에서' in result_list[i-1]:
                                        result_list[i-1] = result_list[i-1].split('에서')[0]
                                    elif '상황' in result_list[i-1]:
                                        result_list[i-1] = result_list[i-1].split('상황')[0]+"상황"
                                    elif '루 ' in result_list[i-1]:
                                        result_list[i-1] = result_list[i-1].split('루')[0]+"루 "

                                    if '에서' in result_list[i]:
                                        result_list[i] = result_list[i].split('에서')[0] + ' 각각 ' + "".join(result_list[i].split('에서')[1:])
                                    elif '상황' in result_list[i]:
                                        result_list[i] = result_list[i].split('상황')[0]+"상황" + ' 각각 ' + "".join(result_list[i].split('상황')[1:])
                                    elif '루 ' in result_list[i]:
                                        result_list[i] = result_list[i].split('루')[0]+"루 " + ' 각각 ' + "".join(result_list[i].split('루 ')[1:])

                                    result_list[i - 1] = result_list[i - 1] + ', ' + result_list[i]
                                    del result_list[i]
                                    del ps[i]
                                    del s_dict_list[i]
                                    temp += 1
                                    jump += 1
                                    continue

                    elif '하우' in s_dict_list[i-1] and '하우' in s_dict_list[i]:
                        if s_dict_list[i-1]['하우'] == s_dict_list[i]['하우']:
                            if (' 때 ' in result_list[i-1] and ' 때 ' in result_list[i]) or (' 때 ' not in result_list[i-1] and ' 때 ' not in result_list[i]):
                                result_list[i-1] = result_list[i-1].split(s_dict_list[i-1]['타자이름'][-1])[0] + s_dict_list[i-1]['타자이름'][-1]
                                result_list[i] = result_list[i].split(s_dict_list[i]['타자이름'][-1])[0] + s_dict_list[i]['타자이름'][-1] + ' 모두' + ("".join(result_list[i].split(s_dict_list[i]['타자이름'][-1])[1:]))[1:]

                                result_list[i - 1] = result_list[i - 1] + ', ' + result_list[i]
                                del result_list[i]
                                del ps[i]
                                del s_dict_list[i]
                                temp += 1
                                jump += 1
                                continue

                if '초에는' in result_list[i] or '말에는' in result_list[i]:
                    pass
                elif '범타' in result_list[i]:  # 임시코드
                    pass
                else:
                    if '루에서' in result_list[i]:
                        count = 0
                        for j in range(len(temp_result)):
                            if '루에서' in temp_result[j]:
                                count += 1
                            if count >= 2:
                                temp_result[j] = temp_result[j][0] + '루에서는'
                                result_list[i] = ' '.join(temp_result)
                                break
                    else:
                        result_list[i] = result_list[i].replace("루에서", "루에서는", 1)

                result_list[i - 1] = result_list[i - 1][:-2] + '고, ' + result_list[i]
                if true_num != 1 and not after_used:
                    result_list[i-1] = '이후 ' + result_list[i-1]
                    after_used = True
                else:
                    after_used = False
                del result_list[i]
                del ps[i]
                del s_dict_list[i]
                temp += 1
                jump += 1
            elif before != current:
                # 연결 어색할 시 건너뛸 수 있음
                ran_num = random.random()
                temp_result = result_list[i].split()
                if '부터' in temp_result[0]:
                    pass
                elif temp_result[0][-1] == ('초' or '말'):
                    if ran_num >= 0.5:
                        temp_result[0] = temp_result[0]+'에는 ' if temp_result[0][-1] != ',' else temp_result[0]
                    else:
                        pass
                elif temp_result[0][-1] == ',':
                    temp_result[1] = temp_result[1][:-1]+'에는 '

                result_list[i] = " ".join(temp_result)

                if '초에는' in result_list[i] or '말에는' in result_list[i]:
                    pass
                else:
                    result_list[i] = result_list[i].replace("루에서", "루에서는", 1)

                if '으나' in result_list[i]:
                    result_list[i - 1] = result_list[i - 1][:-2] + '고, ' + result_list[i]
                elif '지만' in result_list[i]:
                    result_list[i - 1] = result_list[i - 1][:-2] + '고, ' + result_list[i]
                elif '지만' in result_list[i-1]:
                    result_list[i - 1] = result_list[i - 1][:-2] + '고, ' + result_list[i]
                else:
                    result_list[i - 1] = result_list[i - 1][:-2] + '지만, ' + result_list[i]

                if true_num != 1 and not after_used:
                    result_list[i - 1] = '이후 ' + result_list[i - 1]
                    after_used = True
                else:
                    after_used = False

                del result_list[i]
                del ps[i]
                del s_dict_list[i]
                temp += 1
                jump += 1

        try:
            graph_text, g.graph_type = self.get_pitcher_anaysis_data()
            if graph_text:
                g.graph_exist = True
                result_list.append('[graph]')
        except Exception as e:
            print(e, 'pitcher get_sentence 경기수 부족')
            pass

        return '\n\n'.join([result for result in result_list if result])

    def set_template(self, var, used_index_list, used_variable_dict):
        """
        템플릿에 연결하여 문장 생성
        :param var:
        :param used_index_list:
        :return:
        """
        model = g.MODEL_DICT['base_pitcher']
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
                    if var_name == '하프이닝':
                        used_index_list.append(selected_var_dict['index'])
                    else:
                        used_variable_dict[used_key].append(selected_var_dict['index'])
                    continue

                condition = self.get_pitcher_condition(param_dict, selected_var_dict['condition'], var)

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

                    str_sentence = self.get_pitcher_string(param_dict, selected_var_dict['sentence'], var)
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
    def get_pitcher_condition(param_dict, condition, var):
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

    def get_pitcher_string(self, param_dict, sentence, var):
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
            #  문장에서 사용된 타자이름, 하우 ...의 정보
            dic = result[1]
            self.s_dict.update(dic)
            return result[0]
        else:
            return result


    @staticmethod
    def get_eval_value(replaced_sentence):
        reg = r"\<(.+?)\>"
        result = replaced_sentence
        s_list = re.findall(reg, replaced_sentence)
        _s_dict = {}
        for s in s_list:
            try:
                eval_s = eval(s)
                key = "".join(re.findall('[가-힣]', s.split('[')[-1].split(']')[0]))
                if key in _s_dict:
                    _s_dict[key] += [eval_s]
                else:
                    _s_dict[key] = [eval_s]

                result = result.replace("<%s>" % s, "%s" % eval_s)
            except Exception as e:
                print(e, result)
        return result, _s_dict

    def get_pitcher_anaysis_data(self):
        #TODO 2018년도 추가
        pitcher_2019 = b_models.Pitcher.objects.filter(gday__startswith=g.GAME_YEAR, gday__lte=g.GAME_DATE).exclude(name="합계")
        df_pitcher_2019 = pd.DataFrame(pitcher_2019.values())
        threshold = len(df_pitcher_2019.gmkey.unique().tolist())
        if threshold > 30:
            rank_is_exist = self.get_rank_graph(df_pitcher_2019, g.GAME_ID, self.pitcher_code)
            if rank_is_exist:
                return rank_is_exist, 'rank'
            else:
                pitcher = b_models.Pitcher.objects.filter(pcode=self.pitcher_code, gday__lte=g.GAME_DATE)
                df_pitcher = pd.DataFrame(pitcher.values())
                stat_is_exist = self.get_pitcher_graph(df_pitcher, g.GAME_ID)
                return stat_is_exist, 'stat'

        # with ProcessPoolExecutor(max_workers=2) as executor:
        #     graph = executor.submit(self.test)
        #     # graph = executor.submit(self.get_pitcher_graph, (df_pitcher, g.GAME_ID))
        #     # sentence = executor.submit(self.get_sentence, ())
        #     print(graph.done())
        #     print(graph.result())
        #     print('done')
        #     # print(wait(graph))

    def get_rank_graph(self, df_pitcher_2019, game_id, pitcher_code):
        try:
            rank = Rank(df_pitcher_2019, game_id, pitcher_code)
            is_exist = rank.text()[0]
            return is_exist
        except:
            is_exist = False
            return is_exist

    def get_pitcher_graph(self, df_pitcher, game_id):
        stats = Stats(game_id, df_pitcher, self.pitcher_name)
        stat_is_exist = stats.cumulative_text()[0]
        return stat_is_exist
        # except Exception as e:
        #     print(e)
        #     return article


class PitcherStructure:
    def __init__(self, df, pitcher_cd, inning, tb, next_pitcher, last_inn, first_inn, pitcher_name, total_score, game_last_row):
        self.pitcher = pitcher_cd  # 투수코드
        self.pitcher_name = pitcher_name  # 이름
        self.inning = inning  # 회
        self.next_inning = inning + 1  # 다음회
        self.scored_scene = []
        self.vs_team = g.team_kor_dict[g.HOME_ID] if tb == 'B' else g.team_kor_dict[g.AWAY_ID]
        self.team = g.team_kor_dict[g.AWAY_ID] if tb == 'B' else g.team_kor_dict[g.HOME_ID]
        self.tb = '초' if tb == 'T' else '말'  # 초말
        self.event = self.get_event(df)  ##########################################
        self.score = sum(list(map(lambda x: x['score'], self.event)))  # 이닝실점
        self.situation_list = list(map(lambda x: x['situation'], self.event))  # 전체진루상황
        self.first_how = list(map(lambda x: x['첫번째하우'], self.event))  # 첫번째하우
        self.base_list = list(map(lambda x: x['base'], self.event))  # 전체주자상황
        self.how_list = list(map(lambda x: x['how'], self.event))  # how리스트
        self.is_triceps = self.is_triceps()
        self.all_how_list = list(map(lambda x: x['모든하우'], self.event))[0]
        self.all_field_list = list(map(lambda x: x['모든필드'], self.event))[0]
        self.is_oob = self.is_oob()
        self.bcount_list = list(map(lambda x: x['ball_count'], self.event))  # 공갯수리스트
        self.bcount = sum(self.bcount_list)  # 공갯수
        self.out_list = list(filter(lambda x: x['situation'] == 'out' or x['situation'] == 'pos', self.event))  # 아웃상황
        self.set_out_list = list(OrderedDict.fromkeys(list(map(lambda x: x['하우'], self.out_list))))  # 중복제거아웃
        self.hit_list = list(filter(lambda x: x['situation'] == 'hit', self.event))  # 안타상황
        self.onbase_list = list(filter(lambda x: x['situation'] == 'onbase', self.event))  # 온베이스상황
        self.hr_list = list(filter(lambda x: x['how'] == 'HR', self.event))  # 홈런상황
        self.score_list = list(filter(lambda x: x['score'] > 0, self.event))  # 실점상황
        self.out_score_list = list(map(lambda x: x['situation'] == 'out', self.score_list))  # 아웃실점
        self.hitter_list = ', '.join(list(map(lambda x: x['타자이름'], self.hit_list)))  # 안타타자리스트
        self.scene = ''
        self.hitters_kor = ', '.join(list(map(lambda x: x['타자이름'], self.event)))  # 타자리스트
        self.hitters_code = ', '.join(list(map(lambda x: x['hitter'], self.event)))
        self.out_hitter_numbers = self.get_out_hitter_numbers()  # 아웃타자번호
        #  투수에게 긍정적인 상황인지 부정적인 상황인지
        self.pos_neg = 'N' if self.score > 0 else 'P'
        self.sentence = ''
        self.next_pitcher = next_pitcher  # 다음투수
        self.next_pitcher_exist = True if next_pitcher else False  # 다음투수존재
        self.last_inn = last_inn  # 마지막이닝
        self.first_inn = first_inn  # 첫번째이닝
        self.replacement = True if (self.event[-1]['outcount'] == '2' and (self.event[-1]['situation'] == 'out' or self.event[-1]['situation'] == 'pos' or self.event[-1]['연속'])) or \
                                   (self.event[-1]['outcount'] == '1' and self.event[-1]['how'] == 'GD') else False  # 교체시기
        self.cont = list(map(lambda x: x['연속'], self.event))  # 연속
        self.accumulate_score = g.pitcher_accumulate_score  # 누적실점
        self.total_score = total_score  # 총실점
        self.is_called = g.is_called  # 콜드게임
        self.today_weather = g.today_weather  # 날씨
        self.game_last_row_inn = game_last_row['inn']  # 끝_이닝
        self.game_last_row_tb = '초' if game_last_row['tb'] == 'T' else '말'  # 끝_초말
        self.is_first_pitcher = self.is_first_pitcher() # 선발투수여부
        self.init_kor_caller()

    def is_first_pitcher(self):
        _today_record = g.pitchers_today.filter(pcode__exact=self.pitcher)
        is_first_pitcher = _today_record[0].start == '1'
        return is_first_pitcher

    def is_triceps(self):
        res = True
        for i in self.how_list:
            if i in g.HIT:
                res = False
                break
        return res

    def is_oob(self):  # 주루사
        is_oob = False
        if self.all_how_list[-1] == 'TO' and (self.all_how_list[-2] == 'H2' or self.all_how_list == 'H3'):
            is_oob = True
        return is_oob

    # region [EVENT]
    def get_event(self, df_data):
        get_scored = ['E', 'R', 'H', 'F', 'S', 'I']
        event_list = []
        score = 0
        # 타자일순
        # TODO 타자일순을 볼 수는 있으나 실제로 event로 잡지 못함(덧씌워짐)
        df_orderd_hitter = df_data.groupby(['inn2', 'hitter'], sort=False)
        hitter = ''
        hitter_name = ''
        base = ''
        ball_count = ''
        outcount = ''
        how = ''
        place = ''
        situation = ''
        kor_base = ''
        kor_outcount = ''
        turn = ''
        kor_turn = ''
        index = 0
        field = ''
        kor_field = ''
        cont = False
        kor_outcount_base = ''
        all_how_list = []
        all_field_list = []

        for hitter_cd, ser_hitter in df_orderd_hitter:
            # how 에러시 상단으로
            temp_how = ''
            temp_idx = 0
            first_how = ''
            for idx, ser_data in ser_hitter.iterrows():
                all_how_list.append(ser_data['how'])
                if temp_idx == 0:
                    first_how = ser_data['how']
                temp_idx += 1
                # how 에러시 삭제
                if ser_data['how'] == 'ER':
                    if ser_data['place'] not in get_scored:
                        continue
                if ser_data['place'] in get_scored:
                    g.pitcher_accumulate_score += 1
                    score += 1
                if ser_data['how'] in g.pitcher_ignore_list:
                    continue

                if len(temp_how) > 0:
                    if ser_data['place'] not in get_scored:
                        continue
                    else:
                        how = ser_data['how']
                        temp_how = ''
                else:
                    #  연속인 경우에 관한 알고리즘
                    #  g.cont_list = ['FO', 'TO'] 필요시 추가
                    if ser_data['how'] not in g.cont_list:
                        how = ser_data['how']
                        temp_how = ''
                    else:
                        if how == 'GD':
                            cont = False
                        else:
                            cont = True
                            situation = 'out'
                        continue

                if how in g.neg_consider:
                    if ser_data['place'] in get_scored:
                        temp_how = how

                hitter = ser_data['hitter']
                turn = int(ser_data['turn'][-1])
                hitter_name = ser_data['hitname']
                ball_count = len(ser_data['bcount'])
                place = ser_data['place']

                if ser_data['ocount'] == '4':
                    pass
                else:
                    outcount = str(ser_data['ocount'])

                b1 = '1' if ser_data['base1b'] else ''
                b2 = '2' if ser_data['base2b'] else ''
                b3 = '3' if ser_data['base3b'] else ''
                base = b1 + b2 + b3

                field = ser_data['field'].strip()
                all_field_list.append(field)
                # field와 수비 추가
                if len(field) > 0:
                    # 삼진은 수비 없음
                    if how == 'KK':
                        field = ''
                        kor_field = ''
                    else:
                        field = re.sub('[A-Z]', ' ', field).strip().split()[0]
                        try:
                            kor_field = g.defense_kor_dict[field]
                        except KeyError:
                            kor_field = g.defense_kor_dict[field[0]]
                else:
                    field = ''
                    kor_field = ''

                if index == 0:
                    kor_turn = '선두타자'
                else:
                    kor_turn = str(ser_data['turn'][-1]) + '번타자'

                if place in ['0', '1', '2', '3']:
                    situation = 'out'
                elif how in g.HIT:
                    situation = 'hit'
                else:
                    situation = 'onbase'

                if how in g.pos_consider:
                    situation = 'pos'

                elif how in g.neg_consider:
                    situation = 'neg'

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

                if outcount == '0' and len(base) == 0:
                    kor_outcount_base = '선두타자 '
                else:
                    kor_outcount_base = kor_outcount + ' ' + kor_base + '에서 '

            scene_dict = dict()
            scene_dict['idx'] = index
            scene_dict['hitter'] = hitter
            scene_dict['타자이름'] = hitter_name
            scene_dict['ball_count'] = ball_count
            scene_dict['base'] = base
            scene_dict['루상황'] = kor_base
            scene_dict['outcount'] = outcount
            scene_dict['아웃카운트'] = kor_outcount
            scene_dict['how'] = how
            scene_dict['하우'] = g.pitcher_how_kor_dict[how]
            scene_dict['place'] = place
            scene_dict['score'] = score
            scene_dict['situation'] = situation
            scene_dict['turn'] = turn
            scene_dict['타자번호'] = kor_turn
            scene_dict['field'] = field
            scene_dict['모든필드'] = all_field_list
            scene_dict['수비'] = kor_field
            scene_dict['연속'] = cont
            scene_dict['첫번째하우'] = g.pitcher_how_kor_dict[first_how]
            scene_dict['아웃_루상황'] = kor_outcount_base
            scene_dict['모든하우'] = all_how_list
            cont = False

            index += 1

            event_list.append(scene_dict)
            if score > 0:
                self.scored_scene.append(scene_dict)
            score = 0
        return event_list
    # endregion [EVENT]

    # region [FUNCTION]
    def init_kor_caller(self):
        kor_dict = {
            '투수코드': 'pitcher',
            '이름': 'pitcher_name',
            '회': 'inning',
            '초말': 'tb',
            '이닝실점': 'score',
            '전체진루상황': 'situation_list',
            '아웃상황': 'out_list',
            '안타상황': 'hit_list',
            '홈런상황': 'hr_list',
            '온베이스상황': 'onbase_list',
            '실점상황': 'score_list',
            '아웃타자번호': 'out_hitter_numbers',
            '전체상황': 'event',
            '타자리스트': 'hitters_kor',
            '안타타자리스트': 'hitter_list',
            '팀이름':'team',
            '상대팀이름': 'vs_team',
            '전체주자상황': 'base_list',
            '공갯수리스트': 'bcount_list',
            '공갯수': 'bcount',
            '다음투수': 'next_pitcher',
            '다음투수존재': 'next_pitcher_exist',
            '교체시기': 'replacement',
            '마지막이닝': 'last_inn',
            '첫번째이닝': 'first_inn',
            '다음회': 'next_inning',
            '연속': 'cont',
            '아웃실점': 'out_score_list',
            '중복제거아웃': 'set_out_list',
            '누적실점': 'accumulate_score',
            '총실점': 'total_score',
            '첫번째하우': 'first_how',
            '콜드게임': 'is_called',
            '날씨': 'today_weather',
            '끝_이닝': 'game_last_row_inn',
            '끝_초말': 'game_last_row_tb',
            '삼자범퇴': 'is_triceps',
            '모든하우': 'all_how_list',
            '주루사': 'is_oob',
            '모든필드': 'all_field_list',
            'is_선발': 'is_first_pitcher'
        }
        for k, v in kor_dict.items():
            setattr(self, k, getattr(self, v))

    def get_out_hitter_numbers(self):
        result_list = []
        for e in self.event:
            hitter_cd = e['hitter']
            for player in g.player_entry:
                if player.pcode == hitter_cd:
                    result_list.append(player.turn[-1])
                    break
        return result_list
    # endregion [FUNCTION]
