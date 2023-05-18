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
        bdate_switch = False
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
                        try:
                            user = users.pop()
                        except KeyError:
                            return
                        while insert_viewed(user["id"]):
                            user = users.pop()
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
                        self.message_send(event.user_id, f'{self.params["name"]}, для поиска нам нужно '
                                                         f'уточнить кое-что...,'
                                                         f'{new_str}Ответь на вопросы отдельными сообщениями, '
                                                         f'{new_str}Затем отправь "П" или "S" для продолжения...')

                        if self.params['sex'] is None:
                            sex_switch = True
                            self.message_send(event.user_id, f'{self.params["name"]}, кого будем искать?{new_str}'
                                                             f'МУЖЧИНУ или ЖЕНЩИНУ')

                        if self.params['city'] is None:
                            city_name_switch = True
                            self.message_send(event.user_id, f'В следующем сообщении напиши ГОРОД в '
                                                             f'котором будем искать тебе пару... ')

                        if self.params['bdate'] is None:
                            bdate_switch = True
                            self.message_send(event.user_id, f'В следующем сообщении отправь ГОД твоего рождения')

                elif sex_switch is True:
                    if 'жен' in command or 'дев' in command or 'баб' in command:
                        self.params['sex'] = 2
                    else:
                        self.params['sex'] = 1
                    sex_switch = False

                elif city_name_switch is True:
                    self.params['city'] = self.api.get_city(command)
                    city_name_switch = False

                elif bdate_switch is True:
                    self.params['bdate'] = '..' + command
                    bdate_switch = False



                else:
                    self.message_send(event.user_id, f'Привет!, это Vkinder. '
                                                     f'давай подберем тебе пару.{new_str * 2}'
                                                     f'Для активации бота введи "Старт" или "GO".{new_str} '
                                                     f'Для продолжения отправь "П" или "S" ...')


if __name__ == '__main__':
    bot = BotInterface(comunity_token, access_token)
    bot.event_handler()
