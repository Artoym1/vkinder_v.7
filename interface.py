import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from data_store import add_viewed, insert_viewed
from config import comunity_token, access_token
from core import VkTools


class BotInterface:

    def __init__(self, comunity_token, access_token):
        self.interface = vk_api.VkApi(token=comunity_token)
        self.api = VkTools(access_token)
        self.params = None
        self.offset = 0

    def message_send(self, user_id, message, attachment=None):
        self.interface.method('messages.send',
                              {'user_id': user_id,
                               'message': message,
                               'attachment': attachment,
                               'random_id': get_random_id()
                               }
                              )

    def event_handler(self):
        longpoll = VkLongPoll(self.interface)
        city_name_switch = False
        sex_switch = False
        bdate_swith = False
        for event in longpoll.listen():

            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()

                if command == 'п' or command == "s":
                    if self.params is None:
                        self.message_send(event.user_id, f'Для начала поиска введи "Старт" или "GO"')

                    else:
                        users = self.api.search_users(self.params, self.offset)
                        self.offset = self.offset + 1
                        user = users.pop()
                        while insert_viewed(user["id"]):
                            user = users.pop()

                        if True:
                            photos_user = self.api.get_photos(user['id'])
                            attachment = ''
                            for num, photo in enumerate(photos_user):
                                attachment += f'photo{user["id"]}_{photo["id"]},'
                                if num == 2:
                                    break
                            self.message_send(event.user_id,
                                              f'Встречайте {user["name"]}, vk.com/id{user["id"]}',
                                              attachment=attachment
                                              )
                            add_viewed(user["id"], event.user_id)
                            self.message_send(event.user_id,
                                              f'{self.params["name"]}, отправь "п" или "s" для продолжения...')

                elif command == 'старт' or command == 'go':
                    self.params = self.api.get_profile_info(event.user_id)

                    if self.params['sex'] is None or self.params['city'] is None or self.params['bdate'] is None:
                        self.message_send(event.user_id, f'{self.params["name"]}, у тебя не заполнен профиль ВК, '
                                                         f'чтобы поиск был точным мы зададим несколько вопросов. '
                                                         f'Ответь на каждый отдельным сообщением')

                    if self.params['sex'] is None:
                        sex_switch = True
                        self.message_send(event.user_id, f'{self.params["name"]}, Сначала отправь цифру: '
                                                         f'1 если ты женщина, '
                                                         f'2 если мужчина')
                elif sex_switch is True:
                    sex_user = int(command)
                    print(sex_user)
                    sex_switch = False
                    self.params['sex'] = sex_user

                    if self.params['city'] is None:
                        city_name_switch = True
                        self.message_send(event.user_id, f'Введи город для поиска... ')

                elif city_name_switch is True:
                    city_name = command
                    city_name_switch = False
                    city_user = self.api.get_city(city_name)
                    self.params['city'] = city_user

                    if self.params['bdate'] is None:
                        bdate_swith = True
                        self.message_send(event.user_id, f'Отправь дату рождения в формате ММ.ДД.ГГГГ')

                elif bdate_swith is True:
                    self.params['bdate'] = command
                    bdate_swith = False

                    self.message_send(event.user_id, f'Отправь "п" или "s" для продолжения.....')

                else:
                    self.message_send(event.user_id, f'Для начала поиска введи "Старт" или "GO". '
                                                     f'Отправь "п" или "s" для продолжения...')


if __name__ == '__main__':
    bot = BotInterface(comunity_token, access_token)
    bot.event_handler()
