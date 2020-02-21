from . import globals as g
from blog.article_models import Articles
from blog.article_models import ArticleLog
from blog import config as cfg
import json


class Template(object):
    def __init__(self, game_var, kinds_of_article, hitter_e_article):
        self.base_structure = None
        self.game_var = game_var
        self.kinds_of_article = kinds_of_article
        self.hitter_e_article = hitter_e_article

    def set_sentence(self, game_id):
        try:
            sentence_list = []
            active_tab_list = []
            base_temp = g.MODEL_DICT['base_template']
            if base_temp is None:
                return ''
            for bt in iter(base_temp.objects.values()):
                condition_string = g.get_result_string(g.global_param_dict, bt['condition'], self.game_var, final=True)
                if eval(condition_string):
                    # g.LOGGER.adder('INFO', 'base_template', 'CONDITION', bt)
                    if bt['template_tab'] not in active_tab_list:
                        active_tab_list.append(bt['template_tab'])
                        g.set_variable(self.game_var, bt['template_tab'])
                    print(bt['template_tab'])
                    g.set_used_arguments_for_log(bt['sentence'], self.game_var.__dict__)
                    paragraph = bt['sentence'].format(**self.game_var.__dict__)
                    # TODO index가 변경될 시 시트(DB)에서 확인 필요
                    if bt['index'] == 5 or bt['index'] == 12 and paragraph:
                        #  우수투수 or 타자의 추가적인 기록이 없는 경우(문장의 길이로 판단하였음) 합침
                        if len(paragraph) <= 65:
                            if len(sentence_list[-1]) <= 65:
                                paragraph = " ".join(paragraph.split(' ')[1:])
                                sentence_list[-1] = sentence_list[-1].replace('다.', '고, ') + paragraph
                    else:
                        sentences = paragraph.split('\n\n')
                        sentence_list.extend(sentences)

            if self.hitter_e_article == 'hitter_e':
                if self.game_var.is_rare_record().존재:
                    sentence_list[-1] += "[%s=KBOT]" % self.game_var.__dict__['구장이름']
                else:
                    pass
            else:
                sentence_list[-1] += "[%s=KBOT]" % self.game_var.__dict__['구장이름']
            self.save_article(sentence_list, game_id)
        except Exception as e:
            sentence_list = []
            sentences = 'error! msg : ' + str(e) + ' \nplease generate pitcher article instead'
            sentence_list.append(sentences)
            '\n\n'.join(sentence_list)
            print(e)
            self.save_article(sentence_list, game_id)
        # self.save_log(game_id, article_serial)

        return True

    def save_article(self, sentence_list, game_id):
        le_id = 2 if cfg.LEAGUE == 'FUTURES' else 1
        article_type = 1
        if self.kinds_of_article == 'pitcher':
            article_type = 2
        elif self.hitter_e_article == 'hitter_e':
            article_type = 3
        queryset = Articles.objects
        if queryset.all().exists():
            serial = queryset.latest('serial').serial + 1
        else:
            serial = 1
        year = int(game_id[0:4])
        status = 'OK'
        title = sentence_list[0]
        article = '\n'.join([sentence for sentence in sentence_list[1:] if sentence])
        article_model = Articles(
            game_id=game_id,
            le_id=le_id,
            serial=serial,
            gyear=year,
            status=status,
            title=title,
            article=article,
            highlight=g.highlight,
            article_type=article_type
        )
        article_model.save(force_insert=True)
        return serial

    @staticmethod
    def save_log(game_id, serial):
        object_list = []
        le_id = 2 if cfg.LEAGUE == 'FUTURES' else 1
        status = 'OK'
        for i, log in enumerate(g.LOGGER.log_list):
            object_list.append(
                ArticleLog(
                    game_id=game_id,
                    counter=i+1,
                    le_id=le_id,
                    serial=serial,
                    status=status,
                    tab=log['TAB'],
                    mode=log['MODE'],
                    logs=log['LOG'],
                    created_at=log['created_time'],
                )
            )
        ArticleLog.objects.bulk_create(object_list)
        return True
