#TODO

# def is_perfectgame(self):
#     """
#     is_퍼펙트게임
#     :return:
#     """
#     var = NamedVariable()
#     pitcher_today = g.pitchers_today
#
#     for pitcher in pitcher_today:
#         team = self.away_team_info if pitcher.tb == 'T' else self.home_team_info
#         vs_team = self.home_team_info if pitcher.tb == 'T' else self.away_team_info
#
#         if pitcher.sho == 1 and pitcher.hit == 0 and pitcher.bb == 0 and pitcher.hp == 0:
#             setattr(var, '퍼펙트게임', True)
#             setattr(var, 'pitcher_code', pitcher.pcode)
#             setattr(var, '투수이름', pitcher.name)
#             setattr(var, '투구수', pitcher.bf)
#             setattr(var, '팀', team)
#             setattr(var, '상대팀', vs_team)
#         elif pitcher.start == 1 and float(
#                 pitcher.inn2 / 3) >= 7 and pitcher.hit <= 1 and pitcher.bb <= 1 and pitcher.hp <= 1:
#             setattr(var, '아까운퍼펙트게임', True)
#             setattr(var, 'pitcher_code', pitcher.pcode)
#             setattr(var, '투수이름', pitcher.name)
#             setattr(var, '투구수', pitcher.bf)
#             setattr(var, '팀', team)
#             setattr(var, '상대팀', vs_team)
#
#     return var
#
#
# def is_nohitnorun(self):
#     """
#     is_노히트노런
#     :return:
#     """
#     var = NamedVariable()
#     setattr(var, '아까운노히트노런', False)
#     pitcher_today = g.pitchers_today
#
#     for pitcher in pitcher_today:
#         team = self.away_team_info if pitcher.tb == 'T' else self.home_team_info
#         vs_team = self.home_team_info if pitcher.tb == 'T' else self.away_team_info
#         if pitcher.start is None:
#             pitcher.start = 0
#         else:
#             pitcher.start = int(pitcher.start)
#
#         if int(pitcher.sho) == 1 and int(pitcher.hit) == 0 and int(pitcher.r) == 0:
#             setattr(var, '노히트노런', True)
#             setattr(var, 'pitcher_code', pitcher.pcode)
#             setattr(var, '투수이름', pitcher.name)
#             setattr(var, '투구수', pitcher.bf)
#             setattr(var, '팀', team)
#             setattr(var, '상대팀', vs_team)
#         elif pitcher.start == 1 and float(pitcher.inn2 / 3) >= 7 and int(pitcher.hit) <= 1:
#             setattr(var, '아까운노히트노런', True)
#             setattr(var, 'pitcher_code', pitcher.pcode)
#             setattr(var, '투수이름', pitcher.name)
#             setattr(var, '투구수', pitcher.bf)
#             setattr(var, '팀', team)
#             setattr(var, '상대팀', vs_team)
#
#     return var