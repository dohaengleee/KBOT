from .lib import globals as g
from .lib.classes.game import GameVariables
from .lib.sentenct_tempate import Template
from django.utils.timezone import now
from blog.article_models import Articles
from blog import config as cfg
import time


class GameArticles(object):
    def __init__(self, game_id):
        self.game_id = game_id
        self.game_var = None
        self.game_dict = None
        self.template_sentence = None

    def generate_article(self, kinds_of_article=None, hitter_e_article=None, ):
        start = time.time()
        g.initialize(self.game_id)
        if kinds_of_article == 'pitcher':
            g.kinds_of_article = 'pitcher'
            g.hitter_e_article = ''
        elif hitter_e_article == 'hitter_e':
            g.kinds_of_article = ''
            g.hitter_e_article = 'hitter_e'
        else:
            g.kinds_of_article = ''
            g.hitter_e_article = ''

        self.game_var = GameVariables(kinds_of_article, hitter_e_article)
        self.game_dict = self.game_var.get_dict_var()
        template_sentence = Template(self.game_var, kinds_of_article, hitter_e_article)
        result = template_sentence.set_sentence(self.game_id)
        # self.save_article(sentence_list)
        end = time.time()
        print(end-start)
        return result

    def main(self):
        sentence_list = self.template_sentence.set_sentence()
        le_id = 2 if cfg.LEAGUE == 'FUTURES' else 1
        if Articles.objects.all().last():
            serial = Articles.objects.all().last().serial + 1
        else:
            serial = 1
        year = int(self.game_id[0:4])
        status = 'OK'
        title = sentence_list[0]
        if g.kinds_of_article == 'pitcher':
            article_type = 2
        elif g.hitter_e_article == 'hitter_e':
            article_type = 3
        else:
            article_type = 1
        article = '\n'.join([sentence for sentence in sentence_list[1:] if sentence])
        article_model = Articles(
            game_id=self.game_id,
            le_id=le_id,
            serial=serial,
            gyear=year,
            status=status,
            title=title,
            article=article,
            highlight=g.highlight,
            article_type=article_type
        )
        article_model.save()
        return article


if __name__ == "__main__":
    start = time.time()
    gameinfo = g.b_models.Gameinfo.objects.filter(gmkey__startswith=201707).values_list('gmkey', flat=True)
    for game_key in gameinfo:
        game_app = GameArticles(game_key)
        print(game_app.main())
    end = time.time()
    print(end - start)