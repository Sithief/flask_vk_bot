from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import configparser
import os
import sys
import logging
from logging.handlers import RotatingFileHandler
import traceback
from bot_core.bot import *
from bot_core import vk_api

base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
log_path = os.path.join(base_path, 'log')
conf_path = os.path.join(base_path, 'config.cfg')
db_path = os.path.join(base_path, 'data.db')
CONF = dict()


def init_logging():
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    handler = RotatingFileHandler(os.path.join(log_path, 'my_log.log'),
                                  maxBytes=100000,
                                  backupCount=10)
    logging.basicConfig(
        handlers=[handler],
        format='%(filename)-25s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
        level=logging.DEBUG,
        datefmt='%m-%d %H:%M',
    )
    return log_path


def logging_excepthook(exctype, value, tb):
    import logging
    import time
    init_logging()
    logging.critical(f'EXCEPTION: Type: {exctype}, Value: {value}')
    with open(os.path.join(log_path, 'bot_errors.log'), 'w') as error_file:
        error_file.write(time.asctime() + '\n')
        traceback.print_exception(exctype, value, tb, file=error_file)


def read_config():
    global CONF
    is_prod = os.environ.get('ENVIRON', None)
    if is_prod:
        CONF = {'VK_token': os.environ.get('VK_TOKEN', None),
                'VK_confirm': os.environ.get('VK_CONFIRM', None)}
    else:
        conf = configparser.ConfigParser()
        conf.read(conf_path, encoding='utf-8')
        CONF = {'VK_token': conf.get('VK', 'token'),
                'VK_confirm': conf.get('VK', 'confirm')}


read_config()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

bot_api = vk_api.Api(CONF.get('VK_token'), 'main')
bot_app = Bot()

init_logging()
sys.excepthook = logging_excepthook
