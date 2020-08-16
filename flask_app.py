from flask import request
from flask_vk_bot import *

events = list()
messages = dict()


def message_processing(msg):
    user_token = Token(msg)
    menu_function = bot_app.serve(user_token.menu)
    if not menu_function and user_token.text == '/key':
        menu_function = bot_app.serve('main')
        bot_message = menu_function(user_token)
        bot_api.msg_send(payload=bot_message.convert_msg())
    elif not menu_function:
        messages.setdefault(user_token.user_id, []).append(user_token)
    else:
        user_token.prev_msg = messages.pop(user_token.user_id, [])
        bot_message = menu_function(user_token)
        bot_api.msg_send(payload=bot_message.convert_msg())


@app.route('/vk_callback/', methods=['POST'])
def vk_callback():
    content = request.get_json(force=True)
    if content.get('type') == 'confirmation':
        confirm = CONF.get('VK_confirm')
        return confirm

    elif content.get('type') == 'message_new':
        global events
        if content['event_id'] in events:
            return 'Ok'
        events = [content['event_id']] + events[:1000]
        message_processing(content['object']['message'])
    return 'Ok'


@app.route("/")
def index():
    return 'server working'


if __name__ == '__main__':
    app.run(debug=True)
