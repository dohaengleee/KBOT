from blog.lib import globals as g


class PlayerVsTeam(object):
    def __init__(self, team_code):
        self.team_code = team_code
        self.team_kor = None

        g.define_method(self, g.player_vs_team_method)

    def name(self):
        if self.team_kor is None:
            self.team_kor = g.team_kor_dict[self.team_code]

        return self.team_kor

    def is_win(self):
        """
        is_승리
        :return:
        """
        return self.name() == g.WIN_TEAM

    def is_lose(self):
        """
        is_패배
        :return:
        """
        return self.name() == g.LOSE_TEAM

    def is_draw(self):
        """
        is_무승부
        :return:
        """
        return g.IS_DRAW

    def is_home(self):
        """
        is_홈팀
        :return:
        """
        return self.team_code == g.HOME_ID

    def is_away(self):
        """
        is_원정팀
        :return:
        """
        return self.team_code == g.AWAY_ID
