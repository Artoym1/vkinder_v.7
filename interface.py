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
        new_str = '\n'
        for event in longpoll.listen():

            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()

                if command == 'п' or command == "s":
                    if self.params is None:
                        self.message_send(event.user_id, f'Для начала поиска введи: {new_str}"Старт" или "GO"')

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
                                              f'{self.params["name"]}, отправь "П" или "S" {new_str}для продолжения...')

                elif command == 'старт' or command == 'go':
                    self.params = self.api.get_profile_info(event.user_id)

                    if self.params['sex'] is None or self.params['city'] is None or self.params['bdate'] is None:
                        self.message_send(event.user_id, f'{self.params["name"]}, у тебя не заполнен профиль ВК,'
                                                         f'{new_str}для поиска нам нужно уточнить кое-что... ')

                        if self.params['sex'] is None:
                            sex_switch = True
                            self.message_send(event.user_id, f'{self.params["name"]}, Скажи нам в '
                                                             f'отдельном сообщении кого ты хочешь найти{new_str} '
                                                             f'мужчину или женщину')

                        if self.params['city'] is None:
                            city_name_switch = True
                            self.message_send(event.user_id, f'В следующем сообщении напиши название города в'
                                                             f'котором будем искать тебе пару... ')

                        if self.params['bdate'] is None:
                            bdate_swith = True
                            self.message_send(event.user_id, f'Отправь дату твоего рождения в формате:'
                                                             f'{new_str} ММ.ДД.ГГГГ')

                elif sex_switch is True:
                    if 'жен' in command or 'дев' in command or 'баб' in command:
                        sex_user = 2
                    else:
                        sex_user = 1
                    sex_switch = False
                    self.params['sex'] = sex_user


                elif city_name_switch is True:
                    city_name = command
                    city_name_switch = False
                    city_user = self.api.get_city(city_name)
                    self.params['city'] = city_user

                elif bdate_swith is True:
                    self.params['bdate'] = command
                    bdate_swith = False

                    self.message_send(event.user_id, f'Отлично! {new_str}Отправь "П" или "S"'
                                                     f'{new_str}для продолжения.....')

                else:
                    self.message_send(event.user_id, f'Привет!, это Vrinder. '
                                                     f'давай подберем тебе пару.{new_str*2}'
                                                     f'Для начала поиска введи "Старт" или "GO".{new_str} '
                                                     f'Для продолжения отправь "П" или "S" ...')


if __name__ == '__main__':
    bot = BotInterface(comunity_token, access_token)
    bot.event_handler()
