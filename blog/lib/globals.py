from django.core.exceptions import ObjectDoesNotExist
import re
import random
import pandas as pd
from datetime import datetime
from blog import config as cfg
from blog import article_models as models
from blog.lib.logger import Logger
from blog.lib.korean import lab2ai_linguistic as linguistic
from blog.baseball_models import PlayerInjury
if cfg.LEAGUE == 'FUTURES':
    from blog import minor_baseball_models as b_models
else:
    from blog import baseball_models as b_models
# import logging
import logging.config

logging.basicConfig(level=logging.DEBUG, filename='log-debug.log')
logging.config.fileConfig(fname='log_config.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

MODEL_DICT = {}
DYNAMIC_MODEL_DICT = {}
DF_GROUP_DICT = {}
LEAGUE = cfg.LEAGUE
LEAGUE_KOR = cfg.LEAGUE_KOR
AWAY_ID = None
HOME_ID = None
AWAY_SCORE = None  # 원정팀 득점
HOME_SCORE = None  # 홈팀 득점
WIN_TEAM = None  # 승리팀
LOSE_TEAM = None  # 패배팀
WIN_TEAM_SCORE = None  # 승리팀 득점
LOSE_TEAM_SCORE = None  # 패배팀 득점
IS_DRAW = False
WIN_TB = None
GAME_YEAR = None
GAME_DATE = None
GAME_ID = None
team_kor_dict = {}
team_method = None
player_vs_team_method = None
vs_team_method = None
player_method = None
half_inning_method = None
game_method = None
event_method = None
hitter_method = None
pitcher_method = None
score_scene_method = None
gamecontapp = None
record_matrix_mix = None
live_text = None
game_info = None
game_scores = None
game_score = None
duplicate_name = None
teamrank_daily_obj = None
hitters_today = None
pitchers_today = None
players_info = None
entry_obj = None
global_param_dict = {}
time_check = True
pitcher_list = None
player_entry = None
matrix_detail = None
df_record_matrix = None
kinds_of_article = ''
hitter_e_article = ''
top_pitcher_cd = ''
EVENT_LIST = []
SCORE_EVENT_DICT = {}
PLAYERS_DICT = {}
VARIABLE_DICT = {}
LOGGER = Logger()

graph_type = None
graph_exist = False
r_is_exist = False
r_name = ''
r_stat_name = ''
r_target_ranking = ''
r_is_joint = ''
r_league = ''
r_values = ''
s_is_exist = False
s_name = ''
s_stat_name = ''
s_length = ''
s_today_score = ''
s_last_score = ''
s_inn = ''
h_graph_exist = False
h_is_exist = False
h_name = ''
h_stat_name = ''
h_target_ranking = ''
h_is_joint = ''
h_league = ''
h_values = ''
h_s_is_exist = False
h_s_name = ''
h_s_stat_name = ''
h_s_today_score = None
h_s_last_score = None
h_s_game_num = None
h_s_last_game_num = None
h_s_current_month = None
h_s_last_month = None
h_s_today_ab = None
h_s_today_hit = None
h_s_last_ab = None
h_s_last_hit = None
graph_text = ''
h_graph_text = ''

highlight = 0

total_rare_nums = None
total_rare_before_nums = None
total_rare_cate = None
total_rare_base_nums = None
total_rare_base_before_nums = None
kinds_of_rare = ''
scarce_how = None

pitcher_accumulate_score = 0

reversal_num = 0
reversal_inn = []

is_called = False
today_weather = ''

great_hitter = ''
used_personal_record = False

half_sentence_used = []

HIT = ['H1', 'HI', 'HB', 'H2', 'H3', 'HR']
HOW_KOR_DICT = {'BB': '밀어내기 볼넷', 'BN': '번트', 'H1': '안타', 'H2': '2루타', 'H3': '3루타', 'HB': '번트안타', 'CS': '도루실패',
                'HI': '내야안타', 'HP': '밀어내기 사구', 'HR': '홈런', 'IB': '고의4구', 'KP': '포일', 'KK': '삼진', 'ER': '실책',
                'KW': '폭투', 'SF': '희생플라이', 'SH': '희생번트', 'B2': '보크', 'BK': '보크', 'PB': '포일', 'GR': '땅볼',
                'P2': '포일', 'SB': '도루', 'SD': '더블스틸', 'ST': '트리플스틸', 'WP': '폭투', 'W2': '폭투', 'GD': '병살타',
                'FC': '선택수비', 'RF': '선택수비', 'OS': '도루실패'
                }
HITTER_HOW_KOR = {'H1': '안타', 'H2': '2루타', 'H3': '3루타', 'HB': '번트안타', 'HI': '내야안타', 'HR': '홈런'}
HITTER_HOW_KOR2 = {
    'FC': '야수선택',
    'RF': '야수선택',
    'CS': '도루실패',
    'FE': '파울실책',
    'ER': '실책',
    'RB': '주루방해',
    'IN': '타격방해',
    'IF': '인필드플라이',
    'KP': '낫아웃포일',
    'KW': '낫아웃폭투',
    'OB': '주루방해',
    'BK': '보크',
    'B2': '보크',
    'P2': '포일',
    'PB': '포일',
    'WP': '폭투',
    'W2': '폭투',
    'TO': '태그아웃'
}
PITCHER_ERR = ['BK', 'B2', 'W2', 'WP', 'P2', 'PB', 'HP']
POS_KOR = {
    '1': '투수',
    '2': '포수',
    '3': '1루수',
    '4': '2루수',
    '5': '3루수',
    '6': '유격수',
    '7': '좌익수',
    '8': '중견수',
    '9': '우익수',
}
#  HOW_CODE_TO_PITCHER_TOP_RANKING_POINT_CODE
P_TOP_RANK_POINT_DICT = {
    'BB': 'BB',  # 볼넷
    'BN': 'NONE',  # 번트
    'FC': 'NONE',  # 야수선택
    'FE': 'NONE',  # 파울실책
    'FF': 'NONE',  # 파울플라이
    'FL': 'NONE',  # 플라이
    'GR': 'NONE',  # 땅볼
    'GD': 'GD',  # 병살타
    'H1': 'HIT',  # 1루타
    'H2': 'HIT',  # 2루타
    'H3': 'HIT',  # 3루타
    'HB': 'HIT',  # 번트안타
    'HI': 'HIT',  # 내야안타
    'HP': 'HP',  # 사구
    'HR': 'HR',  # 홈런
    'IB': 'NONE',  # 고의4구
    'IN': 'NONE',  # 타격방해
    'IF': 'NONE',  # 인필드플라이
    'IP': 'NONE',  # 규칙위반 ???
    'KB': 'KK',  # 쓰리번트
    'KK': 'KK',  # 삼진
    'KN': 'KK',  # 낫아웃
    'KP': 'KK',  # 낫아웃포일 ???
    'KW': 'KK',  # 낫아웃폭투 ???
    'LL': 'NONE',  # 라인드라이브
    'OB': 'NONE',  # 주루방해
    'SF': 'NONE',  # 희생플라이
    'SH': 'NONE',  # 희생번트(희생타)
    'TP': 'GD',  # 삼중살
    'XX': 'NONE',  # 타구맞음(타자) : 자기 타구에 맞음
    'AO': 'NONE',  # 어필아웃
    'BH': 'NONE',  # 타자의 도움
    'BK': 'BK',  # 보크
    'B2': 'BK',  # (기록된) 보크
    'CS': 'NONE',  # 도루실패
    'ER': 'NONE',  # 실책진루
    'FD': 'NONE',  # 주자의재치
    'FO': 'NONE',  # 포스아웃
    'NS': 'NONE',  # 무관심도루
    'OS': 'NONE',  # 도루실패 진루
    'PB': 'NONE',  # 패스트볼
    'P2': 'NONE',  # (기록된)포일
    'PO': 'NONE',  # 견제 아웃
    'RF': 'NONE',  # 선택수비
    'SB': 'NONE',  # 도루
    'SD': 'NONE',  # 더블스틸
    'ST': 'NONE',  # 트리플스틸
    'TO': 'NONE',  # 태그아웃
    'WP': 'WP',  # 폭투
    'W2': 'WP',  # (기록된) 폭투
    'XT': 'NONE',  # 타구맞음(주자)
    'RB': 'NONE'
}

# PITCHER_POINT_HASH
PITCHER_POINT = {
    'WP': -4,
    'BK': -4,
    'HIT': -4,
    'HR': -8,
    'BB': -4,
    'HP': -4,
    'KK': 1,
    'GD': 3,
    'NONE': 0
}

#  HOW_CODE_TO_HITTER_AND_RUNNER_TOP_RANKING_POINT_CODE
H_R_TOP_RANK_POINT_DICT = {
    'BB': 'BB',  # 볼넷
    'BN': 'OUT',  # 번트
    'FC': 'NONE',  # 야수선택
    'FE': 'NONE',  # 파울실책
    'FF': 'OUT',  # 파울플라이
    'FL': 'OUT',  # 플라이
    'GD': 'GD',  # 병살타
    'GR': 'OUT',  # 땅볼
    'H1': 'HIT',  # 1루타
    'H2': 'H2',  # 2루타
    'H3': 'H3',  # 3루타
    'HB': 'HIT',  # 번트안타
    'HI': 'HIT',  # 내야안타
    'HP': 'HP',  # 사구
    'HR': 'HR',  # 홈런
    'IB': 'IB',  # 고의4구
    'IN': 'NONE',  # 타격방해
    'IF': 'OUT',  # 인필드플라이
    'IP': 'OUT',  # 규칙위반 ???
    'KB': 'KK',  # 쓰리번트
    'KK': 'KK',  # 삼진
    'KN': 'KK',  # 낫아웃
    'KP': 'KK',  # 낫아웃포일
    'KW': 'KK',  # 낫아웃폭투
    'LL': 'OUT',  # 라인드라이브
    'OB': 'NONE',  # 주루방해
    'SF': 'SF',  # 희생플라이
    'SH': 'SH',  # 희생번트(희생타)
    'TP': 'GD',  # 삼중살
    'XX': 'OUT',  # 타구맞음(타자) : 자기 타구에 맞음
    'AO': 'OUT',  # 어필아웃
    'BH': 'NONE',  # 타자의 도움
    'BK': 'NONE',  # 보크
    'B2': 'NONE',  # (기록된) 보크
    'CS': 'CS',  # 도루실패
    'ER': 'NONE',  # 실책진루
    'FD': 'NONE',  # 주자의재치
    'FO': 'OUT',  # 포스아웃
    'NS': 'NONE',  # 무관심도루
    'OS': 'NONE',  # 도루실패 진루
    'PB': 'NONE',  # 패스트볼
    'P2': 'NONE',  # (기록된)포일
    'PO': 'OUT',  # 견제 아웃
    'RF': 'NONE',  # 선택수비
    'SB': 'SB',  # 도루
    'SD': 'SB',  # 더블스틸
    'ST': 'SB',  # 트리플스틸
    'TO': 'OUT',  # 태그아웃
    'WP': 'NONE',  # 폭투
    'W2': 'NONE',  # (기록된) 폭투
    'XT': 'NONE',  # 타구맞음(주자)
    'RB': 'NONE'  # 주루방해
}

# HITTER_AND_RUNNER_POINT
H_R_POINT = {
    'HIT': 2,
    'H2': 4,
    'H3': 6,
    'HR': 10,
    'BB': 2,
    'HP': 2,
    'IB': 2.4,
    'SH': 1.2,
    'SF': 1.6,
    'KK': -1.2,
    'GD': -5,
    'SB': 1.6,
    'CS': -1.2,
    'OUT': -1,
    'NONE': 0
}

pitcher_how_kor_dict = {
    'FL': '뜬공', 'FF': '뜬공', 'LL': '뜬공', 'IF': '인필드 플라이 아웃', 'BN': '땅볼(번트)아웃', 'GD': '병살타', 'GR': '땅볼', 'KK': '삼진',
    'KB': '스트라이크 낫아웃', 'KN': '스트라이크 낫아웃', 'KW': '스트라이크 낫아웃', 'KP': '스트라이크 낫아웃', 'TP': '삼중살',
    'HI': '내야안타', 'H1': '안타', 'H2': '2루타', 'H3': '3루타', 'HB': '번트안타', 'HR': '홈런', 'BB': '볼넷', 'HP': '몸에 맞는 볼',
    'IB': '고의 사구', 'IN': '포수 실책', 'SB': '도루', 'B2': '보크', 'BK': '보크', 'PB': '포일', 'ER': '실책',
    'FE': '수비 파울 실책', 'SD': '더블스틸', 'RF': '선택수비', 'SF': '희생플라이', 'SH': '희생번트',
    'WP': '폭투', 'W2': '폭투', 'CS': '도루저지', 'FO': '포스아웃', 'TO': '태그아웃', 'PO': '견제구',
    'BH': '진루', 'AO': '어필아웃', 'FC': '야수선택', 'XT': '타구맞음', 'P2': '??', 'FD': '??', 'NS': '??', 'OS': '??', 'XX': '??'
}

# field에 따른 수비
defense_kor_dict = {'1': '투수', '2': '', '3': '1루수', '4': '2루수', '5': '3루수', '6': '유격수', '7': '좌익수',
                    '8': '중견수', '9': '우익수', '78': '좌중간', '89': '우중간'}

cont_list = ['FO', 'TO']

sacrifice = ['SF', 'SH']

pos_consider = ['CS', 'PO']

neg_consider = ['SB', 'B2', 'BK', 'PB', 'ER', 'FE', 'SD', 'WP', 'W2']

pitcher_ignore_list = [
    'RF', "FC", "P2", "FD", "BH", "NS", "OS", "XX", "AO", "XT",
]

hit_out_list = ['GR', 'FL', 'IF', 'LL', 'GD', 'TP']


hitter_ignore_list = [
    'TO', 'FO', "FC", "AO", "XT", "FL"
]


def initialize(game_id):
    global LEAGUE_KOR
    global LEAGUE
    global AWAY_ID
    global HOME_ID
    global WIN_TEAM
    global LOSE_TEAM
    global IS_DRAW
    global WIN_TB
    global AWAY_SCORE
    global HOME_SCORE
    global WIN_TEAM_SCORE
    global LOSE_TEAM_SCORE
    global GAME_YEAR
    global GAME_DATE
    global GAME_ID
    global team_kor_dict
    global team_method
    global player_vs_team_method
    global vs_team_method
    global player_method
    global half_inning_method
    global game_method
    global event_method
    global hitter_method
    global pitcher_method
    global score_scene_method
    global gamecontapp
    global record_matrix_mix
    global live_text
    global game_info
    global game_scores
    global game_score
    global duplicate_name
    global teamrank_daily_obj
    global hitters_today
    global pitchers_today
    global players_info
    global entry_obj
    global global_param_dict
    global pitcher_list
    global player_entry
    global PLAYERS_DICT
    global EVENT_LIST
    global SCORE_EVENT_DICT
    global MODEL_DICT
    global DF_GROUP_DICT
    global VARIABLE_DICT
    global DYNAMIC_MODEL_DICT
    global LOGGER
    global matrix_detail
    global df_record_matrix
    global kinds_of_article
    global hitter_e_article
    global graph_type
    global graph_exist
    global r_is_exist
    global r_name
    global r_stat_name
    global r_target_ranking
    global r_is_joint
    global r_league
    global r_values
    global s_is_exist
    global s_name
    global s_stat_name
    global s_length
    global s_today_score
    global s_last_score
    global s_inn
    global h_graph_exist
    global h_is_exist
    global h_name
    global h_stat_name
    global h_target_ranking
    global h_is_joint
    global h_league
    global h_values
    global h_s_is_exist
    global h_s_name
    global h_s_stat_name
    global h_s_today_score
    global h_s_last_score
    global h_s_game_num
    global h_s_last_game_num
    global h_s_current_month
    global h_s_last_month
    global h_s_today_ab
    global h_s_today_hit
    global h_s_last_ab
    global h_s_last_hit
    global h_graph_text
    global graph_text
    global highlight
    global kinds_of_rare
    global scarce_how
    global pitcher_accumulate_score
    global total_rare_nums
    global total_rare_before_nums
    global total_rare_cate
    global total_rare_base_nums
    global total_rare_base_before_nums
    global reversal_num
    global reversal_inn
    global is_called
    global today_weather
    global great_hitter
    global used_personal_record
    global half_sentence_used
    LOGGER.__init__()

    # region Clear Values
    MODEL_DICT = {}
    DYNAMIC_MODEL_DICT = {}
    DF_GROUP_DICT = {}
    AWAY_ID = None
    HOME_ID = None
    AWAY_SCORE = None  # 원정팀 득점
    HOME_SCORE = None  # 홈팀 득점
    WIN_TEAM = None  # 승리팀
    LOSE_TEAM = None  # 패배팀
    WIN_TEAM_SCORE = None  # 승리팀 득점
    LOSE_TEAM_SCORE = None  # 패배팀 득점
    IS_DRAW = False
    WIN_TB = None
    GAME_YEAR = None
    GAME_DATE = None
    GAME_ID = None
    team_kor_dict = {}
    team_method = None
    player_vs_team_method = None
    vs_team_method = None
    player_method = None
    half_inning_method = None
    game_method = None
    event_method = None
    hitter_method = None
    pitcher_method = None
    score_scene_method = None
    gamecontapp = None
    record_matrix_mix = None
    live_text = None
    game_info = None
    game_scores = None
    game_score = None
    duplicate_name = None
    teamrank_daily_obj = None
    hitters_today = None
    pitchers_today = None
    players_info = None
    entry_obj = None
    global_param_dict = {}
    pitcher_list = None
    player_entry = None
    matrix_detail = None
    df_record_matrix = pd.DataFrame()
    EVENT_LIST = []
    SCORE_EVENT_DICT = {}
    PLAYERS_DICT = {}
    VARIABLE_DICT = {}
    LOGGER = Logger()
    kinds_of_article = ''
    hitter_e_article = ''
    graph_type = None
    graph_exist = False
    r_is_exist = False
    r_name = ''
    r_stat_name = ''
    r_target_ranking = ''
    r_is_joint = ''
    r_league = ''
    r_values = ''
    s_is_exist = False
    s_name = ''
    s_stat_name = ''
    s_length = ''
    s_today_score = ''
    s_last_score = ''
    s_inn = ''
    h_graph_exist = False
    h_is_exist = False
    h_name = ''
    h_stat_name = ''
    h_target_ranking = ''
    h_is_joint = None
    h_league = ''
    h_values = ''
    h_s_is_exist = False
    h_s_name = ''
    h_s_stat_name = ''
    h_s_today_score = None
    h_s_last_score = None
    h_s_game_num = None
    h_s_last_game_num = None
    h_s_current_month = None
    h_s_last_month = None
    h_s_today_ab = None
    h_s_today_hit = None
    h_s_last_ab = None
    h_s_last_hit = None
    h_graph_text = ''
    graph_text = ''
    highlight = 0
    kinds_of_rare = ''
    scarce_how = None
    pitcher_accumulate_score = 0
    total_rare_nums = None
    total_rare_before_nums = None
    total_rare_cate = None
    total_rare_base_nums = None
    total_rare_base_before_nums = None
    reversal_num = 0
    reversal_inn = []
    is_called = False
    today_weather = ''
    great_hitter = ''
    used_personal_record = False
    half_sentence_used = []
    # endregion Clear Values

    MODEL_DICT = {
        'event_dynamic_variable': models.EventDynamicVariable,
        'common_dynamic_variable': models.CommonDynamicVariable,
        'player_dynamic_variable': models.PlayerDynamicVariable,
        'hitterrecord_dynamic_variable': models.HitterrecordDynamicVariable,
        'pitcherrecord_dynamic_variable': models.PitcherrecordDynamicVariable,
        'half_inning_dynamic_variable': models.HalfInningDynamicVariable,
        'base_player_sentence': models.BasePlayerSentence,
        'base_sentence': models.BaseSentence,
        'base_team_sentence': models.BaseTeamSentence,
        'base_template': models.BaseTemplate,
        'game_articles': models.GameArticles,
        'method_info': models.MethodInfo,
        'base_half_inning': models.BaseHalfInning,
        'team_method': models.TeamMethod,
        'base_pitcher': models.BasePitcher,
        'pitcher_sentence': models.PitcherSentence,
        'pitcher_player_sentence': models.PitcherPlayerSentence,
        'exceptional_sentence': models.ExceptionalSentence,
        'base_exceptional': models.BaseExceptional,
        'exceptional_player_sentence':models.ExceptionalPlayerSentence,
        'exceptional_team_sentence':models.ExceptionalTeamSentence,
    }

    DYNAMIC_MODEL_DICT = {
        'event_dynamic_variable': models.EventDynamicVariable,
        'common_dynamic_variable': models.CommonDynamicVariable,
        'player_dynamic_variable': models.PlayerDynamicVariable,
        'hitterrecord_dynamic_variable': models.HitterrecordDynamicVariable,
        'pitcherrecord_dynamic_variable': models.PitcherrecordDynamicVariable,
        'half_inning_dynamic_variable': models.HalfInningDynamicVariable,
    }

    for (name, model) in DYNAMIC_MODEL_DICT.items():
        VARIABLE_DICT[name] = init_dynamic_variable(model)

    EVENT_LIST = []
    SCORE_EVENT_DICT.clear()
    PLAYERS_DICT = {}
    global_param_dict = {}
    GAME_ID = game_id
    GAME_YEAR = game_id[0:4]
    GAME_DATE = game_id[0:8]
    AWAY_ID = game_id[8:10]
    HOME_ID = game_id[10:12]

    if cfg.LEAGUE == 'FUTURES':
        team_name = b_models.TeamLeague.objects.filter(gyear=GAME_YEAR)
    else:
        team_name = b_models.TeamName.objects

    if cfg.LEAGUE == 'FUTURES':
        for k, v in team_name.values_list('team', 'teamname'):
            team_kor_dict[k] = v
    else:
        for k, v in team_name.values_list('team', 'team_kor'):
            team_kor_dict[k] = v

    matrix_detail = b_models.MatrixDetail.objects.filter(season_id=GAME_YEAR)
    game_score = b_models.Score.objects.get(gmkey__exact=game_id)
    gamecontapp = b_models.Gamecontapp.objects.filter(gmkey__exact=game_id).order_by('serno')
    record_matrix_mix = b_models.IeRecordMatrixMix.objects.filter(gameid__exact=game_id).order_by('seqno')
    # if record_matrix_mix.last().inn_no != gamecontapp.last().inn:
    #     raise ValueError('record_matrix_mix Data invalid')
    method_obj = models.MethodInfo.objects
    duplicate_name = b_models.DuplicateName.objects
    game_info = b_models.Gameinfo.objects.get(gmkey__exact=game_id)
    live_text = b_models.IeLivetextScoreMix.objects.filter(gameid__exact=game_id).order_by('seqno')
    teamrank_daily_obj = b_models.TeamrankDaily.objects.filter(date__exact=GAME_DATE).values()
    hitters_today = b_models.Hitter.objects.filter(gmkey__exact=game_id).exclude(pcode__in=['T', 'B'])
    pitchers_today = b_models.Pitcher.objects.filter(gmkey__exact=game_id).exclude(pcode__in=['T', 'B'])
    entry_obj = b_models.Entry.objects.filter(gmkey__exact=game_id)
    player_entry = entry_obj.values_list('pcode', 'turn', 'posi', 'team', named=True)

    pitcher_list = entry_obj.filter(posi__endswith=1).values_list('pcode', flat=True)
    players_info = b_models.Person.objects.filter(pcode__in=entry_obj.values_list('pcode'))

    team_method = get_dict_method(method_obj.filter(name__exact='team'))
    player_vs_team_method = get_dict_method(method_obj.filter(name__exact='player_vs_team'))
    vs_team_method = get_dict_method(method_obj.filter(name__exact='vs_team'))
    player_method = get_dict_method(method_obj.filter(name__exact='player'))
    game_method = get_dict_method(method_obj.filter(name__exact='game'))
    event_method = get_dict_method(method_obj.filter(name__exact='event'))
    hitter_method = get_dict_method(method_obj.filter(name__exact='hitter_record'))
    pitcher_method = get_dict_method(method_obj.filter(name__exact='pitcher_record'))
    score_scene_method = get_dict_method(method_obj.filter(name__exact='score_scene'))
    half_inning_method = get_dict_method(method_obj.filter(name__exact='half_inning'))

    if df_record_matrix.empty:
        df_record_matrix = get_df_record_matrix(gamecontapp)

    AWAY_SCORE = game_score.tpoint
    HOME_SCORE = game_score.bpoint

    if AWAY_SCORE > HOME_SCORE:
        WIN_TEAM = team_kor_dict[AWAY_ID]
        LOSE_TEAM = team_kor_dict[HOME_ID]
        WIN_TEAM_SCORE = AWAY_SCORE
        LOSE_TEAM_SCORE = HOME_SCORE
        IS_DRAW = False
        WIN_TB = 'T'
    elif AWAY_SCORE < HOME_SCORE:
        WIN_TEAM = team_kor_dict[HOME_ID]
        LOSE_TEAM = team_kor_dict[AWAY_ID]
        WIN_TEAM_SCORE = HOME_SCORE
        LOSE_TEAM_SCORE = AWAY_SCORE
        IS_DRAW = False
        WIN_TB = 'B'
    else:
        WIN_TEAM = team_kor_dict[AWAY_ID]
        LOSE_TEAM = team_kor_dict[HOME_ID]
        WIN_TEAM_SCORE = HOME_SCORE
        LOSE_TEAM_SCORE = AWAY_SCORE
        IS_DRAW = True
        WIN_TB = None


def define_method(obj, method_dict):
    for k, v in method_dict.items():
        setattr(obj, k, getattr(obj, v))


def get_random_sentence(text):
    temp_list = [d.strip() for d in text.split('@') if d]  # 공백제거
    if not temp_list:
        temp_list.append('')
    return random.choice(temp_list)


def get_josa(text):
    # result = text
    result = linguistic.get_josa(text)
    # brace = []
    # for i, s_str in enumerate(result):
    #     brace.append(s_str)
    #     if s_str == '#':
    #         index = result.index(s_str)
    #         l_str = result[index - 1]
    #         c_str = result[index + 1]
    #         if l_str == ')':
    #             while brace.pop() != '(':
    #                 pass
    #             l_str = brace[-1]
    #             brace = []
    #         change_form = "{0:%s}" % c_str
    #         change_words = l10n.Template(change_form).format(l_str)[1:]
    #         result = "".join((result[:index], change_words, result[index + 2:]))
    return result


def init_dynamic_variable(model):
    df_dynamic_group = pd.DataFrame(list(model.objects.values())).groupby(['group', 'name', 'rank'])

    var_dict = {}
    for d in df_dynamic_group:
        var_name = d[0][1]  # name key
        var_list = d[1].to_dict('record')  # data value list

        selected_var_dict = random.choice(var_list)
        if selected_var_dict['use'] == 'F':
            continue

        if var_name in var_dict:
            var_dict[var_name].append(selected_var_dict)
        else:
            var_dict[var_name] = [selected_var_dict]

    return var_dict


def get_by_name(var, var_name, table_name, used_variable_dict):
    result = ''
    model = MODEL_DICT[table_name]
    dynamic = model.objects.filter(name=var_name)
    df_dynamic_group = pd.DataFrame(list(dynamic.values())).groupby(['group', 'name', 'rank'])
    param_dict = {}
    for d in df_dynamic_group:
        # var_name = d[0][1]  # name key
        var_list = d[1].to_dict('record')  # data value list
        used_key = "%s-%s" % (var_name, d[0][2])

        # 중복 검사하는 Dictionary 를 생성한다.
        if used_key not in used_variable_dict:
            used_variable_dict[used_key] = []

        var_dict = random.choice(var_list)
        if var_dict['use'] == 'F':
            used_variable_dict[used_key].append(var_dict['index'])
            continue

        # selected_var_dict = random.choice(var_list)
        # if selected_var_dict['use'] == 'F':
        #     continue

        # condition = get_condition(selected_var_dict['condition'], var)
        condition = get_condition(var_dict['condition'], var)

        # 중복 제거
        if condition and var_name in ['_하프이닝_시작문장', '_하프이닝_끝문장']:
            if var_dict['index'] in used_variable_dict[used_key]:
                continue
            else:
                used_variable_dict[used_key].append(var_dict['index'])
            # 중복 저장 리스트 Flush
            variable_list_length = len(var_list)
            used_list_length = len(used_variable_dict[used_key])
            if variable_list_length == used_list_length:
                used_variable_dict[used_key] = []

        if condition:
            str_sentence = get_result_string(param_dict, var_dict['sentence'], var)
            if var_dict['eval'] == 'T':
                result = eval(str_sentence)
            else:
                text = str_sentence
                text = get_josa(text)
                result = text
            break
    return result


def set_half_inning_variable(var, table_name, used_variable_dict):
    if table_name in DF_GROUP_DICT:
        df_dynamic_group = DF_GROUP_DICT[table_name]
    else:
        model = MODEL_DICT[table_name]
        df_dynamic_group = pd.DataFrame(list(model.objects.values())).groupby(['group', 'name', 'rank'])
        DF_GROUP_DICT[table_name] = df_dynamic_group

    half_param_dict = {}
    for d in df_dynamic_group:
        var_name = d[0][1]  # name key
        var_list = d[1].to_dict('record')  # data value list
        used_key = "%s-%s" % (d[0][1], d[0][2])

        if var_name in var.__dict__:
            continue

        # 중복 검사하는 Dictionary 를 생성한다.
        if used_key not in used_variable_dict:
            used_variable_dict[used_key] = []

        var_dict = random.choice(var_list)
        if var_dict['use'] == 'F':
            used_variable_dict[used_key].append(var_dict['index'])
            continue

        condition = get_half_inning_condition(half_param_dict, var_dict['condition'], var)

        # 중복 제거
        # if condition and var_name in ['_하프이닝_시작문장', '_하프이닝_끝문장']:
        #     if var_dict['index'] in used_variable_dict[used_key]:
        #         continue
        #     else:
        #         used_variable_dict[used_key].append(var_dict['index'])
        #     # 중복 저장 리스트 Flush
        #     variable_list_length = len(var_list)
        #     used_list_length = len(used_variable_dict[used_key])
        #     if variable_list_length == used_list_length:
        #         used_variable_dict[used_key] = []
        if condition and var_name in ['_하프이닝_시작문장', '_하프이닝_끝문장']:
            if var_dict['index'] in half_sentence_used:
                if '만들었다' in d[1].sentence.values[0]:
                    pass
                else:
                    continue
            else:
                half_sentence_used.append(var_dict['index'])
            # 중복 저장 리스트 Flush
            variable_list_length = len(var_list)
            used_list_length = len(used_variable_dict[used_key])
            if variable_list_length == used_list_length:
                used_variable_dict[used_key] = []

        if condition:
            str_sentence = get_half_result_string(half_param_dict, var_dict['sentence'], var)
            if var_dict['eval'] == 'T':
                setattr(var, var_dict['name'], eval(str_sentence))
            else:
                text = str_sentence
                text = get_josa(text)
                setattr(var, var_dict['name'], text)


def set_variable(var, table_name):
    if table_name in DF_GROUP_DICT:
        df_dynamic_group = DF_GROUP_DICT[table_name]
    else:
        model = MODEL_DICT[table_name]
        df_dynamic_group = pd.DataFrame(list(model.objects.values())).groupby(['group', 'name', 'rank'])
        DF_GROUP_DICT[table_name] = df_dynamic_group

    for d in df_dynamic_group:
        var_name = d[0][1]  # name key
        var_list = d[1].to_dict('record')  # data value list

        if var_name in var.__dict__:
            continue

        var_dict = random.choice(var_list)
        if var_dict['use'] == 'F':
            continue

        condition = get_global_condition(var_dict['condition'], var)
        if condition:
            # LOGGER.adder('INFO', table_name, 'CONDITION', var_dict)
            str_sentence = get_result_string(global_param_dict, var_dict['sentence'], var)
            if var_dict['eval'] == 'T':
                text = eval(str_sentence)
                setattr(var, var_dict['name'], text)
            else:
                text = str_sentence
                text = get_josa(text)
                setattr(var, var_dict['name'], text)
            # LOGGER.adder('RESULT', table_name, '문장', text)
            # LOGGER.adder('PARAM', table_name, 'PARAM', (var_dict['sentence'], var))


def get_attr(variable, str_list):
    if str_list:
        s = str_list.pop(0)

        if s[0] == '_':
            attr_value = get_dynamic_variable(variable, s)
        else:
            attr_value = getattr(variable, s, '')

        if callable(attr_value):
            val = attr_value()
            if not callable(val):
                setattr(variable, s, val)
        else:
            val = attr_value

        if str_list:
            return get_attr(val, str_list)
        else:
            return val


def get_dynamic_variable(val, variable):
    variable_result = getattr(val, variable, '')
    param_dict = {}
    if type(variable_result) != list:
        return variable_result

    for var_dict in variable_result:
        cond = get_condition(var_dict['condition'], val)
        if cond:
            str_sentence = get_result_string(param_dict, var_dict['sentence'], val)

            if str_sentence:
                if var_dict['eval'] == 'T':
                    text = eval(str_sentence)
                else:
                    text = str_sentence
                    text = get_josa(text)
            else:
                text = str_sentence

            setattr(val, var_dict['name'], text)
            return text
    return ''


def get_half_inning_condition(param_dict, condition, val):
    cond_list = condition.split('and')
    for cond in cond_list:
        split_condition = cond
        reg = r"\{(.+?)\}"
        param_list = re.findall(reg, cond)

        if not param_list:
            continue

        for param in param_list:
            if param not in param_dict:
                p = param.split('.')
                value = get_attr(val, p)
                if value == '':
                    value = False

                param_dict.update({param: value})

        for param in param_list:
            split_condition = split_condition.replace("{%s}" % param, "%s" % param_dict[param])

        if eval(split_condition):
            continue
        else:
            return False
    return True


def get_global_condition(condition, val):
    cond_list = condition.split('and')
    for cond in cond_list:
        split_condition = cond
        reg = r"\{(.+?)\}"
        param_list = re.findall(reg, cond)

        if not param_list:
            continue

        for param in param_list:
            if param not in global_param_dict:
                p = param.split('.')
                value = get_attr(val, p)
                if value == '':
                    value = False

                setattr(val, param, value)
                global_param_dict.update({param: value})

        for param in param_list:
            split_condition = split_condition.replace("{%s}" % param, "%s" % global_param_dict[param])

        if eval(split_condition):
            continue
        else:
            return False
    return True


def get_condition(condition, val):
    split_condition = cond = condition
    reg = r"\{(.+?)\}"
    param_list = re.findall(reg, cond)
    param_dict = {}

    if not param_list and condition != 'True':
        return False

    for param in param_list:
        p = param.split('.')
        value = get_attr(val, p)
        if value == '':
            value = False

        param_dict.update({param: value})

    for param in param_list:
        split_condition = split_condition.replace("{%s}" % param, "%s" % param_dict[param])

    if eval(split_condition):
        return True
    else:
        return False


def get_half_result_string(param_dict, sentence, var, final=False):
    result = sentence
    reg = r"\{(.+?)\}"
    param_list = re.findall(reg, result)

    if param_list:
        for param in param_list:
            p = param.split('.')

            if param not in param_dict:
                if param == '생략':
                    param_dict.update({param: ''})
                else:
                    param_dict.update({param: get_attr(var, p)})

        if final and result != '{생략}':
            logger.debug("{0}: %s".format(result), param_dict)
        for param in param_list:
            if not param_dict[param] and type(param_dict[param]) != int:
                param_dict[param] = ''
            result = result.replace("{%s}" % param, "%s" % param_dict[param])
    if final:
        logger.info("[Condition]: {0}".format(result))
    return result


def get_result_string(param_dict, sentence, var, final=False):
    result = sentence
    reg = r"\{(.+?)\}"
    param_list = re.findall(reg, result)
    if param_list:
        for param in param_list:
            p = param.split('.')

            if param == '생략':
                param_dict.update({param: ''})
            else:
                param_dict.update({param: get_attr(var, p)})
        if final and result != '{생략}':
            logger.debug("{0}: %s".format(result), param_dict)
        for param in param_list:
            result = result.replace("{%s}" % param, "%s" % param_dict[param])
    if final:
        logger.info("[Condition]: {0}".format(result))
    return result


def get_dict_method(object_value):
    values = object_value.values()
    return {v['kor']: v['method'] for v in values}


def get_pitcher_total_obj(pitcher_code):
    return b_models.Pitcher.objects.filter(pcode__exact=pitcher_code)


def get_scores_obj(team_code):
    return b_models.Score.objects \
        .filter(gday__startswith=GAME_YEAR) \
        .filter(gday__lte=GAME_DATE) \
        .extra(where=["substring(gmkey, 9, 2) = '{0}' or substring(gmkey, 11, 2) = '{0}'".format(team_code)])


def get_score_event(event_list):
    result_dict = {}
    for e in event_list:
        if e.score_diff() > 0:
            inn_tb = "%d%s" % (e.inning_num(), e.tb())
            if inn_tb not in result_dict:
                result_dict[inn_tb] = [e]
            else:
                result_dict[inn_tb].append(e)
    return result_dict


def get_diff_days(game_date, last_record_date):
    game_dt = datetime.strptime(game_date, '%Y%m%d')
    record_dt = datetime.strptime(last_record_date, '%Y%m%d')
    dt = game_dt - record_dt

    s_format = "지난 {0}월 {1}일".format(record_dt.month, record_dt.day)

    return s_format, dt.days


def get_hitter_record_sentence(record_list):
    _record_list = remove_duplicated_record_sentence(record_list)
    temp_list = []
    if len(_record_list) > 1:
        for i, s in enumerate(_record_list, 1):
            if i % 2 == 1:
                temp_list.append(s.replace('했다.', '했고,'))
            else:
                temp_list.append(s)
    else:
        temp_list = _record_list

    return ' '.join(temp_list)


def set_used_arguments_for_log(str_string, var_args):
    reg = r"\{(.+?)\}"
    param_list = re.findall(reg, str_string)

    for param in param_list:
        logger.info("[문장]: %s=> %s" % (param, var_args[param]))


def get_person_name(person_code):
    result_name = ''
    query_result = duplicate_name.filter(pcode=person_code)
    if query_result:
        result_name = query_result.name_view

    return result_name


def get_value_clear_attr(var, var_name):
    result = getattr(var, var_name, '')
    if result:
        delattr(var, var_name)
    return result


def save_hitter_top_player_to_db(data_list, game_id):
    object_list = []
    top_players = models.TopPlayerHitter

    # Delete records
    top_players.objects.filter(game_id__exact=game_id).delete()

    # Insert records
    for data in data_list:
        object_list.append(
            top_players(
                game_id=data['game_id'],
                gday=data['game_id'][0:8],
                pcode=data['pcode'],
                tb=data['tb'],
                name=data['name'],
                top_point=data['point']
            ))

    top_players.objects.bulk_create(object_list)


def save_pitcher_top_player_to_db(data_list, game_id):
    object_list = []
    top_players = models.TopPlayerPitcher

    # Delete records
    top_players.objects.filter(game_id__exact=game_id).delete()

    for data in data_list:
        object_list.append(
            top_players(
                game_id=data['game_id'],
                gday=data['game_id'][0:8],
                pcode=data['pcode'],
                tb=data['tb'],
                name=data['name'],
                top_point=data['point']
            ))

    top_players.objects.bulk_create(object_list)


def remove_duplicated_record_sentence(record_kor_list):
    """
    가장 처음에는 선수 이름이 나온다고 가정한다.
    ~은/는 ~ 했다.
    :param record_kor_list:
    :return: list
    """
    if len(record_kor_list) < 2:
        return record_kor_list

    result_list = []
    record_kor_dict = {}
    for record_kor in record_kor_list:
        _kor_list = record_kor.split()
        subject = _kor_list[0][:-1] if _kor_list[0][-1] in ['은', '는'] else _kor_list[0]
        recorder_list = ' '.join(_kor_list[1:])

        if recorder_list in record_kor_dict:
            record_kor_dict[recorder_list].append(subject)
        else:
            record_kor_dict[recorder_list] = [subject]

    if True not in list(map(lambda x: len(x) > 1, list(record_kor_dict.values()))):
        return record_kor_list

    for k, v in record_kor_dict.items():
        v_len = len(v)
        if v_len == 1:
            subjects = get_josa("%s" % v)
        elif v_len == 2:
            subjects = get_josa("%s#과 %s" % (v[0], v[1]))
        else:
            subjects = "{0} {1}".format(
                get_josa("%s#과 %s, " % (v[0], v[1])),
                get_josa(", ".join(v[2:]))
            )
        result_list.append(get_josa("%s#는 %s" % (subjects, k)))

    return result_list


def get_event_out_count(evt):
    if evt.cause_event.ocount == '4':
        result = get_event_out_count(evt.prev)
    else:
        result = evt.cause_event.ocount

    return int(result)


def get_we_li(evt, we_li):
    out_cn = get_event_out_count(evt)
    b1 = evt.cause_event.base1a if evt.cause_event.base1a else ''
    b2 = evt.cause_event.base2a if evt.cause_event.base2a else ''
    b3 = evt.cause_event.base3a if evt.cause_event.base3a else ''
    base_list = [b1, b2, b3]
    base_tf = list(map(lambda x: len(x) > 0, base_list))
    base_str = [str(i + 1) for i, v in enumerate(base_tf) if v]
    runner_sc = int(''.join(base_str)) if base_str else 0
    score_gap = evt.cause_event.bscore - evt.cause_event.tscore
    if score_gap > 15:
        score_gap = 15
    elif score_gap < -15:
        score_gap = -15

    try:
        result = matrix_detail.get(
            inn_no=evt.cause_event.inn,
            tb_sc=evt.cause_event.tb,
            out_cn=out_cn,
            runner_sc=runner_sc,
            score_gap_cn=score_gap
        )
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist('get_we_li')

    result = result.we_rt if we_li == 'we' else result.li_rt

    return result


def get_df_record_matrix(gamecontapp):
    result = []
    before_we_rt = 0.5
    init_li_rt = 0.8591
    max_serno = len(gamecontapp)
    for idx, game in enumerate(gamecontapp):
        curr_hitter = game.hitter
        if (idx + 1) == max_serno:
            pass
        else:
            if gamecontapp[idx + 1].hitter == curr_hitter:
                continue
        _out_cn = 1 if game.place in ['0', '1', '2', '3'] else 0

        curr_game_dict = get_game_status_dict(idx, gamecontapp)
        if curr_game_dict['score_gap_cn'] > 15:
            score_gap = 15
        elif curr_game_dict['score_gap_cn'] < -15:
            score_gap = -15
        else:
            score_gap = curr_game_dict['score_gap_cn']
        try:
            curr_result = matrix_detail.get(
                inn_no=curr_game_dict['inn_no'],
                tb_sc=curr_game_dict['tb_sc'],
                out_cn=curr_game_dict['out_cn'] + _out_cn,
                runner_sc=curr_game_dict['runner_sc'],
                score_gap_cn=score_gap
            )
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist('get_df_record_matrix')

        after_we_rt = round(curr_result.we_rt, 3)
        wpa_rt = before_we_rt - after_we_rt if curr_game_dict['tb_sc'] == 'T' else after_we_rt - before_we_rt
        wpa_rt = round(wpa_rt, 3)
        result.append({
            'gameid': game.gmkey,
            'serno': game.serno,
            'inn': game.inn,
            'tb': game.tb,
            'turn': game.turn,
            'hitter': game.hitter,
            'inn2': game.inn2,
            # 'pitcher': game.pitcher,
            'before_we_rt': before_we_rt,
            'after_we_rt': after_we_rt,
            'wpa_rt': wpa_rt,
            'li_rt': init_li_rt,
        })
        before_we_rt = after_we_rt
        init_li_rt = curr_result.li_rt
    return pd.DataFrame(result)


def get_game_status_dict(idx, gamecontapp):
    game = gamecontapp[idx]
    out_cn = get_record_out_count(idx, gamecontapp)
    b1 = game.base1a if game.base1a else ''
    b2 = game.base2a if game.base2a else ''
    b3 = game.base3a if game.base3a else ''
    base_list = [b1, b2, b3]
    base_tf = list(map(lambda x: len(x) > 0, base_list))
    base_str = [str(i + 1) for i, v in enumerate(base_tf) if v]
    runner_sc = int(''.join(base_str)) if base_str else 0
    score_gap = game.bscore - game.tscore
    _status_dict = dict()
    _status_dict['out_cn'] = out_cn
    _status_dict['runner_sc'] = runner_sc
    _status_dict['score_gap_cn'] = score_gap
    _status_dict['inn_no'] = game.inn
    _status_dict['tb_sc'] = game.tb
    return _status_dict


def get_record_out_count(idx, gamecontapp):
    game = gamecontapp[idx]
    if game.ocount == '4':
        result = get_record_out_count((idx - 1), gamecontapp)
    else:
        result = game.ocount

    return int(result)


def get_pitcher_top_point_4_article(pitcher):
    # pitcher_penalty = 0.6
    # pitcher_records = self.record_matrix_mix.filter(pit_p_id__exact=pitcher.pcode)
    pitcher_records = gamecontapp.filter(pitcher=pitcher.pcode)

    result_point = 0
    for i, record in enumerate(pitcher_records):
        out_cn = 2 if record.ocount == '4' else int(record.ocount)
        b1 = record.base1b if record.base1b else ''
        b2 = record.base2b if record.base2b else ''
        b3 = record.base3b if record.base3b else ''
        base_list = [b1, b2, b3]
        base_tf = list(map(lambda x: len(x) > 0, base_list))
        base_str = [str(i + 1) for i, v in enumerate(base_tf) if v]
        runner_sc = int(''.join(base_str)) if base_str else 0
        score_gap = record.bscore - record.tscore
        if score_gap > 15:
            score_gap = 15
        elif score_gap < -15:
            score_gap = -15
        try:
            li_rt = matrix_detail.get(
                inn_no=record.inn,
                tb_sc=record.tb,
                out_cn=out_cn,
                runner_sc=runner_sc,
                score_gap_cn=score_gap
            ).li_rt
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist('get_pitcher_top_point')
        li = 1.5 if li_rt >= 2 else 1
        result_point += PITCHER_POINT[P_TOP_RANK_POINT_DICT[record.how]] * li

    if pitcher.wls == 'W':
        result_point += 50 if pitcher.start else 20
    if pitcher.start:
        result_point += 30
    if pitcher.sho > 0 and \
            pitcher.wls == 'W' and \
            (pitcher.hit + pitcher.r + pitcher.bb) == 0:
        result_point += 10000
    elif pitcher.sho > 0 and \
            pitcher.wls == 'W' and \
            (pitcher.hit + pitcher.r) == 0:
        result_point += 5000
    elif pitcher.sho:
        result_point += 2000
    elif pitcher.cg:
        result_point += 1600
    elif pitcher.inn2 >= 7 and pitcher.er <= 3:
        result_point += 10
    elif pitcher.inn2 >= 6 and pitcher.er <= 3:
        result_point += 8

    if pitcher.wls == 'L':
        result_point -= 20
    elif pitcher.wls == 'S':
        result_point += 24

    result_point += (pitcher.hold * 16 + pitcher.er * -6 +
                     (pitcher.r - pitcher.er) * -3 + (
                             pitcher.inn2 / 3) * 19.4)

    return result_point
