import requests
import time
import random
import os
import json
import logging
from io import BytesIO


class Api(object):
    def __init__(self, access_token, name='name', version='5.101'):
        self.vk_url = "https://api.vk.com/method/"
        self.token = access_token
        self.name = name
        self.version = version
        self.VK_API = requests.Session()
        logging.info(f'{self.name} gApi started')
        self.valid = 'response' in self.request_get('utils.getServerTime')

    def request_get(self, method, parameters=None):
        if not parameters:
            parameters = {'access_token': self.token, 'v': self.version}
        if 'access_token' not in parameters:
            parameters.update({'access_token': self.token})
        if 'v' not in parameters:
            parameters.update({'v': self.version})

        try:
            request = self.VK_API.post(self.vk_url + method, parameters, timeout=10)
            if request.ok:
                if request.json().get('error', {'error_code': 0})['error_code'] == 6:  # too many requests
                    return self.request_get(method, parameters)
                return request.json()
            else:
                logging.error(f'request.status_code = {request.status_code}')
                time.sleep(5)
                return self.request_get(method, parameters)

        except requests.exceptions.RequestException as error_msg:
            logging.error(f'connection problems {error_msg}')
            time.sleep(5)
            return self.request_get(method, parameters)

        except Exception as error_msg:
            logging.error(f'{error_msg}')
            return {}

    def msg_send(self, payload):
        payload['random_id'] = payload.get('random_id', random.randint(0, 2 ** 64))
        if type(payload.get('attachment', '')) != str:
            payload['attachment'] = ','.join(payload['attachment'])
        msg = self.request_get('messages.send', payload)
        logging.info(f'send message {msg}')
        print(f'send message {msg}')
        if 'response' in msg:
            return msg['response']
        else:
            return False

    def msg_get(self, message_id):
        msg_info = self.request_get('messages.getById', {'message_ids': message_id})
        if 'response' not in msg_info:
            logging.error(f'get message error {msg_info}')
            return {}
        return msg_info['response']['items'][0]

    def get_user_info(self, user_id, fields='sex'):
        user_info = self.request_get('users.get', {'user_ids': user_id, 'fields': fields})
        if 'response' not in user_info:
            logging.error(f'get user error {user_info}')
            return {}
        return user_info['response'][0]

    def upload_photo_file(self, peer_id, filename):
        upload_server = self.request_get('photos.getMessagesUploadServer', {'peer_id': peer_id})
        if 'response' not in upload_server:
            logging.error(f'upload server error {upload_server}')
            return {}

        url = upload_server['response']['upload_url']
        file = {'photo': open(filename, 'rb')}
        uploading_file = requests.post(url, files=file).json()

        saving_photo = self.request_get('photos.saveMessagesPhoto', {'photo': uploading_file['photo'],
                                                                     'server': uploading_file['server'],
                                                                     'hash': uploading_file['hash']})
        if 'response' not in saving_photo:
            logging.error(f'saving photo error {saving_photo}')
            return {}
        return ['photo%s_%s_%s' % (saving_photo['response'][0]['owner_id'],
                                   saving_photo['response'][0]['id'],
                                   saving_photo['response'][0]['access_key'])]

    def get_admins(self):
        code = '''
            var group_id = API.groups.getById()[0].id;
            var admins = API.groups.getMembers({"group_id": group_id, "filter": "managers"});
            return admins.items;
        '''
        admins = self.request_get('execute', {'code': code})
        if 'response' not in admins:
            logging.error(f'get admins error {admins}')
            return []
        return admins['response']

    def unanswered(self):
        unread_msg = self.request_get('messages.getConversations', {'filter': 'unanswered', 'count': 200})
        try:
            unread_msg = [i['last_message'] for i in unread_msg['response']['items']]
            return unread_msg
        except Exception as error_msg:
            logging.error(f'unread_msg: {unread_msg} error: {error_msg}')
            return []

    def upload_image_url(self, image_url, peer_id=0, default_image='', group_id=None,
                         server_method='photos.getMessagesUploadServer',
                         save_method='photos.saveMessagesPhoto'):
        dir_path = os.path.abspath('img')
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        upload_params = {}
        if peer_id:
            upload_params.update({'peer_id': peer_id})
        if group_id:
            upload_params.update({'group_id': group_id})
        upload_server = self.request_get(server_method, upload_params)
        if 'response' not in upload_server:
            logging.error(f'upload_server: {upload_server}')
            return default_image
        upload_url = upload_server['response']['upload_url']
        filename = os.path.join(dir_path, image_url.split('/')[-1])

        with BytesIO() as img_buffer:
            resp = self.VK_API.get(image_url)
            if resp.ok:
                img_buffer.write(resp.content)
            else:
                logging.error(f'download file: {resp.status_code}')
                return default_image
            file = {'photo': (filename, img_buffer.getvalue())}
            upload_image = self.VK_API.post(upload_url, files=file)
        if upload_image.ok:
            upload_response = upload_image.json()
        else:
            logging.error(f'upload file: {upload_image.status_code}')
            if os.path.exists(filename):
                os.remove(filename)
            return default_image

        image_params = {
            'photo': upload_response['photo'],
            'server': upload_response['server'],
            'hash': upload_response['hash'],
        }
        if group_id:
            image_params.update({'group_id': group_id})
        save_image = self.request_get(save_method, image_params)
        if 'response' not in save_image:
            logging.error(f'save_image: {save_image}')
            return default_image
        print('save_image', save_image)
        vk_image = save_image['response'][0]
        return f"photo{vk_image['owner_id']}_{vk_image['id']}_{vk_image['access_key']}"


