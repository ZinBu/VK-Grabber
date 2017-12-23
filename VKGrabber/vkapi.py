# coding: utf-8
""" VK api methods """

import random
import requests


class VK:
    """ VK API methods """

    def __init__(self, token):
        self.token = token

    def api(self, method, **kwargs):
        """
        method: string - VK API method
        **kwargs: key=value - requests params
        """

        if kwargs:
            params = dict(kwargs, v='5.65', access_token=self.token)
        else:
            params = dict(v='5.65', access_token=self.token)

        request = requests.post("https://api.vk.com/method/" + method, data=params).json()
        return request

    def get_random_wall_picture(self, group_id):
        """ Return random picture from wall group """

        max_num = self.api("photos.get", owner_id=group_id,
                           album_id='wall', count=0)["response"]["count"]
        num = random.randint(1, max_num)
        photo = self.api("photos.get", owner_id=str(group_id), album_id='wall',
                         count=1, offset=num)["response"]['items'][0]['id']
        attachment = 'photo' + str(group_id) + '_' + str(photo)
        return attachment
