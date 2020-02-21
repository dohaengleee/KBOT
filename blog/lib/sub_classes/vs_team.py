from blog.lib import globals as g


class VsTeam(object):
    def __init__(self, team_code, vs_team_code, team_scores):
        self.team_code = team_code
        self.vs_team_code = vs_team_code
        self.team_scores = team_scores \
            .extra(where=["substring(gmkey, 9, 4) = '{0}{1}' or substring(gmkey, 9, 4) = '{1}{0}'".format(team_code, vs_team_code)])

        g.define_method(self, g.vs_team_method)

    def vs_win_counter(self):
        counter = 0

        for game_count, score in enumerate(self.team_scores):
            if score.gmkey[8:10] == self.team_code and score.tpoint > score.bpoint:
                counter += 1
            elif score.gmkey[10:12] == self.team_code and score.bpoint > score.tpoint:
                counter += 1

        return counter

    def vs_lose_counter(self):
        counter = 0

        for game_count, score in enumerate(self.team_scores):
            if score.gmkey[8:10] == self.team_code and score.tpoint < score.bpoint:
                counter += 1
            elif score.gmkey[10:12] == self.team_code and score.bpoint < score.tpoint:
                counter += 1

        return counter

    def vs_draw_counter(self):
        counter = 0

        for game_count, score in enumerate(self.team_scores):
            if score.tpoint == score.bpoint:
                counter += 1

        return counter

    def vs_consecutive_win(self):
        counter = 0

        for game_count, score in enumerate(self.team_scores):
            if score.gmkey[8:10] == self.team_code and score.tpoint > score.bpoint:
                counter += 1
            elif score.gmkey[10:12] == self.team_code and score.bpoint > score.tpoint:
                counter += 1

            if (game_count + 1) != counter:
                break

        return counter

    def vs_consecutive_lose(self):
        counter = 0

        for game_count, score in enumerate(self.team_scores):
            if score.gmkey[8:10] == self.team_code and score.tpoint < score.bpoint:
                counter += 1
            elif score.gmkey[10:12] == self.team_code and score.bpoint < score.tpoint:
                counter += 1

            if (game_count + 1) != counter:
                break

        return counter

    def vs_after_win_games(self):
        """
        승_이후_경기수
        :return:
        """
        counter = 0

        for game_count, score in enumerate(self.team_scores):
            if game_count == 0:
                counter += 1
                continue
            if score.gmkey[8:10] == self.team_code and score.tpoint > score.bpoint:
                break
            elif score.gmkey[10:12] == self.team_code and score.bpoint > score.tpoint:
                break
            counter += 1

        return counter

    def vs_after_draw_games(self):
        """
        승_이후_무승부수
        :return:
        """
        counter = 0

        for game_count, score in enumerate(self.team_scores):
            if score.tpoint == score.bpoint:
                counter += 1
                continue
            if score.gmkey[8:10] == self.team_code and score.tpoint > score.bpoint:
                break
            elif score.gmkey[10:12] == self.team_code and score.bpoint > score.tpoint:
                break

        return counter

    def half_inning_dynamic_variable(self):
        counter = 0

        for game_count, score in enumerate(self.team_scores):
            if game_count == 0:
                counter += 1
                continue
            if score.gmkey[8:10] == self.team_code and score.tpoint > score.bpoint:
                break
            elif score.gmkey[10:12] == self.team_code and score.bpoint > score.tpoint:
                break

            if score.bpoint == score.tpoint:
                counter += 1
            else:
                break

        return counter

    def vs_previous_consecutive_lose(self):
        counter = 0

        for game_count, score in enumerate(self.team_scores):
            if game_count == 0:
                counter += 1
                continue
            if score.gmkey[8:10] == self.team_code and score.tpoint > score.bpoint:
                break
            elif score.gmkey[10:12] == self.team_code and score.bpoint > score.tpoint:
                break

            if score.gmkey[8:10] == self.team_code and score.tpoint < score.bpoint:
                counter += 1
            elif score.gmkey[10:12] == self.team_code and score.tpoint > score.bpoint:
                counter += 1
            else:
                break

        return counter
