from blog.lib import globals as g
import numpy as np
import pandas as pd
from blog import minor_baseball_models as b_models
import aws.config as cfg
import io
import pickle
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib as mpl
import warnings
import boto3
import datetime

warnings.filterwarnings('ignore')
mpl.use('Agg')
mpl.style.use('default')
path = './blog/lib/analysis/res/NanumGothic.ttf'
fontprop = fm.FontProperties(fname=path, size=15)



class Stats:

    def __init__(self, game_id, pitcher_df, name):
        self.game_id = game_id
        self.name = name
        self.df_pitcher = pitcher_df
        # pitcher table에 GYEAR column 추가
        self.team_dict = {'HH': '한화',
                          'HT': 'KIA',
                          'KT': 'KT',
                          'LG': 'LG',
                          'LT': '롯데',
                          'NC': 'NC',
                          'OB': '두산',
                          'SK': 'SK',
                          'SM': '상무',
                          'SS': '삼성',
                          'WO': '고양',
                          'PL': '경찰',
                          'kt': 'KT'}
        self.stat_dict = {'ERA': '평균자책점',
                          'WHIP': '출루허용률(WHIP)',
                          'KBB': '볼넷당 삼진'}
        self.set_append_year()
        self.stats = self.extract_stats()
        self.s3_resource = boto3.resource(
            's3',
            aws_access_key_id=cfg.aws_access_key_id,
            aws_secret_access_key=cfg.aws_secret_access_key,
            region_name=cfg.region,
        )

    def set_append_year(self):
        player_df = self.df_pitcher
        year = []
        for i in range(len(player_df)):
            year.append(player_df.gday[i][:4])
        player_df['gyear'] = year

    def set_era(self, er, inning):
        inn = inning / 3
        temp = round((er / inn) * 9, 4)
        if len(str(temp)) <= 3:
            return float(temp)
        elif str(temp)[-2] == '5' and int(str(temp)[-3]) % 2 == 0:
            temp = float(str(temp + 0.01)[:-2])
            return float(str(temp)[:4])
        #  x.xx5 에 대한 반올림
        elif str(temp)[-1] == '5':
            temp = float(str(temp + 0.01)[:-1])
            return float(str(temp)[:4])
        else:
            result = round((er / inn) * 9, 2)
            return float(result)

    def cumulative(self, game_num):
        player_df = self.df_pitcher
        pitcher_2019 = player_df[player_df['gyear'] == "2019"].reset_index(drop=True)
        recent_cumulative_ERA = {}
        recent_cumulative_WHIP = {}
        recent_cumulative_KBB = {}

        recent_cumulative_ERA[pitcher_2019.gmkey[0]] = self.set_era(pitcher_2019.er[0], (pitcher_2019.inn2[0]))
        for i in range(1, game_num):
            er = pitcher_2019.er[:i + 1].sum()
            inn = pitcher_2019.inn2[:i + 1].sum()
            recent_cumulative_ERA[pitcher_2019.gmkey[i]] = self.set_era(er, inn)

        recent_cumulative_WHIP[pitcher_2019.gmkey[0]] = round((pitcher_2019.bb[0].sum() + pitcher_2019.ib[0].sum()
                                                         + pitcher_2019.hit[0].sum()) / (pitcher_2019.inn2[0].sum() / 3), 2)
        for i in range(1, game_num):
            recent_cumulative_WHIP[pitcher_2019.gmkey[i]] = round(
                ((pitcher_2019.bb[:i + 1].sum() + pitcher_2019.ib[:i + 1].sum()
                  + pitcher_2019.hit[:i + 1].sum()) / (pitcher_2019.inn2[:i + 1].sum() / 3)), 2)

        recent_cumulative_KBB[pitcher_2019.gmkey[0]] = round(pitcher_2019.kk[0].sum() / (
                pitcher_2019.bb[0].sum() - pitcher_2019.ib[0].sum()), 2)
        for i in range(1, game_num):
            recent_cumulative_KBB[pitcher_2019.gmkey[i]] = round(pitcher_2019.kk[:i + 1].sum() / (
                    pitcher_2019.bb[:i + 1].sum() - pitcher_2019.ib[:i + 1].sum()), 2)

        return recent_cumulative_ERA, recent_cumulative_WHIP, recent_cumulative_KBB

    def ERA(self, game_num, year_num, flag=True):
        player_df = self.df_pitcher
        recent_game = {}
        recent_year = {}

        for i in range(1, game_num + 1):
            if player_df.iloc[-i].inn == 0:
                recent_game[player_df.iloc[-i].gmkey] = '-' if flag else 0
            else:
                recent_game[player_df.iloc[-i].gmkey] = (player_df.iloc[-i].er / (player_df.iloc[-i].inn2 / 3)) * 9

        for j in range(2019, 2019 - year_num, -1):
            if player_df[player_df.gyear == str(j)].inn.sum() == 0:
                recent_year[j] = '-'
            else:
                recent_year[j] = (player_df[player_df.gyear == str(j)].er.sum()
                                  / (player_df[player_df.gyear== str(j)].inn2 / 3).sum()) * 9

        return recent_game, recent_year

    def WHIP(self, game_num, year_num, flag=True):
        player_df = self.df_pitcher
        recent_game = {}
        recent_year = {}

        for i in range(1, game_num + 1):
            if player_df.iloc[-i].inn == 0:
                recent_game[player_df.iloc[-i].gmkey] = '-' if flag else 0
            else:
                recent_game[player_df.iloc[-i].gmkey] = (player_df.iloc[-i].bb + player_df.iloc[-i].ib
                                                         + player_df.iloc[-i].hit) / (player_df.iloc[-i].inn2 / 3)

        for j in range(2019, 2019 - year_num, -1):
            if player_df[player_df.gyear== str(j)].inn.sum() == 0:
                recent_year[j] = '-'
            else:
                recent_year[j] = (player_df[player_df.gyear == str(j)].bb.sum()
                                  + player_df[player_df.gyear == str(j)].ib.sum()
                                  + player_df[player_df.gyear == str(j)].hit.sum()) / (player_df[
                                     player_df.gyear == str(j)].inn2 / 3).sum()

        return recent_game, recent_year

    def KBB(self, game_num, year_num, flag=True):
        player_df = self.df_pitcher
        recent_game = {}
        recent_year = {}

        for i in range(1, game_num + 1):
            if (player_df.iloc[-i].bb - player_df.iloc[-i].ib) == 0:
                recent_game[player_df.iloc[-i].gmkey] = '-' if flag else 0
            else:
                recent_game[player_df.iloc[-i].gmkey] = player_df.iloc[-i].kk / (
                        player_df.iloc[-i].bb - player_df.iloc[-i].ib)

        for j in range(2019, 2019 - year_num, -1):
            if player_df[player_df.gyear == str(j)].bb.sum() - player_df[player_df.gyear == str(j)].ib.sum() == 0:
                recent_year[j] = '-'
            else:
                recent_year[j] = player_df[player_df.gyear == str(j)].kk.sum() / (
                        player_df[player_df.gyear == str(j)].bb.sum() - player_df[
                    player_df.gyear == str(j)].ib.sum())

        return recent_game, recent_year

    def INN(self, game_num, year_num):
        player_df = self.df_pitcher
        recent_game = {}
        recent_year = {}

        for i in range(1, game_num + 1):
            recent_game[player_df.iloc[-i].gmkey] = (player_df.iloc[-i].inn2 / 3)

        for j in range(2019, 2019 - year_num, -1):
            recent_year[j] = round((player_df[player_df.gyear == str(j)].inn2 / 3).sum(), 1)

        return recent_game, recent_year, player_df.inn2.sum()

    def TODAY(self, flag=True):
        # 오늘 경기 STAT기록을 dict로 반환
        result = {'ERA': list(self.ERA(1, 0, flag)[0].values())[0],
                  'WHIP': list(self.WHIP(1, 0, flag)[0].values())[0],
                  'KBB': list(self.KBB(1, 0, flag)[0].values())[0],
                  'GMKEY': self.game_id}
        return result

    def extract_stats(self):
        # 오늘 경기 기준, model이 가장 잘했다고 판단 한 STAT 종류 반환 ex) 'ERA'
        label = {0: 'ERA', 1: 'WHIP', 2: 'KBB'}

        today_stats = list(self.TODAY(True).values())[:3]
        for i in range(len(today_stats)):
            if today_stats[i] == '-':
                today_stats[i] = 0
        today_stats.append(list(self.INN(1, 0)[0].values())[0])
        today_stats = np.array([today_stats])

        with open('./blog/lib/analysis/res/model_ovo_with300', 'rb') as f:
            model = pickle.load(f)

        if label == 1 or label == 2:
            return None
        else:
            return label[model.predict(today_stats)[0]]

    def cumulative_gradient(self):
        label = self.stats
        player_df = self.df_pitcher
        pitcher_2019 = player_df[player_df['gyear'] == "2019"].reset_index(drop=True)
        cu_era, cu_whip, cu_kbb = self.cumulative(len(pitcher_2019))

        result = None
        # test

        try:
            if label == 'ERA':
                if len(pitcher_2019) > 3:
                    grad_dict = {}
                    for i in range(3, 7 if len(pitcher_2019) > 7 else len(pitcher_2019)):
                        grad_dict[i] = np.gradient(list(cu_era.values())[:i]).mean()

                    best_grad = max(grad_dict.values())

                    for k, v in grad_dict.items():
                        if best_grad == v:
                            result = k

                    return result, cu_era
                else:
                    result = 0
                    return result, cu_era

            elif label == 'WHIP':
                if len(pitcher_2019) > 3:
                    grad_dict = {}
                    for i in range(3, 7 if len(pitcher_2019) > 7 else len(pitcher_2019)):
                        grad_dict[i] = np.gradient(list(cu_whip.values())[:i]).mean()

                    best_grad = max(grad_dict.values())

                    for k, v in grad_dict.items():
                        if best_grad == v:
                            result = k

                    return result, cu_whip
                else:
                    result = 0
                    return result, cu_whip

            elif label == 'KBB':
                if len(pitcher_2019) > 3:
                    grad_dict = {}
                    for i in range(3, 7 if len(pitcher_2019) > 7 else len(pitcher_2019)):
                        grad_dict[i] = np.gradient(list(cu_kbb.values())[:i]).mean()

                    best_grad = max(grad_dict.values())

                    for k, v in grad_dict.items():
                        if best_grad == v:
                            result = k

                    return result, cu_kbb
                else:
                    result = 0
                    return result, cu_kbb
        except:
            print('cu_cal_grad')
            pass

    def cumulative_Viz(self):
        """
        그래프제목:윤강민(NC), 최근 3경기 평균자책점(누적)
        xticks: 3/16 **전
        """
        player_df = self.df_pitcher
        pitcher_2019 = player_df[player_df['gyear'] == "2019"].reset_index(drop=True)
        target_stats = self.stats
        target_length, recent_game = self.cumulative_gradient()

        if target_stats == 'ERA':
            game_name = recent_game.keys()
            values = list(recent_game.values())[-target_length:]
            result = []
            f_score = 0
            s_score = 0
            temp_name = list(game_name)[-target_length:]
            f_team = temp_name[0][8:10]
            s_team = temp_name[0][10:12]
            for i in range(len(temp_name)):
                if f_team == temp_name[i][8:10] or f_team == temp_name[i][10:12]:
                    f_score += 1
                else:
                    s_score += 1
            if f_score > s_score:
                team = f_team
            else:
                team = s_team
            for i in range(len(temp_name)):
                first = temp_name[i][8:10]
                second = temp_name[i][10:12]
                month = temp_name[i][4:6]
                day = temp_name[i][6:8]
                if team == first:
                    result.append(month + '/' + day + ' ' + self.team_dict[second] + '전')
                else:
                    result.append(month + '/' + day + ' ' + self.team_dict[first] + '전')

            result = result
            values = values
            month_result = [i[:5] for i in result]
            time_dist = []
            for m, d in [i.split('/') for i in month_result][::-1]:
                temp = datetime.date(19, int(m), int(d))
                temp = temp.toordinal()
                time_dist.append(temp)

            if values[-2] - values[-1] > 0.1 and values[-1] <= 3.5 and max(time_dist) - min(time_dist) < 30:
                fig = plt.figure(figsize=(6, 4))
                ax = fig.add_axes((0.1, 0.2, 0.8, 0.7))
                ax.spines['right'].set_color('none')
                ax.spines['top'].set_color('none')
                plt.plot(result if len(result) < 5 else month_result,
                         values, marker='o', lw=2, markersize=10, label='평균자책점', color="#05173F")
                ticks_dist = max(values) - min(values)
                prev_v = 0
                slope_list = []
                for v in values:
                    slope_list.append(prev_v - v)
                    prev_v = v
                for i, v in enumerate(values):
                    if ticks_dist == 0:
                        x, y = 0.1, 0.015
                    elif ticks_dist < 0.2:
                        x, y = 0.1, 0.025
                    elif ticks_dist < 0.6:
                        x, y = 0.1, 0.035
                    elif ticks_dist < 1:
                        x, y = 0.1, 0.08
                    elif ticks_dist < 3:
                        x, y = 0.1, 0.25
                    elif ticks_dist < 5:
                        x, y = 0.1, 0.5
                    elif ticks_dist < 8:
                        x, y = 0.1, 1
                    else:
                        x, y = 0.3, 5
                    value = str(round(v, 2))
                    if slope_list[i] < 0:
                        y = y
                    else:
                        y = -y
                    ax.text(i - x, v + y,
                            value if len(str(value).split('.')[1]) == 2 else value + '0',
                            fontproperties=fontprop,
                            fontsize=10)
                plt.xticks(fontproperties=fontprop,
                           ticks=result if len(result) < 5 else month_result,
                           weight='bold',
                           fontsize=11)
                if ticks_dist > 0.3:
                    yticks_list = [str(i)[:3] + '0' for i in np.arange(round(min(values), 1) - 0.1 if round(min(values), 1) > 1 else round(min(values), 1),
                                  round(max(values), 2) + 0.1, 0.5)]
                    plt.yticks(np.arange(round(min(values), 1) - 0.1 if round(min(values), 1) > 1 else round(min(values), 1), round(max(values), 2) + 0.1, 0.5),
                               yticks_list)
                elif ticks_dist > 0.1:
                    yticks_list = [str(i)[:3] + '0' for i in np.arange(
                        round(min(values), 1) - 0.1 if round(min(values), 1) > 1 else round(min(values), 1),
                        round(max(values), 2) + 0.1, 0.1)]
                    plt.yticks(
                        np.arange(round(min(values), 1) - 0.1 if round(min(values), 1) > 1 else round(min(values), 1),
                                  round(max(values), 2) + 0.1, 0.1), yticks_list)
                else:
                    yticks_list = [str(i) if len(str(i).split('.')[1]) == 2 else str(i) + '0'
                                   if len(str(i).split('.')[1]) == 1 else str(i) + '00'
                                   for i in np.arange(round(min(values), 1), round(max(values), 2), 0.05)]
                    plt.yticks(np.arange(round(min(values), 1), round(max(values), 1), 0.05), yticks_list)
                plt.margins(0.2, 0.3)
                plt.title('%s(%s) 최근 %d경기 평균자책점(누적)\n' % (self.name,
                                                        self.team_dict[temp_name[-1][8:10]] if g.WIN_TB == 'T' else self.team_dict[temp_name[-1][10:12]],
                                                        target_length),
                                                        fontproperties=fontprop)
                graph_path = '{gmkey}'.format(gmkey=pitcher_2019.iloc[-1].gmkey)
                self.save_fig_file(fig, graph_path)
                plt.close(fig)

                return graph_path, result, values[-2]
            else:
                print('의미없는 변화량')
                raise Exception

        elif target_stats == 'WHIP':
            game_name = recent_game.keys()
            values = list(recent_game.values())[-target_length:]
            result = []
            f_score = 0
            s_score = 0
            temp_name = list(game_name)[-target_length:]
            f_team = temp_name[0][8:10]
            s_team = temp_name[0][10:12]
            for i in range(len(temp_name)):
                if f_team == temp_name[i][8:10] or f_team == temp_name[i][10:12]:
                    f_score += 1
                else:
                    s_score += 1
            if f_score > s_score:
                team = f_team
            else:
                team = s_team
            for i in range(len(temp_name)):
                first = temp_name[i][8:10]
                second = temp_name[i][10:12]
                month = temp_name[i][4:6]
                day = temp_name[i][6:8]
                if team == first:
                    result.append(month + '/' + day + ' ' + self.team_dict[second] + '전')
                else:
                    result.append(month + '/' + day + ' ' + self.team_dict[first] + '전')

            result = result
            values = values
            month_result = [i[:5] for i in result]

            time_dist = []
            for m, d in [i.split('/') for i in month_result][::-1]:
                temp = datetime.date(19, int(m), int(d))
                temp = temp.toordinal()
                time_dist.append(temp)

            if values[-2] - values[-1] > 0.1 and values[-1] <= 2 and max(time_dist) - min(time_dist) < 30:
                fig = plt.figure(figsize=(6, 4))
                ax = fig.add_axes((0.1, 0.2, 0.8, 0.7))
                ax.spines['right'].set_color('none')
                ax.spines['top'].set_color('none')
                plt.plot(result if len(result) < 5 else month_result,
                         values, marker='o', lw=2, markersize=10, label='출루허용률', color="#05173F")
                ticks_dist = max(values) - min(values)
                prev_v = 0
                slope_list = []
                for v in values:
                    slope_list.append(prev_v - v)
                    prev_v = v
                for i, v in enumerate(values):
                    if ticks_dist == 0:
                        x, y = 0.1, 0.015
                    elif ticks_dist < 0.2:
                        x, y = 0.1, 0.02
                    elif ticks_dist < 0.6:
                        x, y = 0.1, 0.045
                    elif ticks_dist < 1:
                        x, y = 0.1, 0.07
                    elif ticks_dist < 3:
                        x, y = 0.1, 0.25
                    elif ticks_dist < 5:
                        x, y = 0.1, 0.5
                    elif ticks_dist < 8:
                        x, y = 0.1, 1
                    else:
                        x, y = 0.1, 5
                    value = str(round(v, 2))
                    if slope_list[i] < 0:
                        y = y
                    else:
                        y = -y
                    ax.text(i - x, v + y,
                            value if len(str(value).split('.')[1]) == 2 else value + '0',
                            fontproperties=fontprop,
                            fontsize=10)
                plt.xticks(fontproperties=fontprop,
                           ticks=result if len(result) < 5 else month_result,
                           weight='bold',
                           fontsize=11)
                if ticks_dist > 0.1:
                    yticks_list = [str(i)[:3] + '0' for i in np.arange(
                        round(min(values), 1) - 0.1 if round(min(values), 1) > 1 else round(min(values), 1),
                        round(max(values), 2) + 0.1, 0.5)]
                    plt.yticks(
                        np.arange(round(min(values), 1) - 0.1 if round(min(values), 1) > 1 else round(min(values), 1),
                                  round(max(values), 2) + 0.1, 0.5),
                        yticks_list)
                else:
                    yticks_list = [str(i) if len(str(i).split('.')[1]) == 2 else str(i) + '0'
                    if len(str(i).split('.')[1]) == 1 else str(i) + '00'
                                   for i in np.arange(round(min(values), 1), round(max(values), 2), 0.05)]
                    plt.yticks(np.arange(round(min(values), 1), round(max(values), 1), 0.05), yticks_list)
                plt.margins(0.2, 0.3)
                plt.title('%s(%s) 최근 %d경기 출루허용률(누적)\n' % (self.name,
                                                        self.team_dict[temp_name[-1][8:10]] if g.WIN_TB == 'T' else self.team_dict[temp_name[-1][10:12]],
                                                        target_length),
                                                        fontproperties=fontprop)
                graph_path = '{gmkey}'.format(gmkey=pitcher_2019.iloc[-1].gmkey)
                self.save_fig_file(fig, graph_path)
                plt.close(fig)

                return graph_path, result, values[-2]
            else:
                print('의미없는 변화량')
                raise Exception

        elif target_stats == 'KBB':
            game_name = recent_game.keys()
            values = list(recent_game.values())[-target_length:]
            result = []
            f_score = 0
            s_score = 0
            temp_name = list(game_name)[-target_length:]
            f_team = temp_name[0][8:10]
            s_team = temp_name[0][10:12]
            for i in range(len(temp_name)):
                if f_team == temp_name[i][8:10] or f_team == temp_name[i][10:12]:
                    f_score += 1
                else:
                    s_score += 1
            if f_score > s_score:
                team = f_team
            else:
                team = s_team
            for i in range(len(temp_name)):
                first = temp_name[i][8:10]
                second = temp_name[i][10:12]
                month = temp_name[i][4:6]
                day = temp_name[i][6:8]
                if team == first:
                    result.append(month + '/' + day + ' ' + self.team_dict[second] + '전')
                else:
                    result.append(month + '/' + day + ' ' + self.team_dict[first] + '전')

            result = result
            values = values
            month_result = [i[:5] for i in result]

            time_dist = []
            for m, d in [i.split('/') for i in month_result][::-1]:
                temp = datetime.date(19, int(m), int(d))
                temp = temp.toordinal()
                time_dist.append(temp)

            if values[-1] - values[-2] > 0.05 and values[-1] >= 3 and max(time_dist) - min(time_dist) < 30:
                fig = plt.figure(figsize=(6, 4))
                ax = fig.add_axes((0.1, 0.2, 0.8, 0.7))
                ax.spines['right'].set_color('none')
                ax.spines['top'].set_color('none')
                plt.plot(result if len(result) < 5 else month_result,
                         values, marker='o', lw=2, markersize=10, label='볼넷당 삼진', color="#05173F")
                ticks_dist = max(values) - min(values)
                prev_v = 0
                slope_list = []
                for v in values:
                    slope_list.append(prev_v - v)
                    prev_v = v
                for i, v in enumerate(values):
                    if ticks_dist == 0:
                        x, y = 0.1, 0.015
                    elif ticks_dist < 0.2:
                        x, y = 0.1, 0.020
                    elif ticks_dist < 0.3:
                        x, y = 0.1, 0.03
                    elif ticks_dist < 0.6:
                        x, y = 0.1, 0.045
                    elif ticks_dist < 1:
                        x, y = 0.1, 0.07
                    elif ticks_dist < 3:
                        x, y = 0.1, 0.25
                    elif ticks_dist < 5:
                        x, y = 0.1, 0.5
                    elif ticks_dist < 8:
                        x, y = 0.1, 1
                    else:
                        x, y = 0.1, 5
                    value = str(round(v, 2))
                    if slope_list[i] < 0:
                        y = y
                    else:
                        y = -y
                    ax.text(i - x, v + y,
                            value if len(str(value).split('.')[1]) == 2 else value + '0',
                            fontproperties=fontprop,
                            fontsize=10)
                plt.xticks(fontproperties=fontprop,
                           ticks=result if len(result) < 5 else month_result,
                           weight='bold',
                           fontsize=12)
                if ticks_dist > 0.1:
                    yticks_list = [str(i)[:3] + '0' for i in np.arange(
                        round(min(values), 1) - 0.1 if round(min(values), 1) > 1 else round(min(values), 1),
                        round(max(values), 2) + 0.1, 0.5)]
                    plt.yticks(
                        np.arange(round(min(values), 1) - 0.1 if round(min(values), 1) > 1 else round(min(values), 1),
                                  round(max(values), 2) + 0.1, 0.5),
                        yticks_list)
                else:
                    yticks_list = [str(i) if len(str(i).split('.')[1]) == 2 else str(i) + '0'
                                   if len(str(i).split('.')[1]) == 1 else str(i) + '00'
                                   for i in np.arange(round(min(values), 1), round(max(values), 2), 0.05)]
                    plt.yticks(np.arange(round(min(values), 1), round(max(values), 1), 0.05), yticks_list)
                plt.margins(0.2, 0.3)
                plt.title('%s(%s) 최근 %d경기 볼넷당 삼진(누적)\n' % (self.name,
                                                        self.team_dict[temp_name[-1][8:10]] if g.WIN_TB == 'T' else self.team_dict[temp_name[-1][10:12]],
                                                        target_length),
                                                        fontproperties=fontprop)
                graph_path = '{gmkey}'.format(gmkey=pitcher_2019.iloc[-1].gmkey)
                self.save_fig_file(fig, graph_path)
                plt.close(fig)

                return graph_path, result, values[-2]
            else:
                print('의미없는 변화량')
                raise Exception

    def cumulative_text(self):
        target_stats = self.stats
        pitcher_df = self.df_pitcher
        name = self.name
        target_length, recent_game = self.cumulative_gradient()
        is_exist = False
        if target_length > 0:
            recent_game_score = [round(i, 2) for i in list(recent_game.values())]
            viz = self.cumulative_Viz()
            stat_name = self.stat_dict[target_stats]
            length = len(recent_game_score)
            is_exist = True
            for i in range(len(recent_game_score)):
                if len(str(recent_game_score[i]).split('.')[1]) == 2:
                    recent_game_score[i] = str(recent_game_score[i])
                else:
                    recent_game_score[i] = str(recent_game_score[i]) + '0'
            today_score = recent_game_score[-1]
            last_score = recent_game_score[-2]
            inn = pitcher_df[pitcher_df.gyear == '2019'].inn2.sum()
            inn = str(round(inn / 3, 1))
            g.s_is_exist = is_exist
            g.s_name = name
            g.s_stat_name = stat_name
            g.s_length = length
            g.s_today_score = today_score
            g.s_last_score = last_score
            g.s_inn = inn
            return is_exist, name, stat_name, length, today_score, last_score, inn
        else:
            return is_exist

    def save_fig_file(self, fig, image_name):
        with io.BytesIO() as img_data:
            fig.savefig(img_data, bbox_inches='tight', format='png')
            image_name += '.png'
            img_data.seek(0)
            self.s3_resource.Bucket(cfg.bucket_name).put_object(Body=img_data, Key=image_name, ACL='public-read', CacheControl='no-cache')


class HitterStat:
    def __init__(self, hitter_df, game_id, hitter_code):
        self.game_id = game_id
        self.pcode = hitter_code
        self.df_2019 = hitter_df
        self.name = self.df_2019.name[0]
        self.today_record = g.hitters_today.filter(pcode__exact=self.pcode)
        self.stat_dict = {'avg': '타율', 'hr': '홈런', 'rbi': '타점', 'sb': '도루', 'run': '득점', 'hit': '안타',
                          'obp': '출루율', 'slg': '장타율', 'h2': '2루타', 'h3': '3루타', 'ops': '오피에스',
                          'ab': '타수', 'bb': '볼넷'}
        self.month_dict = {'03': '3월', '04': '4월', '05': '5월', '06': '6월', '07': '7월', '08': '8월', '09': '9월',
                           '10': '10월'}
        self.stat = self.extract_stats()

        self.s3_resource = boto3.resource(
            's3',
            aws_access_key_id=cfg.aws_access_key_id,
            aws_secret_access_key=cfg.aws_secret_access_key,
            region_name=cfg.region,
        )
        # self.hitter_Viz()

    def avg(self, df):  # 타율
        return round(df.hit / df.ab, 3)

    def obp(self, df):  # 출루율
        return round((df.hit + df.bb + df.ib + df.hp) / (df.ab + df.bb + df.ib + df.hp + df.sf), 3)

    def slg(self, df):  # 장타율
        return round(((df.h2 * 2) + (df.h3 * 3) + (df.hr * 4) + (df.hit - df.h2 + df.h3 + df.hr)) / df.ab, 3)

    def ops(self, df):  # 오피에스
        return self.obp(df) + self.slg(df)

    def extract_stats(self):
        today_record = self.today_record[0]
        if today_record.hit >= 2:
            return 'avg'
        elif today_record.hr != 0:
            return 'hr'
        # elif today_record.h2 + today_record.h3 + today_record.bb + today_record.ib + today_record.hp >= 3:
        #     return 'ops'
        # elif today_record.rbi >= 2:
        #     return 'rbi'
        # elif today_record.sb >= 1:
        #     return 'sb'
        # elif today_record.run >= 2:
        #     return 'run'
        # elif today_record.bb >= 2:
        #     return 'bb'

    def hitter_Viz(self):
        stat = self.stat
        df_2019 = self.df_2019
        month = [i[4:6] for i in list(df_2019.gday)]
        df_2019['month'] = month
        month_game_num = dict(self.df_2019.month.value_counts())
        group_by_month_df = df_2019.groupby('month').sum()
        group_by_month_df.set_value(index=month_game_num.keys(), value=list(month_game_num.values()), col='game_num')

        #TODO 'avg', 'ops' 제외 나머지는 막대그래프로 190626
        target_dict = dict(self.avg(group_by_month_df)) if stat == 'avg' else dict(group_by_month_df.hr) \
                      if stat == 'hr' else dict(self.ops(group_by_month_df)) \
                      if stat == 'ops' else dict(group_by_month_df.rbi) \
                      if stat == 'rbi' else dict(group_by_month_df.sb) \
                      if stat == 'sb' else dict(group_by_month_df.run) \
                      if stat == 'run' else dict(group_by_month_df.bb) \
                      if stat == 'bb' else None
        group_by_month_df.set_value(index=target_dict.keys(), value=list(target_dict.values()), col=stat)
        if stat == 'avg' or stat == 'ops':
            for i in list(target_dict.keys()):
                if target_dict[i] == 0:
                    del target_dict[i]
                if len(target_dict) < 4:
                    break
            x_ = target_dict.keys()
            y_ = target_dict.values()
            if list(y_)[-1] > list(y_)[-2] and list(y_)[-1] > 0.3 \
               and abs(group_by_month_df.iloc[-1].ab - group_by_month_df.iloc[-2].ab) < 15:
                fig = plt.figure(figsize=(6, 4))
                ax = fig.add_axes((0.1, 0.2, 0.8, 0.7))
                ax.spines['right'].set_color('none')
                ax.spines['top'].set_color('none')
                # ax.spines['bottom'].set_position('zero')
                # ax.xaxis.tick_bottom()
                plt.plot([self.month_dict[i] for i in x_], y_, marker='o', lw=2, markersize=10, label=self.stat_dict[stat],
                         color='#05173F')
                ticks_dist = max(y_) - min(y_)
                prev_v = 0
                slope_list = []
                for v in y_:
                    slope_list.append(prev_v - v)
                    prev_v = v
                for i, v in enumerate(y_):
                    value = str(round(v, 3))
                    if ticks_dist == 0:
                        x, y = 0.15, 0.001
                    elif ticks_dist < 0.2:
                        x, y = 0.15, 0.02
                    elif ticks_dist < 0.4:
                        x, y = 0.15, 0.03
                    elif ticks_dist < 0.6:
                        # daehyuk 20190816 차트 y축 0.000 하단 배치
                        #x, y = 0.15, 0.07
                        x, y = 0.15, 0.04
                    elif ticks_dist < 1:
                        x, y = 0.15, 0.1
                    elif ticks_dist < 3:
                        x, y = 0.15, 0.25
                    elif ticks_dist < 5:
                        x, y = 0.15, 0.5
                    elif ticks_dist < 8:
                        x, y = 0.15, 1
                    else:
                        x, y = 0.15, 5
                    if slope_list[i] < 0:
                        y = y
                    else:
                        y = -y

                    # daehyuk 20190816 차트 y축 0.000 하단 배치에 따른 0할 5푼 미만 텍스트 미표출
                    if v < 0.050:
                        ax.text(i - x, v + y, '', fontproperties=fontprop, fontsize=10)
                    else:
                        ax.text(i - x, v + y, value if len(str(value).split('.')[1]) == 3
                                else value + '00' if len(str(value).split('.')[1]) == 1
                                else value + '0', fontproperties=fontprop, fontsize=10)
                plt.xticks(fontproperties=fontprop, weight='bold', fontsize=11)
                if max(list(y_)) - min(list(y_)) > 0.1:
                    yticks_list = [str(i)[:3] + '00' for i in np.arange(round(min(list(y_)), 1) - 0.1 if round(min(list(y_)), 1) > 1 else round(min(list(y_)), 1),
                                                                        round(max(list(y_)), 2) + 0.1, 0.1)]
                    plt.yticks(np.arange(round(min(list(y_)), 1) - 0.1 if round(min(list(y_)), 1) > 1 else round(min(list(y_)), 1), round(max(list(y_)), 2) + 0.1, 0.1), yticks_list)
                else:
                    yticks_list = [str(i) if len(str(i).split('.')[1]) == 3 else str(i) + '00'
                                   if len(str(i).split('.')[1]) == 1 else str(i) + '0'
                                   for i in np.arange(round(min(list(y_)), 1), round(max(list(y_)), 2), 0.05)]
                    plt.yticks(np.arange(round(min(list(y_)), 1), round(max(list(y_)), 1), 0.05), yticks_list)
                # daehyuk 20190816 차트 y축 0.000 하단 배치
                #plt.margins(0.2, 0.3)
                if min(list(y_)) < 0.1:
                    plt.margins(x=0.2, y=0.1)
                else:
                    plt.margins(x=0.2, y=0.3)

                plt.title('%s(%s) 월별 %s' % (self.name, g.team_kor_dict[g.GAME_ID[8:10]]
                          if g.WIN_TB == 'T' else g.team_kor_dict[g.GAME_ID[10:12]], self.stat_dict[stat]),
                          fontproperties=fontprop)
                graph_path = '{gmkey}_H'.format(gmkey=g.GAME_ID)
                self.save_fig_file(fig, graph_path)
                plt.close(fig)
                return group_by_month_df, self.stat_dict[stat], stat
        else:
            x_ = [self.month_dict[i] for i in target_dict.keys()]
            y_ = target_dict.values()
            if list(y_)[-1] > list(y_)[-2]:
                color_list = ['#D2D2D2'] * len(target_dict)
                color_list[-1] = '#05173F'
                height_list = [0.5] * len(target_dict)
                fig, ax = plt.subplots(figsize=(6, 4))
                ax.barh(x_, list(y_), alpha=0.7, align='center', color=color_list,
                        height=height_list, edgecolor=color_list)
                values = list(y_)
                for i, v in enumerate(values):
                    ax.text(v - 0.5, i + .1, v, fontweight='bold', fontsize=15, color='#7BD6CF' if i == len(values)-1 else '#5A5A5A')
                plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
                plt.margins(0.3, 0.1)
                ax.spines['right'].set_color('none')
                ax.spines['top'].set_color('none')
                plt.yticks(list(x_), fontproperties=fontprop)
                ax.invert_yaxis()
                ax.set_title('%s(%s) 월별 %s' % (self.name, g.team_kor_dict[g.GAME_ID[8:10]]
                             if g.WIN_TB == 'T' else g.team_kor_dict[g.GAME_ID[10:12]], self.stat_dict[stat]),
                             fontproperties=fontprop, fontsize=20, fontweight='bold')
                graph_path = '{gmkey}_H'.format(gmkey=g.GAME_ID)
                self.save_fig_file(fig, graph_path)
                plt.close(fig)
                return group_by_month_df, self.stat_dict[stat], stat

    def text(self):
        try:
            group_by_month_df, stat, plain_stat = self.hitter_Viz()
            is_exist = True
            g.h_s_is_exist = is_exist
            g.h_s_name = self.name
            g.h_s_stat_name = stat
            g.h_s_today_score = group_by_month_df.iloc[-1][plain_stat]
            g.h_s_last_score = group_by_month_df.iloc[-2][plain_stat]
            g.h_s_game_num = int(group_by_month_df.iloc[-1].game_num)
            g.h_s_last_game_num = int(group_by_month_df.iloc[-2].game_num)
            g.h_s_current_month = self.month_dict[group_by_month_df.index[-1]]
            g.h_s_last_month = self.month_dict[group_by_month_df.index[-2]]
            if g.h_s_today_score >= g.h_s_last_score and len(group_by_month_df) > 2 and g.h_s_game_num > 5 \
               and g.h_s_last_score != 0:
                rep_values = []
                if plain_stat == 'avg' or plain_stat == 'ops':
                    values = group_by_month_df[plain_stat].values
                    for i in range(len(values)):
                        if len(str(values[i]).split('.')[1]) == 3:
                            rep_values.append(str(values[i]))
                        elif len(str(values[i]).split('.')[1]) == 1:
                            rep_values.append(str(values[i])+'00')
                        else:
                            rep_values.append(str(values[i])+'0')
                    g.h_s_today_score = rep_values[-1]
                    g.h_s_last_score = rep_values[-2]
                    g.h_s_today_ab = group_by_month_df.ab[-1]
                    g.h_s_today_hit = group_by_month_df.hit[-1]
                    g.h_s_last_ab = group_by_month_df.ab[-2]
                    g.h_s_last_hit = group_by_month_df.hit[-2]
                return is_exist
            else:
                raise Exception
        except:
            is_exist = False
            return is_exist

    def save_fig_file(self, fig, image_name):
        with io.BytesIO() as img_data:
            fig.savefig(img_data, bbox_inches='tight', format='png')
            image_name += '.png'
            img_data.seek(0)
            self.s3_resource.Bucket(cfg.bucket_name).put_object(Body=img_data, Key=image_name, ACL='public-read', CacheControl='no-cache')
