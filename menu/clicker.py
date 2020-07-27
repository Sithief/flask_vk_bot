from bot_core.__init__ import *
from bot_core.bot import *
from database import *

symbols = {'hearts': '❤', 'magic': '✨', 'fires': '🔥', 'warriors': '🦊'}


@bot_app.route('clickStat')
def stat(token):
    hearts_user = User.query.join(User.clicker).order_by(Clicker.hearts.desc()).first()
    magic_user = User.query.join(User.clicker).order_by(Clicker.magic.desc()).first()
    fires_user = User.query.join(User.clicker).order_by(Clicker.fires.desc()).first()
    warriors_user = User.query.join(User.clicker).order_by(Clicker.warriors.desc()).first()
    msg = Message(peer_id=token.user_id,
                  text=f"Топ:\n"
                       f"@id{hearts_user.id} (№1 {symbols['hearts']}) x{hearts_user.clicker.hearts}\n"
                       f"@id{magic_user.id} (№1 {symbols['magic']}) x{magic_user.clicker.magic}\n"
                       f"@id{fires_user.id} (№1 {symbols['fires']}) x{fires_user.clicker.fires}\n"
                       f"@id{warriors_user.id} (№1 {symbols['warriors']}) x{warriors_user.clicker.warriors}"
                  )
    msg.add_button(label='Главное меню', menu_id='main')
    msg.add_button(label='Кликер', menu_id='clickAct')
    return msg


@bot_app.route('clickAct')
def action(token):
    user = User.query.filter_by(id=token.user_id).first()
    if token.args and token.args.get('type'):
        if token.args.get('type') == 'hearts':
            user.clicker.hearts += 1
        elif token.args.get('type') == 'magic':
            user.clicker.magic += 1
        elif token.args.get('type') == 'fires':
            user.clicker.fires += 1
        elif token.args.get('type') == 'warriors':
            user.clicker.warriors += 1
        db.session.commit()
    msg = Message(peer_id=token.user_id, text=f"{symbols['hearts']} x{user.clicker.hearts}\n"
                                              f"{symbols['magic']} x{user.clicker.magic}\n"
                                              f"{symbols['fires']} x{user.clicker.fires}\n"
                                              f"{symbols['warriors']} x{user.clicker.warriors}")
    msg.add_button(label=symbols['hearts'], menu_id='clickAct', args={'type': 'hearts'})
    msg.add_button(label=symbols['magic'], menu_id='clickAct', args={'type': 'magic'})
    msg.add_button(label=symbols['fires'], menu_id='clickAct', args={'type': 'fires'})
    msg.add_button(label=symbols['warriors'], menu_id='clickAct', args={'type': 'warriors'})
    msg.add_button(label='статистика', menu_id='clickStat', row=7)
    msg.add_button(label='Главное меню', menu_id='main', row=8, color='negative')
    return msg
