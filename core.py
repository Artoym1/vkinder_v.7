from datetime import datetime
from config import access_token
from operator import itemgetter
import vk_api


class VkTools:
    def __init__(self, access_token):
        self.api = vk_api.VkApi(token=access_token)

    def get_profile_info(self, user_id):
        info, = self.api.method('users.get',
                                {'user_ids': user_id,
                                 'fields': 'city ,bdate== None ,sex== None ,relation,home_town'
                                 }
                                )
        user_info = {'name': info['first_name'],
                     'id': info['id'],
                     'bdate': info['bdate'] if 'bdate' in info else None,
                     'home_town': info['home_town'] if 'home_town' in info else None,
                     'sex': info['sex'] if 'sex' in info else None,
                     'city': info['city']['id'] if 'city' in info else None,
                     'offset': 0
                     }
        return user_info

    def get_city(self, city_name):
        cities = self.api.method("database.getCities",
                                 {'items': 0,
                                  'q': city_name,
                                  'count': 10,
                                  'offset': 0,
                                  }
                                 )
        try:
            cities = cities['items']
        except KeyError:
            return []
        for city in cities:
            res = city['id']
            return res

    def search_users(self, params, offset):
        sex = 1 if params['sex'] == 2 else 2
        city = params['city']
        curent_year = datetime.now().year
        user_year = int(params['bdate'].split('.')[2])
        age = curent_year - user_year
        age_from = age - 1
        age_to = age + 1

        users = self.api.method('users.search',
                                {'count': 50,
                                 'offset': offset,
                                 'age_from': age_from,
                                 'age_to': age_to,
                                 'sex': sex,
                                 'city': city,
                                 'status': 6,
                                 'has_photo': True,
                                 'is_closed': False,
                                 'can_access_closed': True
                                 }
                                )
        try:
            users = users['items']
        except KeyError:
            return []

        res = []

        for user in users:
            if user['is_closed'] is False:
                res.append({'id': user['id'],
                            'name': user['first_name'] + ' ' + user['last_name'],
                            'is_closed': user['is_closed']
                            }
                           )
        return res

    def get_photos(self, user_id):
        photos = self.api.method('photos.get',
                                 {'album_id': 'profile',
                                  'owner_id': user_id,
                                  'extended': 1
                                  }
                                 )
        try:
            photos = photos['items']
        except KeyError:
            return

        result = []
        for num, photo in enumerate(photos):
            result.append({'owner_id': photo['owner_id'],
                           'id': photo['id'],
                           'likes_comments': photo['likes'].get('count') + photo['comments'].get('count'),
                           })
        result = sorted(result, key=itemgetter('likes_comments'), reverse=True)
        result = result[0:3]
        return result


if __name__ == '__main__':
    bot = VkTools(access_token)
    params = bot.get_profile_info(799167117)
    users = bot.search_users(params, offset=None)
