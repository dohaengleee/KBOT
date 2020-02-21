from blog.lib import globals as g
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Circle, RegularPolygon
from matplotlib.path import Path
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D
import warnings
from sklearn.preprocessing import minmax_scale
warnings.filterwarnings('ignore')

path = './res/NanumGothic.ttf'
fontprop = fm.FontProperties(fname=path, size=15)


class RadarGraph:
    # def call_db(self, db, sql):
    #     minor_baseball = pymysql.connect(host='myrds.cqqe2lakgloq.ap-northeast-2.rds.amazonaws.com',
    #                                      port=3306,
    #                                      user='lab2ai',
    #                                      passwd='lab2ailab2ai',
    #                                      db=db,
    #                                      charset='utf8')
    #
    #     curs = minor_baseball.cursor(pymysql.cursors.DictCursor)
    #
    #     sql = sql
    #     curs.execute(sql)
    #     rows = curs.fetchall()
    #     df = pd.DataFrame(data=rows)
    #
    #     return df

    def FIP(self, df):
        return (((13 * df.HR) + (3 * (df.BB - df.IB + df.HP)) - 2 * df.KK) / df.INN) + 3.20

    def WHIP(self, df):  # 이닝 당 출루 허용률
        return (df.BB + df.IB + df.HIT) / df.INN

    def OSA(self, df):  # 피장타율
        return ((1 * df.H1) + (2 * df.H2) + (3 * df.H3) + (4 * df.HR)) / df.AB

    def OBA(self, df):  # 피안타율
        return df.HIT / df.AB

    def OBP(self, df):  # 피출루율
        return (df.HIT + df.BB + df.HP) / (df.AB + df.BB + df.HP + df.SF)

    def OOPS(self, df):
        return self.OBA(df) + self.OBP(df)

    def K9(self, df):  # 9이닝 당 평균삼진
        return (df.KK / df.INN) * 9

    def BB9(self, df):  # 9이닝 당 평균볼넷
        return ((df.BB - df.IB) / df.INN) * 9

    def HR9(self, df):  # 9이닝 당 평균피홈런
        return (df.HR / df.INN) * 9

    def H9(self, df):  # 9이닝 당 평균피안타
        return (df.HIT / df.INN) * 9

    def KBB(self, df):  # 삼진볼넷 비율
        return df.KK / (df.BB - df.IB)

    # def preprocessing(self):
    #
    #     pitcher = self.call_db('minor_baseball', 'SELECT * from pitcher')
    #     pittotal = self.call_db('minor_baseball', 'SELECT * FROM pittotal')
    #
    #     # 이닝 타입 변경 (str -> int)
    #     inn_ls = pittotal.INN.values.tolist()
    #
    #     new_inn_ls = []
    #
    #     for i in inn_ls:
    #         if len(i) == 1:
    #             new_inn_ls.append(int(i))
    #         elif len(i) == 5:
    #             new_inn_ls.append(round(int(i[0]) + (int(i[2]) / 3), 1))
    #         elif len(i) == 6:
    #             new_inn_ls.append(round(int(i[:2]) + (int(i[3]) / 3), 1))
    #         elif len(i) == 7:
    #             new_inn_ls.append(round(int(i[:3]) + (int(i[4]) / 3), 1))
    #         elif len(i) == 8:
    #             new_inn_ls.append(round(int(i[:4]) + (int(i[5] / 3)), 1))
    #         else:
    #             new_inn_ls.append(i)
    #
    #     pittotal['INN'] = new_inn_ls
    #     inn_temp_ls = []
    #
    #     for i in range(len(pittotal.INN.values)):
    #         inn_temp_ls.append(str(pittotal.INN.values[i]).replace("7", "6"))
    #     pittotal['INN'] = inn_temp_ls
    #     pittotal['INN'] = pittotal.INN.astype('float64').values
    #
    #     total_pittotal = pittotal[pittotal.GYEAR == "9999"]
    #     total_pittotal.reset_index(drop=True, inplace=True)
    #
    #     total_pittotal_pcode = total_pittotal.PCODE.unique().tolist()
    #
    #     temp1 = []
    #     for i in range(len(total_pittotal_pcode)):
    #         temp1.append(pitcher[pitcher.PCODE == total_pittotal_pcode[i]].IB.sum())
    #     temp2 = []
    #     for i in range(len(total_pittotal_pcode)):
    #         temp2.append(pitcher[pitcher.PCODE == total_pittotal_pcode[i]].NAME.values[0])
    #     temp3 = []
    #     for i in range(len(total_pittotal_pcode)):
    #         temp3.append(pitcher[pitcher.PCODE == total_pittotal_pcode[i]].AB.sum())
    #     temp4 = []
    #     for i in range(len(total_pittotal_pcode)):
    #         temp4.append(pitcher[pitcher.PCODE == total_pittotal_pcode[i]].H2.sum())
    #     temp5 = []
    #     for i in range(len(total_pittotal_pcode)):
    #         temp5.append(pitcher[pitcher.PCODE == total_pittotal_pcode[i]].H3.sum())
    #
    #     total_pittotal['IB'] = temp1
    #     total_pittotal['AB'] = temp3
    #     total_pittotal['NAME'] = temp2
    #     total_pittotal['H2'] = temp4
    #     total_pittotal['H3'] = temp5
    #
    #     temp6 = []
    #     for i in range(len(total_pittotal)):
    #         temp6.append(total_pittotal.iloc[i].HIT - (
    #                     total_pittotal.iloc[i].H2 + total_pittotal.iloc[i].H3 + total_pittotal.iloc[i].HR))
    #
    #     total_pittotal['H1'] = temp6
    #
    #     temp7 = []
    #     for i in range(len(total_pittotal_pcode)):
    #         temp7.append(pitcher[pitcher.PCODE == total_pittotal_pcode[i]].SF.sum())
    #
    #     total_pittotal['SF'] = temp7
    #
    #     return total_pittotal

    def __init__(self, game_id, pitcher_df, name):
        self.game_id = game_id
        self.name = name
        self.pitcher = pitcher_df
        self.df_total_pitcher = pitcher_df

    def make_stat_df(self):
        total_pittotal = self.df_total_pitcher
        regulation_inn = 92 * 0.8 * 3
        reg_9999_pits = total_pittotal[total_pittotal.INN > regulation_inn].reset_index(drop=True)

        stat_df = pd.DataFrame(columns=['PCODE', 'NAME', 'ERA', 'WHIP', 'OSA', 'OBP', 'OBA', 'OOPS', 'KBB'])
        stat_df['PCODE'] = reg_9999_pits.PCODE.values.tolist()
        stat_df['NAME'] = reg_9999_pits.NAME.values.tolist()
        stat_df['ERA'] = (1 - minmax_scale(reg_9999_pits.ERA.values.tolist()) + 0.1) * 100
        stat_df['WHIP'] = (1 - minmax_scale(self.WHIP(reg_9999_pits)) + 0.1) * 100
        stat_df['OSA'] = (1 - minmax_scale(self.OSA(reg_9999_pits)) + 0.1) * 100
        stat_df['OBP'] = (1 - minmax_scale(self.OBP(reg_9999_pits)) + 0.1) * 100
        stat_df['OBA'] = (1 - minmax_scale(self.OBA(reg_9999_pits)) + 0.1) * 100
        stat_df['OOPS'] = (1 - minmax_scale(self.OOPS(reg_9999_pits)) + 0.1) * 100
        stat_df['KBB'] = (minmax_scale(self.KBB(reg_9999_pits)) + 0.1) * 100
        stat_df['INN'] = (minmax_scale(reg_9999_pits.INN.values.tolist()) + 0.1) * 100

        stat_df.fillna(0, inplace=True)
        stat_df.WHIP.replace(float('inf'), 0, inplace=True)

        return stat_df


def radar_factory(num_vars, frame='circle'):
    """Create a radar chart with `num_vars` axes.

    This function creates a RadarAxes projection and registers it.

    Parameters
    ----------
    num_vars : int
        Number of variables for radar chart.
    frame : {'circle' | 'polygon'}
        Shape of frame surrounding axes.

    """
    # calculate evenly-spaced axis angles
    theta = np.linspace(0, 2*np.pi, num_vars, endpoint=False)

    class RadarAxes(PolarAxes):

        name = 'radar'

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # rotate plot such that the first axis is at the top
            self.set_theta_zero_location('N')

        def fill(self, *args, closed=True, **kwargs):
            """Override fill so that line is closed by default"""
            return super().fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs, ):
            """Override plot so that line is closed by default"""
            lines = super().plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            # FIXME: markers at x[0], y[0] get doubled-up
            if x[0] != x[-1]:
                x = np.concatenate((x, [x[0]]))
                y = np.concatenate((y, [y[0]]))
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(theta), labels, fontproperties=fontprop, fontsize=9)

        def _gen_axes_patch(self):
            # The Axes patch must be centered at (0.5, 0.5) and of radius 0.5
            # in axes coordinates.
            if frame == 'circle':
                return Circle((0.5, 0.5), 0.5)
            elif frame == 'polygon':
                return RegularPolygon((0.5, 0.5), num_vars,
                                      radius=.5, edgecolor="k")
            else:
                raise ValueError("unknown value for 'frame': %s" % frame)

        def draw(self, renderer):
            """ Draw. If frame is polygon, make gridlines polygon-shaped """
            if frame == 'polygon':
                gridlines = self.yaxis.get_gridlines()
                for gl in gridlines:
                    gl.get_path()._interpolation_steps = num_vars
            super().draw(renderer)

        def _gen_axes_spines(self):
            if frame == 'circle':
                return super()._gen_axes_spines()
            elif frame == 'polygon':
                # spine_type must be 'left'/'right'/'top'/'bottom'/'circle'.
                spine = Spine(axes=self,
                              spine_type='circle',
                              path=Path.unit_regular_polygon(num_vars))
                # unit_regular_polygon gives a polygon of radius 1 centered at
                # (0, 0) but we want a polygon of radius 0.5 centered at (0.5,
                # 0.5) in axes coordinates.
                spine.set_transform(Affine2D().scale(.5).translate(.5, .5)
                                    + self.transAxes)


                return {'polar': spine}
            else:
                raise ValueError("unknown value for 'frame': %s" % frame)

    register_projection(RadarAxes)
    return theta


def Viz(stat_df):
    # OSA:피장타율
    # OBA:피안타율
    # OOPS:피OPS
    # OBP:피출루율

    random = np.random.choice(len(stat_df), 1)
    sample = stat_df.values[:, 2:-1][random[0]].tolist()
    mean = stat_df.median()[1:-1].values.tolist()
    q_75 = stat_df.quantile(q=0.75)[:-1].values.tolist()
    # q_25 = test.quantile(q=0.25)[:-1].values.tolist()
    data = [['평균자책점', '출루허용률', '피장타율', '피출루율', '피안타율', '피OPS', '볼삼비'],
            ('%s'%stat_df.iloc[random[0]].NAME, [
                sample,
                mean,
                q_75,
            ])]

    N = len(data[0])
    theta = radar_factory(N, frame='polygon')

    spoke_labels = data.pop(0)
    title, case_data = data[0]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(projection='radar'))
    fig.subplots_adjust(top=0.85, bottom=0.05)

    ax.set_rgrids([20, 40, 60, 80])
    ax.set_title(title,  position=(0.5, 1.1), ha='center', fontproperties=fontprop)

    colors = ['mediumblue','lightslategrey','dimgray']
    for d, color in zip(case_data, colors):
        line = ax.plot(theta, d, marker='o', markersize=8, color=color)
        ax.fill(theta, d,  alpha=0.25, facecolor=color)
    ax.set_varlabels(spoke_labels)

    labels = ('%s'%stat_df.iloc[random[0]].NAME, '평균', '상위25%')
    ax.legend(labels, loc=(0.9, .95), labelspacing=0.1, fontsize='small', prop=fontprop)

    plt.show()


if __name__ == "__main__":
    r = RadarGraph()
    a = r.make_stat_df()
    Viz(a)