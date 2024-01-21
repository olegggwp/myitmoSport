import json
import requests
import time

token_update_config = {
    'headers': {
        "User-Agent":
        "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru",
        # 'Accept-Encoding': 'gzip, deflate, br',
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://my.itmo.ru",
        "DNT": "1",
        "Connection": "keep-alive",
        "Referer": "https://my.itmo.ru/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
    },
    'data': {
        "refresh_token": "?",  # changable
        "scopes": "openid profile",
        "client_id": "student-personal-cabinet",
        "grant_type": "refresh_token",
    },
}

storage_data = {
}

# saves storage_data to file
def save_storage_data(storage_data):
    with open("storage_data.json", "w") as file:
        json.dump(storage_data, file)
        

# loads storage_data from file
def load_storage_data():
    global storage_data, token_update_config
    with open("storage_data.json", "r") as file:
        storage_data = json.load(file)
        token_update_config['data']['refresh_token'] = storage_data['cookies']['auth._refresh_token.itmoId']


def token_upd(storage_data, token_update_config):
    cookies, headers = storage_data["cookies"], storage_data["headers"]
    response = requests.post(
        "https://id.itmo.ru/auth/realms/itmo/protocol/openid-connect/token",
        headers=token_update_config['headers'],
        data=token_update_config['data'],
    )
    new_cookies = response.json()

    exp = (int(cookies["auth._token_expiration.itmoId"]) +
           int(new_cookies["expires_in"]) * 1000)  # exp

    cookies["auth._token.itmoId"] = "Bearer%20e" + new_cookies["access_token"]
    cookies["auth._token_expiration.itmoId"] = str(exp)
    cookies["auth._refresh_token.itmoId"] = new_cookies["refresh_token"]
    cookies["auth._refresh_token_expiration.itmoId"] = str(exp)
    cookies["auth._id_token.itmoId"] = new_cookies["id_token"]
    cookies["auth._id_token_expiration.itmoId"] = str(exp)
    headers["Authorization"] = "Bearer " + new_cookies["access_token"]

    storage_data["cookies"] = cookies
    storage_data["headers"] = headers
    save_storage_data(storage_data)


params = {
    "building_id": "273",
    "date_start": "2024-01-22",
    "date_end": "2024-01-30",
}

# unix time to gmt time
def unix_to_time(unix):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(unix))


def get_slots():
    global storage_data, params
    cookies, headers = storage_data["cookies"], storage_data["headers"]
    response = requests.get(
        "https://my.itmo.ru/api/sport/my_sport/schedule/available",
        params=params,
        cookies=cookies,
        headers=headers,
    )
    data = response.json()
    print(
        "==new data==============================================================="
    )
    print(str(time.time()) + " " + unix_to_time(time.time()))
    print("next token updating in: " + str(unix_to_time(get_deadline())))
    print(
        "========================================================================="
    )
    for day in data["result"]:
        print(day["date"] + " -----------------------------------------------")
        for lesson in day["lessons"]:
            # 44824
            if lesson["type_name"] == "Занятие для студентов с задолженностью":
                if lesson["available"] > 0:
                    print(lesson["id"])
                    print(lesson["section_name"])
                    print(lesson["teacher_fio"])
                    print(lesson["lesson_level_name"])
                    # print(lesson['limit'])
                    print(lesson["time_slot_start"])
                    print(lesson["time_slot_end"])


def get_deadline():
    global storage_data
    return int(storage_data['cookies']["auth._token_expiration.itmoId"]) / 1000


def near_now():
    return int(time.time()) + 5



load_storage_data()
while True:
    while near_now() > get_deadline():
        print("Updating token, " + str(time.time()))
        token_upd(storage_data, token_update_config)
    get_slots()
    time.sleep(20)
