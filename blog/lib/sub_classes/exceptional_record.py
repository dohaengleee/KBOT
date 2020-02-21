from blog.lib import globals as g
import pandas as pd

class ExceptionalRecord(object):
    def __init__(self, hitter_dict, pitcher_dict):
        self.game_id = hitter_dict['game_id']
        self.h_pcode = hitter_dict['pcode']
        self.h_name = hitter_dict['name']
        self.h_tb = hitter_dict['tb']
        self.h_team = hitter_dict['team_code']

        self.p_pcode = pitcher_dict['pcode']
        self.p_tb = pitcher_dict['tb']
        self.p_team = pitcher_dict['team_code']
        self.p_name = ''
        self.p_vs_hitter_num = None
        self.p_start_inn = None
        self.p_last_inn = None
        self.p_score = None
        self.p_how_list = None
        self.b1 = None
        self.b2 = None
        self.b3 = None
        self.base_dict = None
        self.pitch_count = None
        self.inn = None
        self.kk = None
        self.is_cycling()

    def p_set_data(self):
        pitcher_records = g.gamecontapp.filter(pitcher=self.p_pcode)
        df_pitcher_records = pd.DataFrame(pitcher_records.values())
        total_pitcher_records = g.b_models.Pitcher.objects.filter(pcode=self.p_pcode, gmkey=self.game_id)
        df_total_pitcher_records = pd.DataFrame(total_pitcher_records.values())
        self.p_name = df_pitcher_records.pitname.values[0]
        self.p_vs_hitter_num = len(df_pitcher_records.hitter.unique())
        self.p_start_inn = df_pitcher_records.inn.min()
        self.p_last_inn = df_pitcher_records.inn.max()
        self.p_score = df_pitcher_records.bscore.max() if self.p_tb == 'B' else df_pitcher_records.tscore.max()
        self.p_how_list = df_pitcher_records.how.unique().tolist()
        self.b1 = df_pitcher_records.base1a.values.tolist()
        self.b2 = df_pitcher_records.base2a.values.tolist()
        self.b3 = df_pitcher_records.base3a.values.tolist()
        self.base_dict = {'b1': self.b1, 'b2': self.b2, 'b3': self.b3}
        self.pitch_count = df_total_pitcher_records.bf.values[0]
        self.inn = round(df_total_pitcher_records.inn2.values[0] / 3, 1)
        self.kk = df_total_pitcher_records.kk.values[0]

class NamedVariable:
    pass