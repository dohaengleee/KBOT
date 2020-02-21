from blog.lib import globals as g


class ScoreScenes(object):
    def __init__(self, inn, tb):
        self.inn = inn  # 이닝
        self.tb = tb
        self.tb_to_kor = '초' if self.tb == 'T' else '말'  # 초말
        self.first_score = False  # 선취점
        self.run_away = False  # 달아남
        self.reversal = False  # 역전
        self.chase = False  # 추격
        self.follow = False  # 따라잡음
        self.walk_off = False  # 끝내기
        self.big_inning = False  # 빅이닝
        self.last_score = False  # 마지막득점
        self.last_score_team = False
        self.final_score = False  # 결승득점
        self.final_bat = False  # 결승타
        self.team_score_before = 0
        self.vs_team_score_before = 0
        self.team_score_after = 0
        self.vs_team_score_after = 0
        self.score_gap_before = 0
        self.score_gap_after = 0  # 득점차
        self.t_final_score = 0   # 원정팀_득점
        self.b_final_score = 0   # 홈팀_득점
        self.team_code = g.AWAY_ID if self.tb == 'T' else g.HOME_ID
        self.vs_team_code = g.AWAY_ID if self.tb == 'B' else g.HOME_ID
        self.team_kor = g.team_kor_dict[self.team_code]  # 팀명
        self.vs_team_kor = g.team_kor_dict[self.vs_team_code]  # 상대팀명
        self.score = 0  # 득점수
        self.score_kor = 0  # 득점
        self.wpa_avg = 0
        self.events = g.SCORE_EVENT_DICT["%d%s" % (self.inn, self.tb)]
        self.scene_number = len(self.events)
        self.wpa_rt = 0
        self.set_wpa_rt()

    def set_define_method(self):
        g.define_method(self, g.score_scene_method)

    def set_wpa_rt(self):
        wpa = 0
        for e in self.events:
            wpa += e.get_wpa()
        self.wpa_rt = round(wpa / self.scene_number, 3)
