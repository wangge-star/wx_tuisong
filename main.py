import random
from time import localtime
from requests import get, post
from datetime import datetime, date
from zhdate import ZhDate
from datetime import datetime, timedelta
import sys
import os
import random

# 猫爱吃的食物列表
cat_food_list = [
    "鸡胸肉",
    "猫条",
    "三文鱼",
    "鸭肉",
    "牛肉",
    "鹌鹑肉",
    "火鸡肉",
    "鲜虾",
    "鱼子酱",
    "鲜蛋黄",
    "鲜鸡肝",
    "鲜牛肝",
    "猫草",
    "干燥鱼片",
    "干燥鸡肉块",
    "干燥牛肉块"
]

def days_until_next_period(current_date, last_period_date, period_cycle):
    # 计算下一次月经的日期
    next_period_date = last_period_date + timedelta(days=period_cycle)

    # 如果当前日期在下一次月经之前，则距离下一次月经的天数为两者之间的天数
    if current_date < next_period_date:
        days_until_next_period = (next_period_date - current_date).days
    # 如果当前日期在下一次月经之后，则需要连续计算多次月经周期，直到找到下一次月经之后的日期
    else:
        while current_date >= next_period_date:
            last_period_date = next_period_date
            next_period_date += timedelta(days=period_cycle)
        days_until_next_period = (next_period_date - current_date).days

    return days_until_next_period
def get_access_token():
    # appId
    app_id = config["app_id"]
    # appSecret
    app_secret = config["app_secret"]
    post_url = ("https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}"
                .format(app_id, app_secret))
    try:
        access_token = get(post_url).json()['access_token']
    except KeyError:
        print("获取access_token失败，请检查app_id和app_secret是否正确")
        os.system("pause")
        sys.exit(1)
    print("请求获取的access_token为：{}".format(access_token))
    return access_token
def get_weather(region):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    key = config["weather_key"]
    region_url = "https://geoapi.qweather.com/v2/city/lookup?location={}&key={}".format(region, key)
    response = get(region_url, headers=headers).json()
    if response["code"] == "404":
        print("推送消息失败，请检查地区名是否有误！")
        os.system("pause")
        sys.exit(1)
    elif response["code"] == "401":
        print("推送消息失败，请检查和风天气key是否正确！")
        os.system("pause")
        sys.exit(1)
    else:
        # 获取地区的location--id
        location_id = response["location"][0]["id"]
    weather_url = "https://devapi.qweather.com/v7/weather/now?location={}&key={}".format(location_id, key)
    response = get(weather_url, headers=headers).json()
    # 天气
    weather = response["now"]["text"]
    # 当前温度
    temp = response["now"]["temp"] + u"\N{DEGREE SIGN}" + "C"
    # 风向
    wind_dir = response["now"]["windDir"]
    # 获取逐日天气预报
    url = "https://devapi.qweather.com/v7/weather/3d?location={}&key={}".format(location_id, key)
    response = get(url, headers=headers).json()
    # 最高气温
    max_temp = response["daily"][0]["tempMax"] + u"\N{DEGREE SIGN}" + "C"
    # 最低气温
    min_temp = response["daily"][0]["tempMin"] + u"\N{DEGREE SIGN}" + "C"
    # 日出时间
    sunrise = response["daily"][0]["sunrise"]
    # 日落时间
    sunset = response["daily"][0]["sunset"]
    url = "https://devapi.qweather.com/v7/air/now?location={}&key={}".format(location_id, key)
    response = get(url, headers=headers).json()
    # print(response)
    if response["code"] == "200":
        # 空气质量
        category = response["now"]["category"]
        # pm2.5
        pm2p5 = response["now"]["pm2p5"]
    else:
        # 国外城市获取不到数据
        category = ""
        pm2p5 = ""
    id = random.randint(1, 16)
    url = "https://devapi.qweather.com/v7/indices/1d?location={}&key={}&type={}".format(location_id, key, id)
    response = get(url, headers=headers).json()
    proposal = ""
    if response["code"] == "200":
        proposal += response["daily"][0]["text"]
    return weather, temp, max_temp, min_temp, wind_dir, sunrise, sunset, category, pm2p5, proposal
    #获取天气信息
# def get_tianhang():
#     try:
#         key = config["tian_api"]
#         region=config["region"]
#         #url = "http://api.tianapi.com/caihongpi/index?key={}".format(key)
#         url = "https://apis.tianapi.com/tiangou/index?key={}".format(key)
#         headers = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
#                           'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
#             'Content-type': 'application/x-www-form-urlencoded'
#         }
#         response = get(url, headers=headers).json()
#         # print(response)
#         if response["code"] == 200:
#             chp = response["result"]["content"]
#             print(chp)
#         else:
#             chp = ""
#     except KeyError:
#         chp = ""
#     return chp
def get_birthday(birthday, year, today):
    birthday_year = birthday.split("-")[0]
    # 判断是否为农历生日
    if birthday_year[0] == "r":
        r_mouth = int(birthday.split("-")[1])
        r_day = int(birthday.split("-")[2])
        # 获取农历生日的生日
        try:
            year_date = ZhDate(year, r_mouth, r_day).to_datetime().date()
        except TypeError:
            print("请检查生日的日子是否在今年存在")
            os.system("pause")
            sys.exit(1)
    else:
        # 获取国历生日的今年对应月和日
        birthday_month = int(birthday.split("-")[1])
        birthday_day = int(birthday.split("-")[2])
        # 今年生日
        year_date = date(year, birthday_month, birthday_day)
    # 计算生日年份，如果还没过，按当年减，如果过了需要+1
    if today > year_date:
        if birthday_year[0] == "r":
            # 获取农历明年生日的月和日
            r_last_birthday = ZhDate((year + 1), r_mouth, r_day).to_datetime().date()
            birth_date = date((year + 1), r_last_birthday.month, r_last_birthday.day)
        else:
            birth_date = date((year + 1), birthday_month, birthday_day)
        birth_day = str(birth_date.__sub__(today)).split(" ")[0]
    elif today == year_date:
        birth_day = 0
    else:
        birth_date = year_date
        birth_day = str(birth_date.__sub__(today)).split(" ")[0]
    return birth_day

def calculate_age(birth_date_str):
    # 解析出生日期字符串
    birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d')
    # 获取当前日期
    current_date = datetime.now()
    # 计算年龄
    years = current_date.year - birth_date.year
    months = current_date.month - birth_date.month
    if current_date.day < birth_date.day:
        months -= 1
    if months < 0:
        years -= 1
        months += 12
    return years, months
def calculate_days_to_nearest_holiday():
    # 获取当前日期
    current_date = datetime.now()

    # 获取当前农历日期
    current_lunar_date = ZhDate.today().to_datetime()

    # 创建一个空列表来存储节假日日期和名称
    holidays = []

    # 添加公历节假日日期和名称
    holidays.append((datetime(current_date.year, 1, 1), "元旦"))
    holidays.append((datetime(current_date.year, 4, 4), "清明节"))
    holidays.append((datetime(current_date.year, 5, 1), "劳动节"))
    holidays.append((datetime(current_date.year, 10, 1), "国庆节"))

    # 添加农历节假日日期和名称
    holidays.append((ZhDate(current_lunar_date.year, 1, 1).to_datetime(), "春节"))
    holidays.append((ZhDate(current_lunar_date.year, 1, 15).to_datetime(), "元宵节"))
    holidays.append((ZhDate(current_lunar_date.year, 5, 5).to_datetime(), "端午节"))
    holidays.append((ZhDate(current_lunar_date.year, 8, 15).to_datetime(), "中秋节"))

    # 计算距离最近节假日的天数、日期和节假日名称
    nearest_holiday = None
    nearest_holiday_days = timedelta(days=365)  # 初始化为一年的天数
    nearest_holiday_name = None
    for holiday_date, holiday_name in holidays:
        days_until_holiday = holiday_date - current_date
        if days_until_holiday >= timedelta(days=0) and days_until_holiday < nearest_holiday_days:
            nearest_holiday = holiday_date
            nearest_holiday_days = days_until_holiday
            nearest_holiday_name = holiday_name

    return nearest_holiday, nearest_holiday_days.days, nearest_holiday_name



def get_ciba():
    url = "http://open.iciba.com/dsapi/"
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    r = get(url, headers=headers)
    note_en = r.json()["content"]
    note_ch = r.json()["note"]
    return note_ch, note_en


def send_message(to_user, access_token):
    url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}".format(access_token)
    week_list = ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"]
    year = localtime().tm_year
    month = localtime().tm_mon
    day = localtime().tm_mday
    today = datetime.date(datetime(year=year, month=month, day=day))
    week = week_list[today.isoweekday() % 7]
    # 获取在一起的日子的日期格式
    love_year = int(config["love_date"].split("-")[0])
    love_month = int(config["love_date"].split("-")[1])
    love_day = int(config["love_date"].split("-")[2])
    love_date = date(love_year, love_month, love_day)
    # print(love_date)
    # 获取在一起的日期差
    love_days = str(today.__sub__(love_date)).split(" ")[0] #这部分可以计算天数
    # print(love_days)
    #获取结婚的日子的日期格式
    marry_year = int(config["marry_date"].split("-")[0])
    marry_month = int(config["marry_date"].split("-")[1])
    marry_day = int(config["marry_date"].split("-")[2])
    marry_date = date(marry_year, marry_month, marry_day)
    # print(marry_date)
    # 获取在一起的日期差
    marry_days = str(today.__sub__(marry_date)).split(" ")[0]  # 这部分可以计算天数
    print(marry_days)
    # 获取所有生日数据
    birthdays = {}
    for k, v in config.items():
        if k[0:5] == "birth":
            birthdays[k] = v
    print(birthdays)
    for key, value in birthdays.items():
        # 获取距离下次生日的时间
        birth_day = get_birthday(value["birthday"], year, today)
        # print(value["birthday"])
        if birth_day == 0:
            birthday_left = "今天{}生日哦，祝{}生日快乐！".format(value["name"], value["name"])
        else:
            birthday_left = "离鸡爪生日{}天".format(birth_day)
    marry_day_left=get_birthday(config["marryday"],year,today)
    love_day_left=get_birthday(config["love_date"],year,today)
    print(marry_day_left)
    a,b=calculate_age(config["midou"])
    midou="{}岁{}个月".format(a,b)
    # 计算距离最近的节假日的天数、日期和节假日名称
    nearest_holiday, days, holiday_name = calculate_days_to_nearest_holiday()
    if days == 0:
        selected_food = "给米兜加餐{}~".format(random.choice(cat_food_list[1:]))  # 从除去猫粮外的其他食物中随机选择
    else:
        if random.random() < 0.75:
            selected_food = "喂米兜猫粮吧"
        else:
            c= random.choice(cat_food_list[1:])  # 从除去猫粮外的其他食物中随机选择
            selected_food ="给米兜加餐{}~".format(c)
    current_date = datetime.now()
    last_period_date = datetime(current_date.year, 2, 20)  # 本月月经日期
    period_cycle = 26  # 月经周期
    # 调用函数计算距离下一次月经的天数
    days_until_next = days_until_next_period(current_date, last_period_date, period_cycle)
    data = {
        "touser": to_user,
        "template_id": config["template_id"],
        "url": "http://wgcyg.cxytx.cn/",
        #"url": "http://weixin.qq.com/download",
        "topcolor": "#FF0000",
        "data": {
            "date": {
                "value": "{} {}".format(today, week),
                "color": '#00FF00'
            },
            "region": {
                "value": "",
            },
            "weather": {
                "value":"",
            },
            "temp": {
                "value": "",
            },
            "wind_dir": {
                "value":"",
            },
            "love_day": {
                "value": love_days,
            },
            "marry_day": {
                "value": marry_days,
            },
            "note_en": {
                "value": "",
            },
            "note_ch": {
                "value": "",
            },
            "max_temp": {
                "value": "",
            },
            "min_temp": {
                "value":"",
            },
            "sunrise": {
                "value":"",
            },
            "sunset": {
                "value": "",
            },
            "category": {
                "value": "",
            },
            "pm2p5": {
                "value":"",
            },
            "proposal": {
                "value": "",
            },
            # "chp": {
            #     "value": "",
            # },
            "marry_day_left": {
                "value":marry_day_left,
            },
            "birthday_left": {
                "value": birthday_left,
            },
            "midou_bir": {
                "value": midou,
            },
            "jiejiari": {
                "value": holiday_name,
            },
            "jie_left": {
                "value":days+1,
            },
            "liangshi": {
                "value": selected_food,
            },
            "liangshi": {
                "value": selected_food,
            },
            "thing2": {
                "value": "鸡爪小盆友~注意保暖哈~".format(weather,min_temp),
            },
            "thing3": {
                "value": "鸡爪猪蹄恋爱{}天,纪念日{}天".format(love_days,love_day_left),
            },"thing7": {
                "value":"{}，米兜{}岁{}天".format(birthday_left,a+1,marry_day_left),
            },"thing10": {
                "value": "离{}还有{}天，{}".format(holiday_name,days+1,selected_food),
            },"thing4": {
                "value": "姨妈大约{}天到达，注意不要误伤友军".format(days_until_next),
            },
        }
    }
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    response = post(url, headers=headers, json=data).json()
    if response["errcode"] == 40037:
        print("推送消息失败，请检查模板id是否正确")
    elif response["errcode"] == 40036:
        print("推送消息失败，请检查模板id是否为空")
    elif response["errcode"] == 40003:
        print("推送消息失败，请检查微信号是否正确")
    elif response["errcode"] == 0:
        print("推送消息成功")
    else:
        print(response)

if __name__ == "__main__":
    try:
        with open("config.txt", encoding="utf-8") as f:
            config = eval(f.read())
    except FileNotFoundError:
        print("推送消息失败，请检查config.txt文件是否与程序位于同一路径")
        os.system("pause")
        sys.exit(1)
    except SyntaxError:
        print("推送消息失败，请检查配置文件格式是否正确")
        os.system("pause")
        sys.exit(1)
    # 获取accessToken
    accessToken = get_access_token()
    # 接收的用户
    users = config["user"]
    # 传入地区获取天气信息
  

    
    #birthday_left=get_birthday_left()
    # 公众号推送消息
    for user in users:
        send_message(user, accessToken)
    os.system("pause")
