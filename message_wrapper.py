import json
import random


class Menu:
    def __init__(self):
        self.routes = dict()

    def route(self, route_str):
        def decorator(f):
            self.routes.update({route_str: f})
            return f
        return decorator

    def serve(self, path):
        return self.routes.get(path)


class Token:
    def __init__(self, msg, prev_msg=()):
        self.user_id = msg.get('from_id', 0)
        self.text = msg.get('text', '')
        payload = json.loads(msg.get('payload', '{}'))
        self.menu = payload.get('mid', '')
        self.args = payload.get('args', {})
        self.attachments = msg.get('attachments', [])
        self.prev_msg = prev_msg


class Message:
    def __init__(self, peer_id, text='', attachments=None, keyboard=None, random_id=None):
        self.peer_id = peer_id
        self.text = text
        self.attachments = attachments if attachments else []
        self.keyboard = keyboard
        if keyboard is None:
            self.empty_keyboard()
        self.random_id = random_id if random_id else random.randrange(2**64)

    def empty_keyboard(self, rows=10, columns=5):
        self.keyboard = [[None for _ in range(columns)] for _ in range(rows)]

    def add_button(self, label, menu_id, args=None, row=None, column=None, color='default'):
        vk_button = {'action': {'type': 'text',
                                'payload': {'mid': menu_id,
                                            'args': args},
                                'label': label},
                     'color': color}
        if row is not None:
            if column is None:
                if None in self.keyboard[row]:
                    column = self.keyboard[row].index(None)
                else:
                    return False
            self.keyboard[row][column] = vk_button
        else:
            row = 0
            if column is not None:
                while row < len(self.keyboard) and self.keyboard[row][column] is None:
                    row += 1
            else:
                while row < len(self.keyboard) and None not in self.keyboard[row]:
                    row += 1
                column = self.keyboard[row].index(None)
            if row < len(self.keyboard):
                self.keyboard[row][column] = vk_button
            else:
                return False
        return True

    def keyboard_from_buttons(self, one_time=False):
        keyboard = {'one_time': one_time, 'buttons': []}
        for key_row in self.keyboard:
            buttons_row = []
            for key in key_row:
                if key:
                    if type(key['action']['payload']) != str:
                        key['action']['payload'] = json.dumps(key['action']['payload'], ensure_ascii=False)
                    buttons_row.append(key)
            if buttons_row:
                keyboard['buttons'].append(buttons_row)
        if keyboard['buttons']:
            return json.dumps(keyboard, ensure_ascii=False)
        return ''

    def convert_msg(self):
        return {
            'peer_id': self.peer_id,
            'random_id': self.random_id,
            'message': self.text,
            'attachment': ','.join(self.attachments),
            'keyboard': self.keyboard_from_buttons()
        }


