from blog.lib import globals as g
import re
import logging.config
from datetime import datetime
# from django.utils import timezone
# import pytz


logging.config.fileConfig(fname='log_config.conf', disable_existing_loggers=False)

logger = logging.getLogger(__name__)

logger.info('This is an info message')
logger.debug('This is a debug %s', {'test': 1, 'dictionary': True, 'test1': 'Good'})


class Logger:
    def __init__(self):
        self.log_list = []

    def adder(self, mode, tab, catg, data):
        log = ''
        if mode == 'RESULT':
            log = data
        elif mode == 'PARAM':
            source_sentence, var = data
            reg = r"\{(.+?)\}"
            param_list = re.findall(reg, source_sentence)
            log = ' | '.join(["{%s}: %s" % (p, g.global_param_dict[p]) for p in param_list if p in g.global_param_dict])
        else:
            log = ', '.join(["%s: %s" % (k, v) for k, v in (sorted(data.items()))])

        log_dict = {
            'TAB': tab,
            'MODE': mode,
            'LOG': '[%s]: %s' % (catg, log),
            'created_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        self.log_list.append(log_dict)
