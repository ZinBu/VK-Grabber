# coding: utf-8
""" Brings all photos from dialogs of user """

import math
import os
import threading
from time import sleep

import requests
import vk  # external lib
from vkapi import VK


def thread(func):
    """ Run in thread """

    def run(*args, **kwargs):
        """ Threading """
        target = threading.Thread(target=func, args=args, kwargs=kwargs)
        # target.setDaemon(True)
        target.start()
        return target

    return run


def log_in_vk():
    """ Open file token or login and create a token """

    scope = "friends,photos,audio,video,docs,notes,pages,status,wall,groups,messages,notifications,offline"
    app_id = 5377227

    try:
        with open("Token", "r") as memory:
            token = memory.read()

    except Exception as error:
        print("NO TOKEN", error)
        while True:
            log = input("Login: ")
            password = input("Password: ")
            try:
                session = vk.AuthSession(app_id=app_id, user_login=log,
                                         user_password=password, scope=scope)
            except Exception as error:
                print(error)
            else:
                token = session.get_access_token()
                with open("Token", "w") as memory:
                    memory.write(token)
                break
    return token


def get_user_info(user_id=None):
    """  Help to get: Name - id """

    try:
        if user_id:
            info = VK.api("users.get", user_ids=user_id)["response"][0]
        else:
            info = VK.api("users.get")["response"][0]

        info = "{} {} - {}".format(info["first_name"],
                                   info["last_name"],
                                   info["id"])
    except Exception:
        info = "Error"
    return info


def save_data(data, path, name):
    """ Сохраннение данных """

    with open(path + name, "w") as file_:
        file_.write(str(data))


@thread
def save_photos(photos_list, path):
    """ Сохранение фото по ссылкам """

    for link in photos_list:
        with open(path + link[-10:], "wb") as file_:
            file_.write(requests.get(link).content)
        print("{} was saved!".format(path))


VK = VK(log_in_vk())
USER_INFO = get_user_info()
DIALOGS_COUNT = VK.api("messages.getDialogs", count=0)["response"]["count"]
MULTIPLIER = 0
IDES = []  # id будущих диалогов
# размер фото
SIZE = "photo_130"  # photo_604/photo_130 - для быстрой загрузки

print("User: ", USER_INFO)
print("Count of dialogs: ", DIALOGS_COUNT)

# вычисляем количество офсетов
if DIALOGS_COUNT >= 200:
    OFFSETS = math.ceil(DIALOGS_COUNT / 200)
else:
    OFFSETS = 1

# обходим все диалоги
for i in range(OFFSETS):
    dialogs = VK.api("messages.getDialogs", count=200,
                     offset=0 + 200 * MULTIPLIER)["response"]
    # получаем id пользователей с которыми есть диалог и дополняем
    # основной список
    IDES.extend([x["message"]["user_id"] for x in dialogs["items"]])
    MULTIPLIER += 1
    sleep(0.3)

print("Count of dialogs receive: ", len(IDES))

# создаем папку с пользователем
try:
    os.mkdir(USER_INFO)
except FileExistsError:
    pass

# TODO: расширить максимум вложений выгружаемых из диалога (сейчас вроде 200)
# получаем ссылки
for id_ in IDES:
    sleep(1)
    # создаем директорию диалога и переходим в нее
    companion = get_user_info(id_)  # данные собеседника
    dir_dialog = "{}/Диалог с {}".format(USER_INFO, companion)
    try:
        os.mkdir(dir_dialog)
    except FileExistsError:
        pass

    try:
        dialog_links = VK.api("messages.getHistoryAttachments",
                              count=0,
                              peer_id=id_,
                              media_type="photo")["response"]["items"]

    except Exception as e:
        print(e)

    # список отправленных изображений
    # TODO сделать итератор может?
    sent = [x["attachment"]["photo"][SIZE] for x in dialog_links if x["attachment"]["photo"]["owner_id"] != id_]
    dir_sent = "{}/Sent/".format(dir_dialog)
    try:
        os.mkdir(dir_sent)
    except FileExistsError:
        pass
    save_data(sent, dir_sent, "sent.txt")
    save_photos(sent, dir_sent)  # сохраняем исходящие фото в потоке

    # список полученных изображений
    received = [x["attachment"]["photo"][SIZE] for x in dialog_links if x["attachment"]["photo"]["owner_id"] == id_]
    dir_received = "{}/Received/".format(dir_dialog)
    try:
        os.mkdir(dir_received)
    except FileExistsError:
        pass
    save_data(received, dir_received, "received.txt")
    save_photos(received, dir_received)  # сохраняем входящие фото в потоке
    sleep(1)
