from blog.lib import globals as g
import random


class HalfInning(object):
    def __init__(self):
        self.TABLE_NAME = 'half_inning_dynamic_variable'

    def get_half_inning_text(self, sentence_type, e1=None, e2=None):
        setattr(self, '상황1', e1)
        setattr(self, '상황2', e2)
        setattr(self, 'sentence_types', sentence_type)
        result = g.get_by_name(self, '_하프이닝_중간문장', self.TABLE_NAME)
        return result

    # def get_player_record_text(self, sentence_type, e1=None, e2=None):
    #     setattr(self, '상황1', e1)
    #     setattr(self, '상황2', e2)
    #     setattr(self, 'sentence_types', sentence_type)
    #     result = g.get_by_name(self, '_개인기록', self.TABLE_NAME)
    #     return result

    def get_player_record_text_v2(self, sentence_type, event_list, used_dict):
        result = []
        setattr(self, 'sentence_types', sentence_type)
        for e in event_list:
            _data = g.get_by_name(e, '하프이닝_개인기록', 'hitterrecord_dynamic_variable', used_dict)
            if _data:
                result.append(_data)
        return result

    def get_split_player_list(self, event_list, total_scene):
        setattr(self, 'sentence_types', '')
        prev_hitter_name = ''
        prev_how_code = ''
        prev_scene = ''
        half_list = []
        pitcher_err_list = []
        team_score = total_scene.team_score_before
        vs_team_score = total_scene.vs_team_score_before
        final_bat_how = ''
        final_bat_player = ''
        for idx, e in enumerate(event_list):
            # {_상황}
            how_cd = e.how
            if how_cd == 'BH':
                continue
            out_count_kor = e.start_out_count_to_kor()
            pa_kor = e.base_before_str()
            score = e.score_diff()
            team_score += score
            # if score == 1:
            #     score = ''
            if pa_kor == '주자 없는':
                pa_kor = "%s 상황" % pa_kor

            scene = "{0}사 {1}".format(out_count_kor, pa_kor)
            hitter_name = e.hitter().name()
            player_name = hitter_name
            rturn = e.cause_event.rturn
            turn = e.cause_event.turn
            field = e.cause_event.field
            # 20190822 1회인 경우 prev event 유무 확인
            if e.prev.cause_event:
                prev_turn = e.prev.cause_event.turn
            else:
                prev_turn = None
            tb = e.cause_event.tb
            bcount = e.cause_event.bcount
            bcnt = e.cause_event.bcnt
            splited_how = e.how_name().split()
            splited_how[-1] = "끝내기 " + splited_how[-1]
            end_how = " ".join(splited_how)
            how_name = end_how if total_scene.끝내기 and tb == 'B' and e.cause_event.inn == 9 and e.next is None else e.how_name()
            last_bcnt = e.cause_event.bcount[-1] if len(e.cause_event.bcount) > 0 else ''
            pitcher_name = e.cause_event.pitname
            pitcher_team_kor = g.team_kor_dict[g.GAME_ID[8:10]] if tb == 'B' else g.team_kor_dict[g.GAME_ID[10:12]]

            if total_scene.final_bat and final_bat_how == '' and final_bat_player == '':
                if team_score > vs_team_score:
                    final_bat_player = hitter_name
                    final_bat_how = how_name

            # if how_cd == 'ER':
            #     player_name = g.entry_obj.filter(turn=rturn, team=tb)[0].name

            if how_cd == 'SD':
                if len(e.how_list) > 1:
                    prev_rturn = e.cause_event.rturn
                    last_rturn = e.last_event.rturn
                    hitter_name1 = g.entry_obj.filter(turn=last_rturn, team=tb)[0].name
                    hitter_name2 = g.entry_obj.filter(turn=prev_rturn, team=tb)[0].name
                    _players = g.get_josa("{0}#과 ".format(hitter_name1)) + hitter_name2
                else:
                    hitter_name1 = g.entry_obj.filter(turn=rturn, team=tb)[0].name
                    _players = hitter_name1
                player_name = _players
            elif how_cd in g.PITCHER_ERR:
                # if pitcher_name not in pitcher_err_list:
                #     pitcher_err_list.append(pitcher_name)
                #     pitcher_team_kor = g.team_kor_dict[g.GAME_ID[8:10]] if tb == 'B' else g.team_kor_dict[g.GAME_ID[10:12]]
                #     pitcher_team_name = "%s %s" % (pitcher_team_kor, pitcher_name)
                # else:
                #     pitcher_team_name = "상대"
                # player_name = g.entry_obj.filter(turn=rturn, team=tb)[0].name
                # player_name = g.get_josa("%s#이 %s" % (runner_name, pitcher_team_name))
                if how_cd not in ['BK', 'B2']:
                    how_name = "%s" % how_name

            # todo 190404 아래 부분 조건을 더 넣어서 만들어 줘야 할 듯.
            if idx == 0:
                _scene_dict = dict()
                _scene_dict['scene'] = scene
                _scene_dict['score'] = score
                _scene_dict['outcount'] = out_count_kor
                _scene_dict['vs_team_kor'] = pitcher_team_kor
                _scene_dict['last_bcnt'] = last_bcnt
                _scene_dict['er_place_list'] = e.er_place_list
                _scene_dict['turn'] = turn
                _scene_dict['field'] = field
                _scene_dict['prev_turn'] = prev_turn
                _scene_dict['bcnt'] = bcnt
                _scene_dict['final_bat'] = [
                    {
                        'player': final_bat_player,
                        'how_name': final_bat_how
                    }
                ]
                _scene_dict['how'] = [
                    {
                        'how_code': how_cd,
                        'how_name': how_name,
                        'players': [player_name],
                        'pitcher': pitcher_name,
                        'how_list': e.how_list
                    }
                ]
                half_list.append(_scene_dict)
            # 연속 상황일 경우
            elif prev_hitter_name == e.prev.hitter_name():
                if prev_how_code == how_cd:
                    if prev_scene == scene:
                        # 상황과 HOW 가 같을 경우
                        half_list[-1]['score'] += 1 if score == '' else score
                        half_list[-1]['how'][-1]['players'].append(player_name)
                        half_list[-1]['final_bat'][-1]['player'] = final_bat_player
                        half_list[-1]['final_bat'][-1]['how_name'] = final_bat_how
                    else:
                        # 상황이 다를 경우
                        _scene_dict = dict()
                        _scene_dict['scene'] = scene
                        _scene_dict['score'] = score
                        _scene_dict['outcount'] = out_count_kor
                        _scene_dict['pitcher'] = pitcher_name
                        _scene_dict['vs_team_kor'] = pitcher_team_kor
                        _scene_dict['last_bcnt'] = last_bcnt
                        _scene_dict['field'] = field
                        _scene_dict['er_place_list'] = e.er_place_list
                        _scene_dict['turn'] = turn
                        _scene_dict['prev_turn'] = prev_turn
                        _scene_dict['bcnt'] = bcnt
                        _scene_dict['final_bat'] = [
                            {
                                'player': final_bat_player,
                                'how_name': final_bat_how
                            }
                        ]
                        _scene_dict['how'] = [
                            {
                                'how_code': how_cd,
                                'how_name': how_name,
                                'players': [player_name],
                                'pitcher': pitcher_name,
                                'how_list': e.how_list
                            }
                        ]
                        half_list.append(_scene_dict)
                else:
                    # 상황이 다를 경우
                    _scene_dict = dict()
                    _scene_dict['scene'] = scene
                    _scene_dict['score'] = score
                    _scene_dict['outcount'] = out_count_kor
                    _scene_dict['pitcher'] = pitcher_name
                    _scene_dict['vs_team_kor'] = pitcher_team_kor
                    _scene_dict['last_bcnt'] = last_bcnt
                    _scene_dict['field'] = field
                    _scene_dict['er_place_list'] = e.er_place_list
                    _scene_dict['turn'] = turn
                    _scene_dict['prev_turn'] = prev_turn
                    _scene_dict['bcnt'] = bcnt
                    _scene_dict['final_bat'] = [
                        {
                            'player': final_bat_player,
                            'how_name': final_bat_how
                        }
                    ]
                    _scene_dict['how'] = [
                        {
                            'how_code': how_cd,
                            'how_name': how_name,
                            'players': [player_name],
                            'pitcher': pitcher_name,
                            'how_list': e.how_list
                        }
                    ]
                    half_list.append(_scene_dict)
            else:
                # 상황이 다를 경우
                _scene_dict = dict()
                _scene_dict['scene'] = scene
                _scene_dict['score'] = score
                _scene_dict['outcount'] = out_count_kor
                _scene_dict['pitcher'] = pitcher_name
                _scene_dict['vs_team_kor'] = pitcher_team_kor
                _scene_dict['last_bcnt'] = last_bcnt
                _scene_dict['field'] = field
                _scene_dict['er_place_list'] = e.er_place_list
                _scene_dict['turn'] = turn
                _scene_dict['prev_turn'] = prev_turn
                _scene_dict['bcnt'] = bcnt
                _scene_dict['final_bat'] = [
                    {
                        'player': final_bat_player,
                        'how_name': final_bat_how
                    }
                ]
                _scene_dict['how'] = [
                    {
                        'how_code': how_cd,
                        'how_name': how_name,
                        'players': [player_name],
                        'pitcher': pitcher_name,
                        'how_list': e.how_list
                    }
                ]
                half_list.append(_scene_dict)
            prev_hitter_name = hitter_name
            prev_how_code = how_cd
            prev_scene = scene
        return half_list

    def get_half_inning_player_structure(self, scene, used_dict):
        event_list = scene.events
        half_list = self.get_split_player_list(event_list, scene)
        half_text_list = []
        half_string_list = []
        last_how = ''
        before_scene = ''
        before_turn = ''
        for half_idx, half in enumerate(half_list):
            # 무사 만루 상황에서
            setattr(self, 'list_length', len(half_list))
            setattr(self, 'index', half_idx)
            how_list = []

            setattr(self, '상황', half['scene'])
            if half['scene'] == before_scene and before_turn == half['prev_turn']:
                scene_kor = ''
            else:
                if half_idx % 3 == 0:
                    _scene_kor = '에서 '
                elif half_idx % 3 == 1:
                    _scene_kor = '에서는 '
                else:
                    _scene_kor = ' '

                _half_scene = '선두타자 ' if half['scene'] == '무사 주자 없는 상황' else half['scene']
                if _half_scene == '선두타자 ':
                    scene_kor = _half_scene
                else:
                    scene_kor = _half_scene + _scene_kor

            before_scene = half['scene']
            before_turn = half['turn']

            for how in half['how']:
                is_defender = True
                last_how = how['how_code']
                try:
                    defender = half['field'][half['field'].index('E')-1]
                except:
                    is_defender = False
                if len(how['players']) == 1:
                    player_kor = how['players'][0]
                    if how['how_code'] == 'ER':
                        if half['last_bcnt'] in ['X', 'Y', 'Z']:
                            if is_defender:
                                if int(defender) == 1:
                                    if _scene_kor == ' ':
                                        _how_kor = g.get_josa("%s 타석에서 상대 투수의 견제 실책" % player_kor)
                                    else:
                                        _how_kor = g.get_josa("%s 타석 때 상대 투수의 견제 실책" % player_kor)
                                else:
                                    if _scene_kor == ' ':
                                        _how_kor = g.get_josa("%s 타석에서 상대 실책" % player_kor)
                                    else:
                                        _how_kor = g.get_josa("%s 타석 때 상대 실책" % player_kor)
                            else:
                                if _scene_kor == ' ':
                                    _how_kor = g.get_josa("%s 타석에서 상대 실책" % player_kor)
                                else:
                                    _how_kor = g.get_josa("%s 타석 때 상대 실책" % player_kor)
                        else:
                            if _scene_kor == ' ':
                                _how_kor = g.get_josa("%s 타석에서 상대 실책" % player_kor)
                            else:
                                _how_kor = g.get_josa("%s 타석 때 상대 실책" % player_kor)

                    elif half['last_bcnt'] in ['X', 'Y', 'Z']:
                        if _scene_kor == ' ':
                            _how_kor = g.get_josa("%s 타석에서 %s에 이은 상대 투수의 견제 실책" % (player_kor, how['how_name']))
                        else:
                            _how_kor = g.get_josa("%s 타석 때 %s에 이은 상대 투수의 견제 실책" % (player_kor, how['how_name']))

                    elif 'ER' in how['how_list'] and list(filter(lambda x: x in ['E', 'R', 'H', 'F', 'S', 'I'], half['er_place_list'])):
                        if '상대' in how['how_name']:
                            _how_kor = g.get_josa("%s의 %s" % (player_kor, how['how_name']))
                        else:
                            _how_kor = g.get_josa("%s의 %s 타구 때 상대 실책" % (player_kor, how['how_name']))
                    elif how['how_code'] in g.PITCHER_ERR:
                        if _scene_kor == ' ':
                            player_kor = g.get_josa("%s 타석에서" % player_kor)
                            _how_kor = "{0} {1}".format(player_kor, how['how_name'])
                        else:
                            if how['how_code'] == 'HP':
                                _how_kor = "{}의 {}".format(player_kor, how['how_name'])
                            else:
                                player_kor = g.get_josa("%s 타석 때" % player_kor)
                                _how_kor = "{0} {1}".format(player_kor, how['how_name'])
                    # daehyuk 20190812 - 20190811KTOB0 - '선택수비' 이전 상황 확인 및 적용
                    elif last_how == 'RF' and len(how['how_list']) > 1 and how['how_list'][-1] != 'RF':
                        _how_kor = "{0} 타석 때 {1}에 이은 선택수비".format(player_kor, g.HOW_KOR_DICT[how['how_list'][-1]])

                    # daehyuk 20190812 - 20190811KTOB0 - '폭투'로 인한 '밀어내기 볼넷'의 경우 폭투로 인한 득점 적용
                    elif len(how['how_list']) == 2 and 'BB' in how['how_list'] and 'WP' in how['how_list']:
                        _how_kor = "{0} 타석 때 상대 투수의 폭투".format(player_kor)

                    # dohaeng 20190902 - 20190828SMKT0 = 'OO의 초구 홈런' 추가
                    elif how['how_code'] == 'HR' and half['bcnt'] == '0-0':
                        _how_kor = "{}의 초구 {}".format(player_kor, how['how_name'])

                    else:
                        _how_kor = "{}의 {}".format(player_kor, how['how_name'])
                else:
                    _player = g.get_josa("{0}#과 ".format(how['players'][0]))
                    player_kor = _player + ', '.join(how['players'][1:])
                    if how['how_code'] == 'ER':
                        _how_kor = g.get_josa("%s#이 상대 연속 실책" % player_kor)
                    elif how['how_code'] in g.PITCHER_ERR:
                        if how['how_code'] == 'WP':
                            runner = g.get_josa("%s" % player_kor)
                            _how_kor = "{0} 타석 때 상대 투수의 {1}".format(runner, how['how_name'])
                        else:
                            runner = g.get_josa("%s#이" % player_kor)
                            _how_kor = "{0} 상대 연속 {1}".format(runner, how['how_name'])
                    else:
                        if how['how_name'] == '홈런':
                            _how_kor = "{}의 연속타자 {}".format(player_kor, how['how_name'])
                        else:
                            _how_kor = "{}의 연속 {}".format(player_kor, how['how_name'])
                how_list.append(_how_kor)

            if len(how_list) > 1:
                _how_list = g.get_josa("{0}#과 ".format(how_list[0]))
                how_string = _how_list + ', '.join(how_list[1:])
            else:
                how_string = how_list[0]

            _scene = scene_kor + how_string
            half_string_list.append({
                '문장': _scene,
                '아웃': half['outcount'],
                '연속': True if len(half['how']) > 1 else False,
                # ''득점': '' if half['score'] == 1 else half['score'],
                # daehyuk 20190731 - 20190730WOOB0 - 백민규의 안타, 백동훈의 3루타로 2득점했다. > 백민규의 안타로 1득점, 백동훈의 3루타로 2득점했다.
                '득점': half['score'],
                'HOW': last_how,
                '하우': g.HOW_KOR_DICT[last_how],
                '타자이름': player_kor,
                '타자리스트': half['how'][0]['players'],
                '상황': half['scene'],
                '상황_조사': _scene_kor,
                '이전점수': scene.team_score_before,
                '현재점수': scene.team_score_after,
                'tscore': scene.t_score,
                'bscore': scene.b_score,
                '상대_이전점수': scene.vs_team_score_before,
                '상대_현재점수': scene.vs_team_score_after,
                '초말': scene.tb,
                '마지막득점': scene.last_score,
                '결승득점': scene.final_score,
                '역전': scene.reversal,
                '결승타': scene.final_bat,
                '결승타하우': half['final_bat'][0]['how_name'],
                '결승타플레이어': half['final_bat'][0]['player'],
                '선취점': scene.first_score,
                '이닝': scene.inn
            })

            setattr(self, '상황문장', _scene)
            setattr(self, '득점', half['score'])
            half_text = g.get_by_name(self, '_하프이닝_중간문장', self.TABLE_NAME, used_dict)
            half_text_list.append(half_text)

        _half_string_list = self.get_string_connection(half_string_list)
        return ''.join(_half_string_list)

    @staticmethod
    def get_string_connection(info_list):
        # 코드 주석은 기존 버전
        # 점수 언급 수정 필요 / 문장 연결이 아닌 문장 생성부분에서
        result_list = []
        info_length = len(info_list) - 1
        # prev_out_count = ''
        prev_scene = ''
        prev_consecutive_kor = ''
        used = False
        first_score_used = False
        ran_choice = float(random.random())
        t_score = 0
        b_score = 0
        t_score_for_final = 0
        b_score_for_final = 0
        temp = 0
        for idx, info in enumerate(info_list):
            idx = idx - temp
            out = info['아웃']
            scene = info['상황']
            reversal = False
            final_bat = False
            # consecutive = info['연속']
            if info['선취점'] and not first_score_used and len(info['타자리스트']) != 1:
                first_score_used = True

            #  역전 시점을 잡기 위해서
            if info['역전']:
                if info['초말'] == 'T':
                    if info['이전점수'] > t_score:
                        t_score = info['이전점수']
                    if info['이전점수'] - info['상대_이전점수'] <= 0:
                        if t_score - info['상대_이전점수'] <= 0:
                            if info['득점'] == '':
                                t_score += 1
                            else:
                                t_score += info['득점']

                            if t_score > info['상대_이전점수']:
                                reversal = True
                            else:
                                pass
                else:
                    if info['이전점수'] > b_score:
                        b_score = info['이전점수']
                    if info['이전점수'] - info['상대_이전점수'] <= 0:
                        if b_score - info['상대_이전점수'] <= 0:
                            if info['득점'] == '':
                                b_score += 1
                            else:
                                b_score += info['득점']
                            if b_score > info['상대_이전점수']:
                                reversal = True
                            else:
                                pass

            consecutive_kor = '#로 ' if info['HOW'] != "GD" else ' 때 '
            if reversal:
                if g.reversal_inn.index([info['이닝'], info['초말'].lower()]) >= 1:
                    reversal_text = '재역전'
                else:
                    reversal_text = '역전'

            if idx+temp == info_length:
                # 마지막 문장
                # out_kor = '이후 ' if prev_out_count != out and idx > 0 else ''
                scene_kor = '이후 ' if prev_consecutive_kor[-3:] == '다. ' and not used else ''

                if reversal:
                    if info['마지막득점']:
                        if info['이닝'] == 9 and info['초말'] == 'B':
                            if info['득점'] != '':
                                consecutive_kor += '%s득점하며 %s-%s#로 %s승을 거뒀다. ' % (info['득점'], info['tscore'], info['bscore'], reversal_text)
                            else:
                                consecutive_kor += '%s-%s#로 %s승을 거뒀다. ' % (info['tscore'], info['bscore'], reversal_text)
                        else:
                            if info['득점'] != '':
                                if info['결승득점']:
                                    consecutive_kor += '%s득점하여 %s-%s#로 %s에 성공했고, 이 점수는 팀의 결승 득점이 됐다. ' % (info['득점'], info['tscore'], info['bscore'], reversal_text)
                                else:
                                    consecutive_kor += '%s득점하여 %s-%s#로 %s에 성공했고, 이 점수는 팀의 마지막 득점이 됐다. ' % (info['득점'], info['tscore'], info['bscore'], reversal_text)
                            else:
                                consecutive_kor += ' %s-%s#로 %s에 성공했고, 이 점수는 팀의 마지막 득점이 됐다. ' % (info['tscore'], info['bscore'], reversal_text)
                    elif info['HOW'] == 'HR':
                        if reversal_text == '재역전':
                            consecutive_kor += '%s-%s#로 경기를 다시 뒤집는 데 성공했다. ' % (info['tscore'], info['bscore'])
                        else:
                            consecutive_kor += '%s-%s#로 경기를 뒤집는 데 성공했다. ' % (info['tscore'], info['bscore'])
                    elif info['득점'] != '':
                        consecutive_kor += '%s득점하여 %s-%s#로 %s에 성공했다. ' % (info['득점'], info['tscore'], info['bscore'], reversal_text)
                    else:
                        consecutive_kor += ' %s-%s#로 %s에 성공했다. ' % (info['tscore'], info['bscore'], reversal_text)
                elif info['선취점'] and not first_score_used and len(info['타자리스트']) == 1:
                    if info['HOW'] != 'HR' and info['득점'] != '':
                        if info['득점'] > 1:
                            consecutive_kor += ' 선취점(%s점)을 기록했다. ' % (info['득점'])
                        else:
                            consecutive_kor += ' 선취점을 기록했다. '
                    elif info['마지막득점']:
                        consecutive_kor += ' 선취점을 기록했고, '
                    else:
                        consecutive_kor += ' 선취점을 기록했다. '
                    first_score_used = True
                else:
                    if info['HOW'] == 'HR':
                        pass
                    elif info['득점'] != '':
                        consecutive_kor += '%s득점하며 ' % (info['득점'])
                    elif idx == 0:
                        pass
                    elif idx == info_length:
                        # consecutive_kor = consecutive_kor[:-3]+', '
                        pass

            elif idx % 2 == 1:
                # 중간 마무리 문장
                if prev_consecutive_kor[-3:] == '다. ' and not used:
                    scene_kor = '이후 '
                    used = True
                else:
                    scene_kor = ''

                if reversal:
                    if info['HOW'] == 'HR':
                        consecutive_kor += '%s에 성공했다. ' % reversal_text
                    elif info['득점'] != '':
                        consecutive_kor += '%s득점하며 %s에 성공했다. ' % (info['득점'], reversal_text)
                    else:
                        consecutive_kor += ' %s에 성공했다. ' % (reversal_text)
                else:
                    if info['HOW'] == 'HR':
                        if ran_choice <= 0.33:
                            consecutive_kor += '득점했다. '
                        else:
                            consecutive_kor += '점수를 더했다. '
                    elif info['득점'] != '':
                        consecutive_kor += '%s득점했다. ' % (info['득점'])
                    elif info_list[idx+1]['아웃'] != out:
                        consecutive_kor += '%s득점했다. ' % (info['득점'])
                    elif info_list[idx+1]['아웃'] == out:
                        if ran_choice <= 0.33:
                            if info['이전점수'] == 0:
                                consecutive_kor += '1점을 올렸다. '
                            else:
                                consecutive_kor += '1점을 더했다. '
                        else:
                            if info['이전점수'] == 0:
                                consecutive_kor += '점수를 올렸다. '
                            else:
                                consecutive_kor += '점수를 더했다. '
                if used:
                    consecutive_kor = consecutive_kor[:-3]+'고, '
            else:
                # 이어지는 문장
                if prev_consecutive_kor[-3:] == '다. ' and not used:
                    scene_kor = '이후 '
                    used = True
                else:
                    scene_kor = ''

                if reversal:
                    if info['HOW'] == 'HR':
                        consecutive_kor += '%s에 성공했고, ' % (reversal_text)
                    elif info['득점'] != '':
                        consecutive_kor += '%s득점하며 %s에 성공했고, ' % (info['득점'], reversal_text)
                    else:
                        consecutive_kor += ' %s에 성공했고, ' % (reversal_text)
                elif info['선취점'] and not first_score_used and len(info['타자리스트']) == 1:
                    if info['HOW'] != 'HR' and info['득점'] != '':
                        if info['득점'] > 1:
                            consecutive_kor += ' 선취점(%s점)을 기록했고, ' % (info['득점'])
                        else:
                            consecutive_kor += ' 선취점을 기록했고, '
                    else:
                        consecutive_kor += ' 선취점을 기록했고, '
                    first_score_used = True
                else:
                    if info['HOW'] == 'HR':
                        consecutive_kor = consecutive_kor[:-3]+', '
                    elif info_list[idx+1]['아웃'] != out:
                        if info['득점'] != '':
                            consecutive_kor += '%s점을 더했고, ' % (info['득점'])
                        # 당분간 삭제
                        # elif ran_choice <= 0.33:
                        #     if info['이전점수'] == 0:
                        #         consecutive_kor += '점수를 올렸고, '
                        #     else:
                        #         consecutive_kor += '점수를 더했고, '
                        # elif ran_choice <= 0.66:
                        #     if info['이전점수'] == 0:
                        #         consecutive_kor += '1점을 올렸고, '
                        #     else:
                        #         consecutive_kor += '1점을 더했고, '
                        else:
                            consecutive_kor = consecutive_kor[:-3]+', '
                    else:
                        if info['득점'] != '':
                            consecutive_kor += '%s득점, ' % (info['득점'])
                        elif info['HOW'] == 'SD':
                            consecutive_kor += '1득점, '
                        else:
                            consecutive_kor = consecutive_kor[:-3]+', '

            #  결승타 시점을 잡기 위해서
            if info['결승타']:
                if info['초말'] == 'T':
                    if info['이전점수'] > t_score_for_final:
                        t_score_for_final = info['이전점수']
                    if info['이전점수'] - info['상대_이전점수'] <= 0:
                        if t_score_for_final - info['상대_이전점수'] <= 0:
                            if info['득점'] == '':
                                t_score_for_final += 1
                            else:
                                t_score_for_final += info['득점']

                            if t_score_for_final > info['상대_이전점수']:
                                final_bat = True
                            else:
                                pass
                else:
                    if info['이전점수'] > b_score_for_final:
                        b_score_for_final = info['이전점수']
                    if info['이전점수'] - info['상대_이전점수'] <= 0:
                        if b_score_for_final - info['상대_이전점수'] <= 0:
                            if info['득점'] == '':
                                b_score_for_final += 1
                            else:
                                b_score_for_final += info['득점']
                            if b_score_for_final > info['상대_이전점수']:
                                final_bat = True
                            else:
                                pass

                #  사용되지 않는 if문도 있으리라 생각합니다.
                if final_bat:
                    if info['이닝'] == 9 and info['초말'] == 'B' and not reversal:
                        consecutive_kor = consecutive_kor + """{t}-{b}#로 승리했다. """.format(t=info['상대_이전점수'], b=b_score_for_final, hitname=info['타자이름'])
                    elif info['이닝'] == 9 and info['초말'] == 'B' and reversal:
                        pass
                    elif info['마지막득점']:
                        final_bat_sentence = """{hitname}의 {how}#는 오늘 경기의 결승타로 기록됐다. """.format(hitname=info['결승타플레이어'], how=info['결승타하우'])
                        if '이 점수는 팀의 마지막 득점이 됐다.' in consecutive_kor:
                            consecutive_kor = consecutive_kor.replace('이 점수는 팀의 마지막 득점이 됐다. ', final_bat_sentence)
                        elif consecutive_kor == '#로 ' or consecutive_kor[-2:] == '며 ':
                            if info['초말'] == 'T':
                                if info['상대_이전점수'] > b_score_for_final:
                                    consecutive_kor += """앞서나갔고, 이 {how}#는 오늘 경기의 결승타로 기록됐다. """.format(how=info['하우'])
                                else:
                                    consecutive_kor += """{t}-{b}를 만들었고, 이 {how}#이 오늘 경기의 결승타로 기록됐다. """.format(t=t_score_for_final, b=info['상대_이전점수'], hitname=info['타자이름'], how=info['하우'])
                            else:
                                if info['상대_이전점수'] < b_score_for_final:
                                    consecutive_kor += """앞서나갔고, 이 {how}#는 오늘 경기의 결승타로 기록됐다. """.format(how=info['하우'])
                                else:
                                    consecutive_kor += """{t}-{b}를 만들었고, 이 {how}#이 오늘 경기의 결승타로 기록됐다. """.format(t=info['상대_이전점수'], b=b_score_for_final, hitname=info['타자이름'], how=info['하우'])
                        else:
                            consecutive_kor += final_bat_sentence
                    elif consecutive_kor[-3:] == '고, ':
                        consecutive_kor += """{hitname}의 {how}#는 오늘 경기의 결승타로 기록됐다. """.format(hitname=info['결승타플레이어'], how=info['결승타하우'])
                    elif consecutive_kor[-2:] == ', ':
                        if info['초말'] == 'T':
                            if len(info['타자이름'].split(' ')) > 1:
                                consecutive_kor = consecutive_kor[
                                                  :-3] + """#로 {t}-{b}를 만들었고, {hitname}의 {how}#은 오늘 경기의 결승타로 기록됐다. """.format(
                                    t=t_score_for_final, b=info['상대_이전점수'], hitname=info['타자이름'].split(' ')[0][:-1], how=info['하우'])
                            else:
                                if '득점,' in consecutive_kor:
                                    consecutive_kor = """#로 {t}-{b}를 만들었고, 이 {how}#이 오늘 경기의 결승타로 기록됐다. """.format(t=t_score_for_final, b=info['상대_이전점수'], hitname=info['타자이름'], how=info['하우'])
                                else:
                                    consecutive_kor = consecutive_kor[:-3]+"""#로 {t}-{b}를 만들었고, 이 {how}#이 오늘 경기의 결승타로 기록됐다. """.format(t=t_score_for_final, b=info['상대_이전점수'], hitname=info['타자이름'], how=info['하우'])
                        else:
                            if len(info['타자이름'].split(' ')) > 1:
                                consecutive_kor = consecutive_kor[
                                                  :-3] + """#로 {t}-{b}를 만들었고, {hitname}의 {how}#은 오늘 경기의 결승타로 기록됐다. """.format(
                                    t=info['상대_이전점수'], b=b_score_for_final, hitname=info['타자이름'].split(' ')[0][:-1], how=info['하우'])
                            else:
                                consecutive_kor = consecutive_kor[:-3]+"""#로 {t}-{b}를 만들었고, 이 {how}#이 오늘 경기의 결승타로 기록됐다. """.format(t=info['상대_이전점수'], b=b_score_for_final, hitname=info['타자이름'], how=info['하우'])
                    elif consecutive_kor[-2:] == '며 ' or consecutive_kor[-2:] == '로 ':
                        if info['초말'] == 'T':
                            consecutive_kor += """{t}-{b}를 만들었고, 이 {how}#이 오늘 경기의 결승타로 기록됐다. """.format(t=t_score_for_final, b=info['상대_이전점수'], hitname=info['타자이름'], how=info['하우'])
                        else:
                            consecutive_kor += """{t}-{b}를 만들었고, 이 {how}#이 오늘 경기의 결승타로 기록됐다. """.format(t=info['상대_이전점수'], b=b_score_for_final, hitname=info['타자이름'], how=info['하우'])
                    else:
                        consecutive_kor = consecutive_kor[:-3]+'고, '+"""{hitname}의 {how}#는 오늘 경기의 결승타로 기록됐다. """.format(hitname=info['결승타플레이어'], how=info['결승타하우'])
                    info['결승타'] = False
                    temp += 1
                else:
                    pass
            else:
                pass

            # prev_out_count = out
            prev_scene = scene
            prev_consecutive_kor = consecutive_kor
            # result_list.append(
            #     g.get_josa("{0}{1}{2}".format(out_kor, info['문장'], consecutive_kor, )),
            # )
            result_list.append(
                g.get_josa("{0}{1}{2}".format(scene_kor, info['문장'], consecutive_kor, )),
            )
        return result_list
