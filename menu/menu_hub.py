from bot_core.__init__ import *
from bot_core.bot import *
from database import *
import menu.clicker


def init_user(user_id):
    new_clicker = Clicker()
    new_user = User(id=user_id, clicker=new_clicker)
    db.session.add(new_clicker)
    db.session.add(new_user)
    db.session.commit()


@bot_app.route('main')
def main(token):
    user = User.query.filter(User.id == token.user_id).first()
    if not user:
        init_user(token.user_id)
    msg = Message(peer_id=token.user_id, text="Главное меню")
    msg.add_button(label='Главное меню', menu_id='main')
    msg.add_button(label='Второе меню', menu_id='menu2')
    msg.add_button(label='Третье меню', menu_id='menu3')
    msg.add_button(label='Кликер', menu_id='clickAct')
    return msg


@bot_app.route('menu2')
def main(token):
    msg = Message(peer_id=token.user_id, text="Второе меню")
    msg.add_button(label='Главное меню', menu_id='main')
    msg.add_button(label='Второе меню', menu_id='menu2')
    msg.add_button(label='Третье меню', menu_id='menu3')
    return msg


@bot_app.route('menu3')
def main(token):
    msg = Message(peer_id=token.user_id, text="Третье меню")
    msg.add_button(label='Главное меню', menu_id='main')
    msg.add_button(label='Второе меню', menu_id='menu2')
    msg.add_button(label='Третье меню', menu_id='menu3')
    return msg
