import json
import random as ra
import re
import string

# import subprocess
from datetime import datetime
from typing import Any, Literal, Optional, Union
from urllib.parse import unquote

import requests
import wikipedia
from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag
from discord import Embed, Interaction, Member, Message, TextChannel, User
from googlemaps import Client
from requests import Response
from wikipedia.exceptions import DisambiguationError, PageError

import config as cfg


async def atcoder(orgmsg: Union[Interaction, Message], *args) -> None:
    channel, user = await cfg.botutil.convert_orgmsg(orgmsg)
    if channel is None or user is None:
        return

    # Scrape
    BASELINK: str = "https://atcoder.jp"
    bs: BeautifulSoup = BeautifulSoup(requests.get(f"{BASELINK}/contests").content, "lxml")

    # Extract contest list
    div: Optional[Union[Tag, NavigableString]] = bs.find(id="contest-table-upcoming")
    if type(div) is not Tag:
        return

    # Create embed
    embed: Embed = Embed(title="Upcoming contests", description="", color=0xA79FA7)
    for tr_ in div.find_all("tr")[1:]:
        td_ = tr_.find_all("td")

        start_time: str = td_[0].text
        link: str = f"{BASELINK}{td_[1].a.get('href')}"
        contest_name: str = td_[1].a.text
        # duration: str = td_[2].text
        rated_range: str = td_[3].text

        value: str = f"{start_time}\n"
        value += f"Rated range: {rated_range}\n"
        value += f"{link}"

        embed.add_field(name=contest_name, value=value, inline=False)

    # Post
    await channel.send(embed=embed)


async def color(orgmsg: Union[Interaction, Message], query_: str, *args) -> None:
    channel, user = await cfg.botutil.convert_orgmsg(orgmsg)
    if channel is None or user is None:
        return

    # カラーコードか判定
    if re.match(r"^(#)?([0-9a-fA-F]{6})$", query_):
        reply: str = f"https://www.color-site.com/images/{query_[-6:]}.jpg"
    else:
        query: str = query_.replace(" ", "+")
        reply: str = f"https://alexbeals.com/projects/colorize/search.php?q={query}"

    # Post
    await channel.send(reply)


async def echo(orgmsg: Union[Interaction, Message], text: str, *args) -> None:
    channel, user = await cfg.botutil.convert_orgmsg(orgmsg)
    if channel is None or user is None:
        return

    if not orgmsg.guild:
        return

    reply: str = text
    member: Optional[Member] = ra.choice(orgmsg.guild.members)

    # Post
    data: dict[str, Any] = {
        "channel": channel,
        "reply": reply,
        "avatar_url": str(member.avatar),
        "username": member.display_name,
    }

    await cfg.botutil.webhook(**data)


async def hdmi(orgmsg: Union[Interaction, Message], query_: str = "", *args) -> None:
    channel, user = await cfg.botutil.convert_orgmsg(orgmsg)
    if channel is None or user is None:
        return

    wikipedia.set_lang("ja")

    # SET query
    if query_ == "":
        query_ = "".join([ra.choice(string.ascii_uppercase) for _ in range(4)])

    # GET sammary
    try:
        word: str = wikipedia.search(query_, results=1)[0]
        summary: str = wikipedia.summary(word)
    except (PageError, IndexError) as e:
        word: str = "佐井村"
        summary: str = wikipedia.summary(word)
        print(e)
    except DisambiguationError as e:
        word: str = e.options[0]
        summary: str = wikipedia.summary(word)

        reply: str = f"DisambiguationPage: {e.options}"
        await channel.send(reply)

    # Post
    reply: str = (f"俺...{query_}かもしれん...\n" f"{summary}")
    await channel.send(cfg.botutil.limitnchar(reply))

    reply: str = unquote(wikipedia.page(word).url)
    await cfg.botutil.post_subreply(orgmsg.guild, reply)


async def neko(orgmsg: Union[Interaction, Message], *args) -> None:
    channel, user = await cfg.botutil.convert_orgmsg(orgmsg)
    if channel is None or user is None:
        return

    await channel.send("にゃーん")


async def omikuji(orgmsg: Union[Interaction, Message], *args) -> None:
    channel, user = await cfg.botutil.convert_orgmsg(orgmsg)
    if channel is None or user is None:
        return

    result: str = ra.choice(["大吉", "中吉", "吉", "小吉", "末吉", "凶", "大凶"])

    await channel.send(result)


async def pic(orgmsg: Union[Interaction, Message], channel_: Optional[TextChannel], *args) -> None:
    channel, user = await cfg.botutil.convert_orgmsg(orgmsg)
    if channel is None or user is None:
        return

    path: str = "/discord/log/_attachments.json"
    df: dict[str, str] = cfg.mydbx.read_json(path)  # type: ignore

    # create attachments list
    if channel_:  # attachments in channel only
        cname: str = channel_.name

        # Prune attachments list
        dfv: list[dict] = []
        for dfv_ in df.values():  # type: ignore
            if cname == dfv_["channel"]["name"]:  # type: ignore
                dfv.append(dfv_)  # type: ignore
    else:  # all attachments
        dfv: list[dict] = [dfv_ for dfv_ in df.values()]  # type: ignore

    # Pick attachment
    if dfv:
        pick_message: dict = ra.choice(dfv)
    else:
        await channel.send("No attachments")
        return

    # Post
    reply: str = (
        f"【{pick_message['channel']['name']}】 {pick_message['created_at']} \n" f"{pick_message['attachments']['url']}"
    )
    data: dict[str, Any] = {
        "channel": channel,
        "reply": reply,
        "avatar_url": pick_message["author"]["avatar"],
        "username": pick_message["author"]["display_name"],
    }

    await cfg.botutil.webhook(**data)


async def pin(
    orgmsg: Union[Interaction, Message],
    channel_: Optional[TextChannel],
    mode: Optional[Literal["All", "Meigen"]] = "All",
    *args,
) -> None:

    channel, user = await cfg.botutil.convert_orgmsg(orgmsg)
    if channel is None or user is None:
        return

    if orgmsg.guild is None:
        return

    if channel_:  # Only channel
        pins: list[Message] = await channel_.pins()
    else:  # All channel
        pins: list[Message] = cfg.myclient.pins

    # Extract meigen
    if mode == "Meigen":
        pins_ = []
        for p in pins:
            # not content
            if not p.content:
                continue

            # attachments
            if p.attachments:
                continue

            # url
            if re.match(r"^http", p.content):
                continue

            # code
            if "```" in p.content:
                continue

            pins_.append(p)

        pins = pins_

    # Pick pin message
    if pins:
        m: Message = ra.choice(pins)
    else:
        await channel.send("ピンが見つかりませんでした")
        return

    # Post
    reply: str = f"{m.content if m.content else ''}\n"
    reply += f"{m.attachments[0].url if m.attachments else ''}"

    data: dict[str, Any] = {
        "channel": channel,
        "reply": reply,
        "avatar_url": str(m.author.avatar),
        "username": m.author.display_name,
    }

    await cfg.botutil.webhook(**data)

    reply: str = m.jump_url
    await cfg.botutil.post_subreply(orgmsg.guild, reply)


async def shojin(orgmsg: Union[Interaction, Message], user_: str, lower: int, upper: int, *args) -> None:
    channel, user = await cfg.botutil.convert_orgmsg(orgmsg)
    if channel is None or user is None:
        return

    url: str = f"https://script.google.com/macros/s/AKfycby5PvFQAa4W8m812NVFcjx1sQGKPQ2QUnFr1RLtL7I-JczdDrq_5XvnTJoJIGQtbco0/exec?user={user_}&lower={lower}&upper={upper}"
    response = requests.get(url)
    json_ = response.json()
    print(json_)

    if json_["error"]["code"] != 0:
        reply: str = "Error"

    task_id: str = ra.choice(list(json_["data"]["tasks"].keys()))
    task = json_["data"]["tasks"][task_id]

    reply: str = f"{user_}: {json_['data']['rating']}\n"
    reply += f"問題：{task['task']}\n"
    reply += f"Difficulty：{task['difficulty']}\n"
    reply += task["url"]

    await channel.send(reply)


async def slot(orgmsg: Union[Interaction, Message], choices: Union[str, list[str]], *args) -> None:
    channel, user = await cfg.botutil.convert_orgmsg(orgmsg)
    if channel is None or user is None:
        return

    li: Union[str, list[str]] = choices
    if type(choices) is str:
        li = choices.split()

    # Post
    reply: str = ra.choice(li)
    await channel.send(reply)


async def tenki(orgmsg: Union[Interaction, Message], query_: Optional[str], *args) -> None:
    channel, user = await cfg.botutil.convert_orgmsg(orgmsg)
    if channel is None or user is None:
        return

    BASELINK: str = "https://api.openweathermap.org/data/2.5/weather/"
    key: str = cfg.botutil.get_environvar("KEY_OPENWEATHER")
    tenkilist: dict[str, str] = {
        "01": "☀",
        "02": "☀",
        "03": "⛅",
        "04": "☁",
        "09": "🌧",
        "10": "☔",
        "11": "🌩",
        "13": "❄",
        "50": "🌫",
        "other": "💩",
    }

    if query_:
        gapikey: str = cfg.botutil.get_environvar("GOOGLEAPIKEY")
        gmaps: Client = Client(key=gapikey)

        if gcode := gmaps.geocode(query_):  # type: ignore
            lat: float = gcode[0]["geometry"]["location"]["lat"]
            lon: float = gcode[0]["geometry"]["location"]["lng"]
            address: str = f'({gcode[0]["formatted_address"]})'
        else:
            await channel.send("そんな村はない")
            return

        params: str = f"?lang=ja&units=metric&lat={lat}&lon={lon}&appid={key}"
        url: str = f"{BASELINK}{params}"
    else:
        pf: Optional[dict[str, dict[str, str]]] = cfg.mydbx.get_profile()
        if pf is None:
            return

        city: str = pf[user.name]["locate"]

        params: str = f"?lang=ja&units=metric&q={city}&APPID={key}"
        url: str = f"{BASELINK}{params}"

        address: str = ""

    response = requests.get(url)
    data: dict[str, Union[float, str]] = json.loads(response.text)

    iconid: str = data["weather"][0]["icon"]  # type: ignore
    icon: str = tenkilist[iconid[:-1]]

    feels_like: str = str(data["main"]["feels_like"])  # type: ignore
    f1: float = 0.81 * float(data["main"]["feels_like"])  # type: ignore
    f2: float = 0.01 * float(data["main"]["humidity"])  # type: ignore
    f3: float = (0.99 * float(data["main"]["temp"] - 14.3))  # type: ignore
    fukai: float = f1 + f2 + f3 + 46.3
    sunrise: float = data["sys"]["sunrise"]  # type: ignore
    sunset: float = data["sys"]["sunset"]  # type: ignore
    ssunrise: str = datetime.fromtimestamp(sunrise).strftime("%T")
    ssunset: str = datetime.fromtimestamp(sunset).strftime("%T")

    reply: str = f'{datetime.fromtimestamp(data["dt"]).strftime("%T")} \n'  # type: ignore
    reply += f'都市：{data["name"]} {address} \n'
    reply += f'天気：{icon}{data["weather"][0]["description"]} \n'  # type: ignore
    reply += f'温度：{data["main"]["temp"]}℃ （体感：{feels_like}℃）\n'  # type: ignore
    reply += f'湿度：{data["main"]["humidity"]}% \n'  # type: ignore
    reply += f"不快：{fukai:.2f} \n"
    reply += f'風速：{data["wind"]["speed"]}m/s \n'  # type: ignore
    reply += f'気圧：{data["main"]["pressure"]}hPa \n'  # type: ignore
    reply += f'雲量：{data["clouds"]["all"]}% \n'  # type: ignore
    reply += f"日出：{ssunrise} \n"
    reply += f"日没：{ssunset}"

    # Post
    await channel.send(reply)


async def translate(
    orgmsg: Union[Interaction, Message], text: str, from_: Literal["EN", "JA"], to_: Literal["EN", "JA"], *args
) -> None:
    channel, user = await cfg.botutil.convert_orgmsg(orgmsg)
    if channel is None or user is None:
        return

    key: str = cfg.botutil.get_environvar("DEEPLAPIKEY")
    url = "https://api-free.deepl.com/v2/translate"
    headers = {"Authorization": f"DeepL-Auth-Key {key}"}
    data = {"text": text, "source_lang": from_, "target_lang": to_}

    response = requests.post(url, headers=headers, data=data)

    reply: str = response.json()["translations"][0]["text"]

    await channel.send(reply)


async def uranai(orgmsg: Union[Interaction, Message], *args) -> None:
    channel, user = await cfg.botutil.convert_orgmsg(orgmsg)
    if channel is None or user is None:
        return

    date: str = datetime.today().strftime("%Y/%m/%d")
    res: Response = requests.get(url=f"http://api.jugemkey.jp/api/horoscope/free/{date}")
    pf: Optional[dict[str, dict[str, str]]] = cfg.mydbx.get_profile()
    seiza_id: str = pf[user.name]["seiza_id"]  # type: ignore
    j: dict[str, Any] = res.json()["horoscope"][date][seiza_id]

    reply: str = f'【{user.display_name}さんの今日の運勢（{j["sign"]}）】\n'
    reply += f'{j["content"]}\n'
    reply += f'ラッキーアイテム：{j["item"]}\n'
    reply += f'ラッキーカラー：{j["color"]}\n'
    reply += f'{j["rank"]}位\n'
    reply += f'全体運：{"⭐️" * int(j["total"])}\n'
    reply += f'金　運：{"⭐️" * int(j["money"])}\n'
    reply += f'仕事運：{"⭐️" * int(j["job"])}\n'
    reply += f'恋愛運：{"⭐️" * int(j["love"])}\n'

    # Post
    await channel.send(reply)
