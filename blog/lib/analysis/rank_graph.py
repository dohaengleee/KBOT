from blog.lib import globals as g
from blog import minor_baseball_models as b_models
import pandas as pd
import boto3
import aws.config as cfg
import io
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib as mpl
import warnings
warnings.filterwarnings('ignore')
mpl.style.use('default')
path = './blog/lib/analysis/res/NanumGothic.ttf'
fontprop = fm.FontProperties(fname=path, size=15)


class Rank:
    """
    total 기록 사용하면 안됨!
    (pittotal, team_rank etc...)
    """
    def __init__(self, df_pitcher_2019, game_id, pitcher_code):
        self.pcode = pitcher_code
        self.pitcher = df_pitcher_2019
        self.game_id = game_id

        self.stat_dict = {'ERA': '평균자책점', 'WIN': '승리', 'SAVE': '세이브', 'HOLD': '홀드',
                         'KBB': '볼넷 당 삼진', 'K9': '9이닝 당 삼진', 'BB9': '9이닝 당 볼넷',
                         'KK': '탈삼진', 'GAMENUM': '게임 수'}

        self.league_dict = {'남부리그': ['KIA', 'KT', 'NC', '롯데', '삼성', '상무'], '북부리그': ['LG', 'SK', '고양', '두산', '한화']}

        self.s3_resource = boto3.resource(
            's3',
            aws_access_key_id=cfg.aws_access_key_id,
            aws_secret_access_key=cfg.aws_secret_access_key,
            region_name=cfg.region,
        )

    def ERA(self, df):
        inn = df.inn2 / 3
        temp = round((df.er / inn) * 9, 4)
        if len(str(temp)) <= 3:
            return float(temp)
        elif str(temp)[-2] == '5' and int(str(temp)[-3]) % 2 == 0:
            temp = float(str(temp + 0.01)[:-2])
            return float(str(temp)[:4])
        else:
            result = round((df.er / inn) * 9, 2)
            return float(result)

    def KBB(self, df):  # 삼진볼넷 비율
        return round((df.kk / (df.bb - df.ib)), 2)

    def K9(self, df):  # 9이닝 당 평균삼진
        return round(((df.kk) / round(df.inn2 / 3, 1)) * 9, 2)

    def BB9(self, df):  # 9이닝 당 평균볼넷
        return round(((df.bb - df.ib) / round(df.inn2 / 3, 1)) * 9, 2)

    def WHIP(self, df):  # 이닝 당 출루 허용률
        return round((df.bb + df.ib + df.hit) / round(df.inn2 / 3, 1), 2)

    def get_rank(self):

        pitcher_df = self.pitcher

        # for i in range(len(pitcher_df)):
        #     if pitcher_df.loc[i].name == '합계':
        #         pitcher_df.drop(axis=0, index=i, inplace=True)
        #
        # pitcher_df.reset_index(drop=True, inplace=True)

        w_idx = []
        s_idx = []
        for i in range(len(pitcher_df)):
            if pitcher_df.loc[i]['wls'] == 'W':
                w_idx.append(i)
            elif pitcher_df.loc[i]['wls'] == 'S':
                s_idx.append(i)

        pitcher_df['W'] = 0
        pitcher_df['SV'] = 0
        pitcher_df.set_value(w_idx, 'W', 1)
        pitcher_df.set_value(s_idx, 'SV', 1)
        pitcher_df.fillna(0, inplace=True)
        pitcher_df['start'] = pitcher_df.start.astype('int64').values
        # db4_minor_baseball teamrank_daily는 4월17일 경기부터 존재 (이전경기 데이터는 minor_baseball teamrank_daily에 있음)
        # 퓨처스리그 시상 항목만 적용 (투수 : 평균자책점, 승리 / 타자 : 타율, 홈런, 타점) 190715
        teamrank = dict(g.teamrank_daily_obj.filter(date__startswith=g.GAME_DATE).values_list('team', 'game'))
        if len(teamrank) == 0:
            teamrank = dict(g.b_models.Teamrank.objects.values_list('team', 'game'))
        reg_inn_dict = {}
        for k, v in teamrank.items():
            if k == '기아':
                reg_inn_dict['KIA'] = v * 0.8
            elif k == '우리':
                reg_inn_dict['고양'] = v * 0.8
            else:
                reg_inn_dict[k] = v * 0.8

        g_pitcher = pitcher_df.groupby(['pcode', 'name'], as_index=False).sum()
        team_name = []
        for i in g_pitcher.name:
            team_name.append(b_models.Person.objects.filter(name=i).values_list('team')[0][0])
        g_pitcher['team'] = team_name
        g_pitcher['ERA'] = [self.ERA(g_pitcher.iloc[i])
                            if round(g_pitcher.inn2[i] / 3, 1) + 1 >= reg_inn_dict[g_pitcher.team[i]]
                            else 1000 for i in range(len(g_pitcher))]
        # g_pitcher['KBB'] = self.KBB(g_pitcher)
        # g_pitcher['K9'] = self.K9(g_pitcher)
        # g_pitcher['BB9'] = self.BB9(g_pitcher)
        # g_pitcher['WHIP'] = self.WHIP(g_pitcher)
        g_pitcher.replace(float('inf'), 0, inplace=True)

        target_team = g_pitcher[g_pitcher.pcode == self.pcode].team.values[0]

        if target_team in self.league_dict['남부리그']:
            south_pitcher = pd.DataFrame(columns=g_pitcher.columns)
            so_rank_dict = {}
            for i in range(len(g_pitcher)):
                if g_pitcher.team[i] in self.league_dict['남부리그']:
                    south_pitcher.loc[i] = g_pitcher.values[i]

            SO_ERA = south_pitcher.sort_values(by='ERA').pcode.values.tolist()[:20]
            SO_WIN = south_pitcher.sort_values(by='W', ascending=False).pcode.values.tolist()[:20]
            # SO_SAVE = south_pitcher.sort_values(by='SV', ascending=False).pcode.values.tolist()[:20]
            # SO_HOLD = south_pitcher.sort_values(by='hold', ascending=False).pcode.values.tolist()[:20]
            # SO_KBB = south_pitcher.sort_values(by='KBB', ascending=False).pcode.values.tolist()[:20]
            # SO_WHIP = south_pitcher.sort_values(by='WHIP').pcode.values.tolist()[:20]
            # SO_K9 = south_pitcher.sort_values(by='K9', ascending=False).pcode.values.tolist()[:20]
            # SO_BB9 = south_pitcher.sort_values(by='BB9').pcode.values.tolist()[:20]
            # SO_KK = south_pitcher.sort_values(by='kk', ascending=False).pcode.values.tolist()[:20]

            so_rank_dict['ERA'] = dict(zip([south_pitcher[south_pitcher.pcode == j].name.values[0] for j in SO_ERA[:20]],
                                           [south_pitcher[south_pitcher.pcode == i].ERA.values[0] for i in SO_ERA[:20]]))
            so_rank_dict['WIN'] = dict(zip([south_pitcher[south_pitcher.pcode == j].name.values[0] for j in SO_WIN[:20]],
                                           [south_pitcher[south_pitcher.pcode == i].W.values[0] for i in SO_WIN[:20]]))
            # so_rank_dict['SAVE'] = dict(zip([south_pitcher[south_pitcher.pcode == j].name.values[0] for j in SO_SAVE[:5]],
            #                                 [south_pitcher[south_pitcher.pcode == i].SV.values[0] for i in SO_SAVE[:5]]))
            # so_rank_dict['HOLD'] = dict(zip([south_pitcher[south_pitcher.pcode == j].name.values[0] for j in SO_HOLD[:5]],
            #                                 [south_pitcher[south_pitcher.pcode == i].hold.values[0] for i in SO_HOLD[:5]]))
            # so_rank_dict['KBB'] = dict(zip([south_pitcher[south_pitcher.pcode == j].name.values[0] for j in SO_KBB[:5]],
            #                                [south_pitcher[south_pitcher.pcode == i].KBB.values[0] for i in SO_KBB[:5]]))
            # so_rank_dict['WHIP'] = dict(zip([south_pitcher[south_pitcher.pcode == j].name.values[0] for j in SO_WHIP[:5]],
            #                                 [south_pitcher[south_pitcher.pcode == i].WHIP.values[0] for i in SO_WHIP[:5]]))
            # so_rank_dict['K9'] = dict(zip([south_pitcher[south_pitcher.pcode == j].name.values[0] for j in SO_K9[:5]],
            #                               [south_pitcher[south_pitcher.pcode == i].K9.values[0] for i in SO_K9[:5]]))
            # so_rank_dict['BB9'] = dict(zip([south_pitcher[south_pitcher.pcode == j].name.values[0] for j in SO_BB9[:5]],
            #                                [south_pitcher[south_pitcher.pcode == i].BB9.values[0] for i in SO_BB9[:5]]))
            # so_rank_dict['KK'] = dict(zip([south_pitcher[south_pitcher.pcode == j].name.values[0] for j in SO_KK[:5]],
            #                               [south_pitcher[south_pitcher.pcode == i].kk.values[0] for i in SO_KK[:5]]))

            return so_rank_dict, '남부리그'

        elif target_team in self.league_dict['북부리그']:
            north_pitcher = pd.DataFrame(columns=g_pitcher.columns)
            no_rank_dict = {}
            for i in range(len(g_pitcher)):
                if g_pitcher.team[i] in self.league_dict['북부리그']:
                    north_pitcher.loc[i] = g_pitcher.values[i]

            NO_ERA = north_pitcher.sort_values(by='ERA').pcode.values.tolist()[:20]
            NO_WIN = north_pitcher.sort_values(by='W', ascending=False).pcode.values.tolist()[:20]
            # NO_SAVE = north_pitcher.sort_values(by='SV', ascending=False).pcode.values.tolist()[:20]
            # NO_HOLD = north_pitcher.sort_values(by='hold', ascending=False).pcode.values.tolist()[:20]
            # NO_KBB = north_pitcher.sort_values(by='KBB', ascending=False).pcode.values.tolist()[:20]
            # NO_WHIP = north_pitcher.sort_values(by='WHIP').pcode.values.tolist()[:20]
            # NO_K9 = north_pitcher.sort_values(by='K9', ascending=False).pcode.values.tolist()[:20]
            # NO_BB9 = north_pitcher.sort_values(by='BB9').pcode.values.tolist()[:20]
            # NO_KK = north_pitcher.sort_values(by='kk', ascending=False).pcode.values.tolist()[:20]

            no_rank_dict['ERA'] = dict(zip([north_pitcher[north_pitcher.pcode == j].name.values[0] for j in NO_ERA[:20]],
                                           [north_pitcher[north_pitcher.pcode == i].ERA.values[0] for i in NO_ERA[:20]]))
            no_rank_dict['WIN'] = dict(zip([north_pitcher[north_pitcher.pcode == j].name.values[0] for j in NO_WIN[:20]],
                                           [north_pitcher[north_pitcher.pcode == i].W.values[0] for i in NO_WIN[:20]]))
            # no_rank_dict['SAVE'] = dict(zip([north_pitcher[north_pitcher.pcode == j].name.values[0] for j in NO_SAVE[:5]],
            #                                 [north_pitcher[north_pitcher.pcode == i].SV.values[0] for i in NO_SAVE[:5]]))
            # no_rank_dict['HOLD'] = dict(zip([north_pitcher[north_pitcher.pcode == j].name.values[0] for j in NO_HOLD[:5]],
            #                                 [north_pitcher[north_pitcher.pcode == i].hold.values[0] for i in NO_HOLD[:5]]))
            # no_rank_dict['KBB'] = dict(zip([north_pitcher[north_pitcher.pcode == j].name.values[0] for j in NO_KBB[:5]],
            #                                [north_pitcher[north_pitcher.pcode == i].KBB.values[0] for i in NO_KBB[:5]]))
            # no_rank_dict['WHIP'] = dict(zip([north_pitcher[north_pitcher.pcode == j].name.values[0] for j in NO_WHIP[:5]],
            #                                 [north_pitcher[north_pitcher.pcode == i].WHIP.values[0] for i in NO_WHIP[:5]]))
            # no_rank_dict['K9'] = dict(zip([north_pitcher[north_pitcher.pcode == j].name.values[0] for j in NO_K9[:5]],
            #                               [north_pitcher[north_pitcher.pcode == i].K9.values[0] for i in NO_K9[:5]]))
            # no_rank_dict['BB9'] = dict(zip([north_pitcher[north_pitcher.pcode == j].name.values[0] for j in NO_BB9[:5]],
            #                                [north_pitcher[north_pitcher.pcode == i].BB9.values[0] for i in NO_BB9[:5]]))
            # no_rank_dict['KK'] = dict(zip([north_pitcher[north_pitcher.pcode == j].name.values[0] for j in NO_KK[:5]],
            #                               [north_pitcher[north_pitcher.pcode == i].kk.values[0] for i in NO_KK[:5]]))

            return no_rank_dict, '북부리그'

    def Viz(self):

        try:
            rank_dict, league = self.get_rank()

            pitcher = self.pitcher
            name = pitcher[pitcher.pcode == self.pcode].name.values[0]

            category = list(rank_dict.keys())
            stat = []
            for i in category:
                if name in list(rank_dict[i].keys()):
                    stat.append(i)
            target_key = []
            target_idx = None
            count = 0
            for i in list(rank_dict[stat[0]].keys()):
                team_name = b_models.Person.objects.filter(name=i).values_list('team')
                new_key = i + '(%s)' % (team_name[0])
                rank_dict[stat[0]][new_key] = rank_dict[stat[0]].pop(i)
                if i == name:
                    target_idx = count
                target_key.append(new_key)
                count += 1
            asc_false = ['WIN', 'SAVE', 'HLOD', 'KBB', 'K9', 'KK']
            # asc_true = ['ERA', 'WHIP', 'BB9']
            rank_list = [int(i) for i in pd.Series(rank_dict[stat[0]]).rank(method='min', ascending=False if stat[0] in asc_false else True)]
            fifth_num = None
            if len(pd.Series(rank_list)[pd.Series(rank_list).values == 5]) > 1:
                fifth_num = len(pd.Series(dict(zip(list(rank_dict[stat[0]].keys()), rank_list)))
                                [pd.Series(dict(zip(list(rank_dict[stat[0]].keys()), rank_list))).values == 5])
            target_key = target_key[:5]
            rank_list = rank_list[:5]
            ranking_dict = dict(zip(list(rank_dict[stat[0]].keys()), rank_list))
            target_ranking = ranking_dict[target_key[target_idx]]
            del ranking_dict[target_key[target_idx]]
            is_joint = False
            if target_ranking in list(ranking_dict.values()):
                is_joint = True
            color_list = ['#D2D2D2'] * 5
            color_list[target_idx] = '#05173F'
            height_list = [0.5] * 5

            """
            연한회색:#D2D2D2
            남색:#05173F
            청록색:#7BD6CF
            연한검정색:#5A5A5A
            """

            fig, ax = plt.subplots(figsize=(6, 4))
            if fifth_num:
                yticks_list = list(rank_dict[stat[0]].keys())[:4]
                yticks_list.append(list(rank_dict[stat[0]].keys())[:5][-1] + '외 {num}명'.format(num=fifth_num-1))
                ax.barh(yticks_list,
                        [int(i) if stat[0] == 'hr' or stat[0] == 'rbi' or stat[0] == 'sb' or stat[0] == 'run'
                         or stat[0] == 'hit' or stat[0] == 'total_base'
                         else float(i) for i in list(rank_dict[stat[0]].values())[:5]],
                        color=color_list,
                        alpha=0.7, height=height_list, align='center', edgecolor=color_list)
                plt.yticks(yticks_list, fontproperties=fontprop)
            else:
                ax.barh(list(rank_dict[stat[0]].keys())[:5],
                        [int(i) if stat[0] == 'hr' or stat[0] == 'rbi' or stat[0] == 'sb' or stat[0] == 'run'
                         or stat[0] == 'hit' or stat[0] == 'total_base'
                         else float(i) for i in list(rank_dict[stat[0]].values())[:5]],
                        color=color_list,
                        alpha=0.7, height=height_list, align='center', edgecolor=color_list)
                plt.yticks(list(rank_dict[stat[0]].keys())[:5], fontproperties=fontprop)
            values = list(rank_dict[stat[0]].values())[:5]
            for i in range(len(values)):
                if len(str(values[i]).split('.')[1]) == 2:
                    values[i] = str(values[i])
                else:
                    values[i] = str(values[i]) + '0'
            for i, v in enumerate(values):
                if float(v) == 0:
                    raise Exception
                else:
                    if float(v) < 1:
                        x = 0.5
                    elif float(v) < 5:
                        x = 0.9
                    elif float(v) < 10:
                        x = 1
                    else:
                        x = 5
                    ax.text(float(v) - x, i + .1, v, color='#7BD6CF' if i == target_idx else '#5A5A5A',
                            fontweight='bold', fontsize=15)
            plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
            plt.margins(0.3, 0.1)
            ax.spines['right'].set_color('none')
            ax.spines['top'].set_color('none')
            if stat not in ['ERA', 'WHIP', 'BB9']: ax.invert_yaxis()
            ax.set_title('2019 KBO 퓨처스리그 {stat} TOP5 [{league}]\n'.format(stat=self.stat_dict[stat[0]], league=league), fontproperties=fontprop,
                         fontsize=20, fontweight='bold')
            graph_path = '{gmkey}'.format(gmkey=self.game_id)
            self.save_fig_file(fig, graph_path)
            plt.close(fig)

            return name, self.stat_dict[stat[0]], target_ranking, is_joint, league, values[target_idx]

        except Exception as e:
            print(e, 'rank_graph Viz rank에 없음')
            pass


    def text(self):
        try:
            is_exist = False
            viz = self.Viz()
            name = viz[0]
            stat_name = viz[1]
            target_ranking = viz[2]
            is_joint = viz[3]
            league = viz[4]
            values = viz[5]
            if target_ranking:
                is_exist = True
                g.r_is_exist = True
                g.r_name = name
                g.r_stat_name = stat_name
                g.r_target_ranking = target_ranking
                g.r_is_joint = is_joint
                g.r_league = league
                g.r_values = values
                return is_exist, name, stat_name, target_ranking, is_joint, league, values
        except:
            is_exist = False
            return is_exist

    def save_fig_file(self, fig, image_name):
        img_data = io.BytesIO()
        fig.savefig(img_data, bbox_inches='tight', format='png')
        image_name += '.png'
        img_data.seek(0)
        self.s3_resource.Bucket(cfg.bucket_name).put_object(Body=img_data, Key=image_name, ACL='public-read', CacheControl='no-cache')
        self.url = "https://s3-%s.amazonaws.com/%s/%s" % (cfg.region, cfg.bucket_name, image_name)


class HitterRank:
    def __init__(self, df_hitter_2019, game_id, hitter_code):
        self.pcode = hitter_code
        self.hitter = df_hitter_2019
        self.game_id = game_id

        self.stat_dict = {'avg': '타율', 'hr': '홈런', 'rbi': '타점', 'sb': '도루', 'run': '득점', 'hit': '안타',
                          'obp': '출루율', 'slg': '장타율', 'h2': '2루타', 'h3': '3루타', 'ops': '오피에스',
                          'ab': '타수', 'bb': '볼넷'}

        self.league_dict = {'남부리그': ['KIA', 'KT', 'NC', '롯데', '삼성', '상무'], '북부리그': ['LG', 'SK', '고양', '두산', '한화']}

        self.s3_resource = boto3.resource(
            's3',
            aws_access_key_id=cfg.aws_access_key_id,
            aws_secret_access_key=cfg.aws_secret_access_key,
            region_name=cfg.region,
        )

    def avg(self, df):  # 타율
        return round(df.hit / df.ab, 3)

    def obp(self, df):  # 출루율
        return round((df.hit + df.bb + df.ib + df.hp) / (df.ab + df.bb + df.ib + df.hp + df.sf), 3)

    def slg(self, df):  # 장타율
        return round(((df.h2 * 2) + (df.h3 * 3) + (df.hr * 4) + (df.hit - df.h2 + df.h3 + df.hr)) / df.ab, 3)

    def ops(self, df):  # 오피에스
        return self.obp(df) + self.slg(df)

    def total_base(self, df):  # 루타
        return (df.h2 * 2) + (df.h3 * 3) + (df.hr * 4) + (df.hit - df.h2 + df.h3 + df.hr)

    def get_hitter_rank(self):

        hitter_df = self.hitter

        # 타율, 출루율, 장타율은 규정타석 채운 타자만 인정
        teamrank = dict(g.b_models.Teamrank.objects.filter(gyear__exact=g.GAME_YEAR).values_list('team', 'game'))  # TODO
        reg_inn_dict = {}
        for k, v in teamrank.items():
            if k == '기아':
                reg_inn_dict['KIA'] = int(v * 2.7)
            elif k == '우리':
                reg_inn_dict['고양'] = int(v * 2.7)
            else:
                reg_inn_dict[k] = int(v * 2.7)

        # 퓨처스리그 시상 항목만 적용 (투수 : 평균자책점, 승리 / 타자 : 타율, 홈런, 타점) 190715
        g_hitter = hitter_df.groupby(['pcode', 'name'], as_index=False).sum()
        team_name = []
        for i in g_hitter.pcode:
            team_name.append(b_models.Person.objects.filter(pcode=i).values_list('team')[0][0])
        g_hitter['team'] = team_name
        g_hitter['avg'] = [self.avg(g_hitter.iloc[i])
                            if g_hitter.pa[i] >= reg_inn_dict[g_hitter.team[i]]
                            else 0 for i in range(len(g_hitter))]
        g_hitter['hr'] = g_hitter.hr
        g_hitter['rbi'] = g_hitter.rbi
        # g_hitter['sb'] = g_hitter.sb
        # g_hitter['run'] = g_hitter.run
        # g_hitter['hit'] = g_hitter.hit
        # g_hitter['obp'] = [self.obp(g_hitter.iloc[i])
        #                    if g_hitter.pa[i] >= reg_inn_dict[g_hitter.team[i]]
        #                    else 0 for i in range(len(g_hitter))]
        # g_hitter['slg'] = [self.slg(g_hitter.iloc[i])
        #                    if g_hitter.pa[i] >= reg_inn_dict[g_hitter.team[i]]
        #                    else 0 for i in range(len(g_hitter))]
        # g_hitter['ops'] = [self.ops(g_hitter.iloc[i])
        #                    if g_hitter.pa[i] >= reg_inn_dict[g_hitter.team[i]]
        #                    else 0 for i in range(len(g_hitter))]
        # g_hitter['total_base'] = self.total_base(g_hitter)
        g_hitter.replace(float('inf'), 0, inplace=True)

        target_team = g_hitter[g_hitter.pcode == self.pcode].team.values[0]

        if target_team in self.league_dict['남부리그']:
            south_hitter = pd.DataFrame(columns=g_hitter.columns)
            so_rank_dict = {}
            for i in range(len(g_hitter)):
                if g_hitter.team[i] in self.league_dict['남부리그']:
                    south_hitter.loc[i] = g_hitter.values[i]

            SO_avg = south_hitter.sort_values(by='avg', ascending=False).pcode.values.tolist()[:20]
            SO_hr = south_hitter.sort_values(by='hr', ascending=False).pcode.values.tolist()[:20]
            SO_rbi = south_hitter.sort_values(by='rbi', ascending=False).pcode.values.tolist()[:20]
            # SO_sb = south_hitter.sort_values(by='sb', ascending=False).pcode.values.tolist()[:20]
            # SO_run = south_hitter.sort_values(by='run', ascending=False).pcode.values.tolist()[:20]
            # SO_hit = south_hitter.sort_values(by='hit', ascending=False).pcode.values.tolist()[:20]
            # SO_obp = south_hitter.sort_values(by='obp', ascending=False).pcode.values.tolist()[:20]
            # SO_slg = south_hitter.sort_values(by='slg', ascending=False).pcode.values.tolist()[:20]
            # SO_ops = south_hitter.sort_values(by='ops', ascending=False).pcode.values.tolist()[:20]
            # SO_total_base = south_hitter.sort_values(by='total_base', ascending=False).pcode.values.tolist()[:20]

            so_rank_dict['avg'] = dict(zip([south_hitter[south_hitter.pcode == j].name.values[0] for j in SO_avg[:20]],
                                           [south_hitter[south_hitter.pcode == i].avg.values[0] for i in SO_avg[:20]]))
            so_rank_dict['hr'] = dict(zip([south_hitter[south_hitter.pcode == j].name.values[0] for j in SO_hr[:20]],
                                           [south_hitter[south_hitter.pcode == i].hr.values[0] for i in SO_hr[:20]]))
            so_rank_dict['rbi'] = dict(zip([south_hitter[south_hitter.pcode == j].name.values[0] for j in SO_rbi[:20]],
                                            [south_hitter[south_hitter.pcode == i].rbi.values[0] for i in SO_rbi[:20]]))
            # so_rank_dict['sb'] = dict(zip([south_hitter[south_hitter.pcode == j].name.values[0] for j in SO_sb[:20]],
            #                                 [south_hitter[south_hitter.pcode == i].sb.values[0] for i in SO_sb[:20]]))
            # so_rank_dict['run'] = dict(zip([south_hitter[south_hitter.pcode == j].name.values[0] for j in SO_run[:20]],
            #                                [south_hitter[south_hitter.pcode == i].run.values[0] for i in SO_run[:20]]))
            # so_rank_dict['hit'] = dict(zip([south_hitter[south_hitter.pcode == j].name.values[0] for j in SO_hit[:20]],
            #                                 [south_hitter[south_hitter.pcode == i].hit.values[0] for i in SO_hit[:20]]))
            # so_rank_dict['obp'] = dict(zip([south_hitter[south_hitter.pcode == j].name.values[0] for j in SO_obp[:20]],
            #                               [south_hitter[south_hitter.pcode == i].obp.values[0] for i in SO_obp[:20]]))
            # so_rank_dict['slg'] = dict(zip([south_hitter[south_hitter.pcode == j].name.values[0] for j in SO_slg[:20]],
            #                                [south_hitter[south_hitter.pcode == i].slg.values[0] for i in SO_slg[:20]]))
            # so_rank_dict['ops'] = dict(zip([south_hitter[south_hitter.pcode == j].name.values[0] for j in SO_ops[:20]],
            #                               [south_hitter[south_hitter.pcode == i].ops.values[0] for i in SO_ops[:20]]))
            # so_rank_dict['total_base'] = dict(zip([south_hitter[south_hitter.pcode == j].name.values[0] for j in SO_total_base[:20]],
            #                                [south_hitter[south_hitter.pcode == i].total_base.values[0] for i in SO_total_base[:20]]))

            return so_rank_dict, '남부리그'

        elif target_team in self.league_dict['북부리그']:
            north_hitter = pd.DataFrame(columns=g_hitter.columns)
            no_rank_dict = {}
            for i in range(len(g_hitter)):
                if g_hitter.team[i] in self.league_dict['북부리그']:
                    north_hitter.loc[i] = g_hitter.values[i]

            NO_avg = north_hitter.sort_values(by='avg', ascending=False).pcode.values.tolist()[:20]
            NO_hr = north_hitter.sort_values(by='hr', ascending=False).pcode.values.tolist()[:20]
            NO_rbi = north_hitter.sort_values(by='rbi', ascending=False).pcode.values.tolist()[:20]
            # NO_sb = north_hitter.sort_values(by='sb', ascending=False).pcode.values.tolist()[:20]
            # NO_run = north_hitter.sort_values(by='run', ascending=False).pcode.values.tolist()[:20]
            # NO_hit = north_hitter.sort_values(by='hit', ascending=False).pcode.values.tolist()[:20]
            # NO_obp = north_hitter.sort_values(by='obp', ascending=False).pcode.values.tolist()[:20]
            # NO_slg = north_hitter.sort_values(by='slg', ascending=False).pcode.values.tolist()[:20]
            # NO_ops = north_hitter.sort_values(by='ops', ascending=False).pcode.values.tolist()[:20]
            # NO_total_base = north_hitter.sort_values(by='total_base', ascending=False).pcode.values.tolist()[:20]

            no_rank_dict['avg'] = dict(zip([north_hitter[north_hitter.pcode == j].name.values[0] for j in NO_avg[:20]],
                                           [north_hitter[north_hitter.pcode == i].avg.values[0] for i in NO_avg[:20]]))
            no_rank_dict['hr'] = dict(zip([north_hitter[north_hitter.pcode == j].name.values[0] for j in NO_hr[:20]],
                                           [north_hitter[north_hitter.pcode == i].hr.values[0] for i in NO_hr[:20]]))
            no_rank_dict['rbi'] = dict(zip([north_hitter[north_hitter.pcode == j].name.values[0] for j in NO_rbi[:20]],
                                            [north_hitter[north_hitter.pcode == i].rbi.values[0] for i in NO_rbi[:20]]))
            # no_rank_dict['sb'] = dict(zip([north_hitter[north_hitter.pcode == j].name.values[0] for j in NO_sb[:20]],
            #                                 [north_hitter[north_hitter.pcode == i].sb.values[0] for i in NO_sb[:20]]))
            # no_rank_dict['run'] = dict(zip([north_hitter[north_hitter.pcode == j].name.values[0] for j in NO_run[:20]],
            #                                [north_hitter[north_hitter.pcode == i].run.values[0] for i in NO_run[:20]]))
            # no_rank_dict['hit'] = dict(zip([north_hitter[north_hitter.pcode == j].name.values[0] for j in NO_hit[:20]],
            #                                 [north_hitter[north_hitter.pcode == i].hit.values[0] for i in NO_hit[:20]]))
            # no_rank_dict['obp'] = dict(zip([north_hitter[north_hitter.pcode == j].name.values[0] for j in NO_obp[:20]],
            #                               [north_hitter[north_hitter.pcode == i].obp.values[0] for i in NO_obp[:20]]))
            # no_rank_dict['slg'] = dict(zip([north_hitter[north_hitter.pcode == j].name.values[0] for j in NO_slg[:20]],
            #                                [north_hitter[north_hitter.pcode == i].slg.values[0] for i in NO_slg[:20]]))
            # no_rank_dict['ops'] = dict(zip([north_hitter[north_hitter.pcode == j].name.values[0] for j in NO_ops[:20]],
            #                               [north_hitter[north_hitter.pcode == i].ops.values[0] for i in NO_ops[:20]]))
            # no_rank_dict['total_base'] = dict(zip([north_hitter[north_hitter.pcode == j].name.values[0] for j in NO_total_base[:20]],
            #                                [north_hitter[north_hitter.pcode == i].total_base.values[0] for i in NO_total_base[:20]]))

            return no_rank_dict, '북부리그'

    def hitter_Viz(self):

        try:
            rank_dict, league = self.get_hitter_rank()

            hitter = self.hitter
            name = hitter[hitter.pcode == self.pcode].name.values[0]

            category = list(rank_dict.keys())
            stat = []
            for i in category:
                if name in list(rank_dict[i].keys()):
                    stat.append(i)
            target_key = []
            target_idx = None
            count = 0
            for i in list(rank_dict[stat[0]].keys()):
                team_name = b_models.Person.objects.filter(name=i).values_list('team')
                new_key = i + '(%s)' % (team_name[0])
                rank_dict[stat[0]][new_key] = rank_dict[stat[0]].pop(i)
                if i == name:
                    target_idx = count
                target_key.append(new_key)
                count += 1
            rank_list = [int(i) for i in pd.Series(rank_dict[stat[0]]).rank(method='min', ascending=False)]
            fifth_num = None
            if len(pd.Series(rank_list)[pd.Series(rank_list).values == 5]) > 1:
                fifth_num = len(pd.Series(dict(zip(list(rank_dict[stat[0]].keys()), rank_list)))
                                [pd.Series(dict(zip(list(rank_dict[stat[0]].keys()), rank_list))).values == 5])
            target_key = target_key[:5]
            rank_list = rank_list[:5]
            ranking_dict = dict(zip(list(rank_dict[stat[0]].keys()), rank_list))
            target_ranking = ranking_dict[target_key[target_idx]]
            del ranking_dict[target_key[target_idx]]
            is_joint = False
            if target_ranking in list(ranking_dict.values()):
                is_joint = True
            color_list = ['#D2D2D2'] * 5
            color_list[target_idx] = '#05173F'
            height_list = [0.5] * 5

            """
            연한회색:#D2D2D2
            남색:#05173F
            청록색:#7BD6CF
            연한검정색:#5A5A5A
            """

            fig, ax = plt.subplots(figsize=(6, 4))
            if fifth_num:
                yticks_list = list(rank_dict[stat[0]].keys())[:4]
                yticks_list.append(list(rank_dict[stat[0]].keys())[:5][-1] + '외 {num}명'.format(num=fifth_num-1))
                ax.barh(yticks_list,
                        [int(i) if stat[0] == 'hr' or stat[0] == 'rbi' or stat[0] == 'sb' or stat[0] == 'run'
                         or stat[0] == 'hit' or stat[0] == 'total_base'
                         else float(i) for i in list(rank_dict[stat[0]].values())[:5]],
                        color=color_list,
                        alpha=0.7, height=height_list, align='center', edgecolor=color_list)
                plt.yticks(yticks_list, fontproperties=fontprop)
            else:
                ax.barh(list(rank_dict[stat[0]].keys())[:5],
                        [int(i) if stat[0] == 'hr' or stat[0] == 'rbi' or stat[0] == 'sb' or stat[0] == 'run'
                         or stat[0] == 'hit' or stat[0] == 'total_base'
                         else float(i) for i in list(rank_dict[stat[0]].values())[:5]],
                        color=color_list,
                        alpha=0.7, height=height_list, align='center', edgecolor=color_list)
                plt.yticks(list(rank_dict[stat[0]].keys())[:5], fontproperties=fontprop)
            values = list(rank_dict[stat[0]].values())[:5]
            if stat[0] == 'avg' or stat[0] == 'ops' or stat[0] == 'obp' or stat[0] == 'slg':
                for i in range(len(values)):
                    if len(str(values[i]).split('.')[1]) == 3:
                        values[i] = str(values[i])
                    else:
                        values[i] = str(values[i]) + '0'
                for i, v in enumerate(values):
                    if float(v) == 0:
                        raise Exception
                    ax.text(float(v) - 0.1, i + .1, v, color='#7BD6CF' if i == target_idx else '#5A5A5A',
                            fontweight='bold', fontsize=15)
            else:
                for i, v in enumerate(values):
                    ax.text(v - 2 if v < 10 else v - 3, i + .1, v, color='#7BD6CF' if i == target_idx else '#5A5A5A',
                            fontweight='bold', fontsize=15)
            plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
            plt.margins(0.3, 0.1)
            ax.spines['right'].set_color('none')
            ax.spines['top'].set_color('none')
            ax.invert_yaxis()
            ax.set_title('2019 KBO 퓨처스리그 {stat} TOP5 [{league}]\n'.format(stat=self.stat_dict[stat[0]], league=league), fontproperties=fontprop,
                         fontsize=20, fontweight='bold')
            graph_path = '{gmkey}_H'.format(gmkey=self.game_id)
            self.save_fig_file(fig, graph_path)
            plt.close(fig)

            return name, self.stat_dict[stat[0]], target_ranking, is_joint, league, values[target_idx]

        except Exception as e:
            print(e, 'rank_graph Viz rank에 없음')
            pass

    def text(self):
        try:
            viz = self.hitter_Viz()
            name = viz[0]
            stat_name = viz[1]
            target_ranking = viz[2]
            is_joint = viz[3]
            league = viz[4]
            values = viz[5]
            if target_ranking:
                is_exist = True
                g.h_is_exist = True
                g.h_name = name
                g.h_stat_name = stat_name
                g.h_target_ranking = target_ranking
                g.h_is_joint = is_joint
                g.h_league = league
                g.h_values = values
                return is_exist
        except:
            is_exist = False
            return is_exist

    def save_fig_file(self, fig, image_name):
        img_data = io.BytesIO()
        fig.savefig(img_data, bbox_inches='tight', format='png')
        image_name += '.png'
        img_data.seek(0)
        self.s3_resource.Bucket(cfg.bucket_name).put_object(Body=img_data, Key=image_name, ACL='public-read', CacheControl='no-cache')
        self.url = "https://s3-%s.amazonaws.com/%s/%s" % (cfg.region, cfg.bucket_name, image_name)

