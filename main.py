import requests
from typing import List
from datetime import datetime

from config import TOKEN


BASE_URL = f'https://api.telegram.org/bot{TOKEN}/'


class User:

    def __init__(self, id, is_bot, first_name, last_name, username, language_code):
        self.id = id
        self.is_bot = is_bot
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.language_code = language_code

    @classmethod
    def from_dict(cls, user_dict):
        id = user_dict['id']
        is_bot = user_dict['is_bot']
        first_name = user_dict['first_name']
        last_name = user_dict.get('last_name')  # may be missing e.g. for bots
        username = user_dict['username']
        language_code = user_dict['username']
        return cls(id, is_bot, first_name, last_name, username, language_code)

    
class Chat:

    def __init__(self, id, first_name, last_name, username, type):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.type = type

    @classmethod
    def from_dict(cls, chat_dict):
        id = chat_dict['id']
        first_name = chat_dict['first_name']
        last_name = chat_dict.get('last_name')  # may be missing e.g. for bots
        username = chat_dict['username']
        type = chat_dict['type']
        return cls(id, first_name, last_name, username, type)


class Message:

    def __init__(self, id, from_user: User, chat: Chat, date, text):
        self.id = id
        self.from_user = from_user
        self.chat = chat
        self.date = date
        self.text = text

    @classmethod
    def from_dict(cls, message_dict):
        id: int = message_dict['message_id']
        from_user: User = User.from_dict(message_dict['from'])
        chat: Chat = Chat.from_dict(message_dict['chat'])
        date: int = message_dict['date']  # in seconds since 1/1/1970
        text = message_dict.get('text')
        return cls(id, from_user, chat, date, text)
        

class Update:

    def __init__(self, id, message: Message):
        self.id = id
        self.message = message

    @classmethod
    def from_dict(cls, update_dict):
        id: int = update_dict['update_id']
        message: Message = Message.from_dict(update_dict['message'])
        return cls(id, message)


def json(request_func):
    """
    decorator for getting response json as dict
    """
    def wrapper(*args, **kwargs):
        response = request_func(*args, **kwargs)
        return response.json()
    return wrapper

@json
def get_response(url, params=None):
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response
    return None

def get_tg_response(suburl, params=None):
    response = get_response(BASE_URL + suburl, params)
    if response['ok']:
        return response['result']
    raise requests.exceptions.RequestException('Telegram is down')  # RequstException is parent for all request exceptins


# specific api calls

def getMe() -> User:
    return User.from_dict(get_tg_response('getMe'))

def getUpdates() -> List[Update]:
    """
    returns last 24 hours updates
    """
    updates = [Update.from_dict(update_dict) for update_dict in get_tg_response('getUpdates')]
    return updates

def sendMessage(chat_id, text) -> Message:
    params = {
        'chat_id': chat_id,
        'text': text
    }
    return Message.from_dict(get_tg_response('sendMessage', params))

def sendDice(chat_id) -> Message:
    params = {
        'chat_id': chat_id
    }
    return Message.from_dict(get_tg_response('sendDice', params))



if __name__ == '__main__':

    # TODO: make bot answer to last messages

    # fetch last 24h updates
    updates = getUpdates()
    # updates = [update for update in getUpdates()]

    # get users interacted with bot
    user_ids = []
    for update in updates:
        user_id = update.message.from_user.id
        if user_id not in user_ids:
            user_ids.append(user_id)

    # prints message history (all users)
    for update in updates:
        print(f"{datetime.utcfromtimestamp(update.message.date).strftime('%H:%M:%S')} "  # UTC-0 time \
              f"{update.message.from_user.username}: "\
              f"{update.message.text}")


    # chat id is user's id to whom you're gonna message

    # send message to every known user
    for user_id in user_ids:
        # sent_message_dict = sendMessage(user_id, 'With the lights out...')
        # sent_message = Message.from_dict(sent_message_dict)
        # print(f'Bot sent message to {sent_message.chat.first_name} ({sent_message.chat.username}): {sent_message.text}')
        sendDice(user_id)
