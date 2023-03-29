import json
import os
import platform
import random as ra
import re
from datetime import datetime as dt
from typing import Any, Optional

import requests
from discord import Emoji, Member, Message, TextChannel, utils
from pandas_datareader.data import get_quote_yahoo

import commands
from botutility import BotUtility
from mydropbox import MyDropbox


class Action(BotUtility, MyDropbox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.PATTERNS: dict[str, str] = {
            "calc": r".*=$",
            "dice": r"^(?!http).*(\d+)d(\d+)",
            "kaiji": f"^{self.EMOJI_PATTERN}.*",
            "kawase": r"\$\d+(?:\.\d+)?",
            "slash_command": r"^/.*",
            "tenki": r"\$tenki",
            "uname": r"\$uname",
        }

        self.WEATHERS: dict[str, str] = {
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

    async def calc(self, message: Message) -> None:
        """仕方ないから代わりに計算してあげます"""

        reply: str = eval(message.content[:-1])  # remove '='

        await message.channel.send(reply)

    async def dice(self, message: Message) -> None:
        """賽は投げられた"""
        refa: list[Any] = re.findall(self.PATTERNS["dice"], message.content)

        if refa:
            n: int
            me: int
            n, me = map(int, refa[0])

            if n is None or me is None:
                print(refa)
                await message.channel.send("えっろｒ")
                return
        else:
            print(refa)
            await message.channel.send("えっろｒ")
            return

        dice = [ra.randrange(me) + 1 for i in range(n)]  # dices
        sum_ = f"(sum: {sum(dice)})" if len(dice) >= 2 else ""  # 合計

        reply: str = f'{", ".join(map(str, dice))} {sum_}'
        await message.channel.send(reply)

    async def kaiji(self, message: Message) -> None:
        """床゛が゛キ゛ン゛キ゛ン゛に゛冷゛え゛て゛や゛が゛る゛よ゛～゛！゛"""

        # Error handling
        if message.webhook_id:
            await message.channel.send("webhookのときは使えないよ")
            return

        if message.guild is None:
            await message.channel.send("サーバーに入ってないと使えないよ")
            return

        if type(message.channel) is not TextChannel:
            await message.channel.send("テキストチャンネルでないと使えないよ")
            return

        li: list[str] = self.disassemble_content(message.content)
        emoji: Optional[Emoji] = utils.find(lambda e: str(e.id) in li[0], message.guild.emojis)

        # Error handling
        if emoji is None:
            await message.channel.send("エモジがないよ")
            return

        THRESHOLD_HEART: float = 0.5
        tail_s: str = self.kksconv.do(li[-1])[-1]
        shiin: dict[str, str] = {"a": "ぁ", "i": "ぃ", "u": "ぅ", "e": "ぇ", "o": "ぉ"}

        li = li[1:] + [shiin[tail_s] if tail_s in shiin else "ッ"] * ra.randrange(1, 10)
        li = li + ["ッ"] * ra.randrange(5, 15)
        reply: str = "゛".join(li)
        reply += ("！" if THRESHOLD_HEART < ra.random() else "♡") * ra.randrange(5, 15)

        data: dict[str, Any] = {
            "channel": message.channel,
            "reply": reply,
            "avatar_url": emoji.url,
            "username": message.author.display_name,
        }

        await self.webhook(**data)

    async def kawase(self, message: Message) -> None:
        """円安つらい"""

        # Get exchange rate
        result = get_quote_yahoo("JPY=X")
        rate: float = float(result["price"].values[0])

        doll_list: list[str] = re.findall(self.PATTERNS["kawase"], message.content)

        reply: str = message.content
        for s in doll_list:
            reply = reply.replace(s, f"{int(float(s[1:]) * rate)}円")

        await message.channel.send(reply)

    async def slash_command(self, message: Message) -> None:
        """スラコマきらい"""

        cmd, *args = message.content.split()
        if (cmd := cmd[1:]) in dir(commands):  # Command() function list
            print(cmd, args)
            await eval(f"commands.{cmd}(message, {args})")

    async def tenki(self, message: Message) -> None:
        """貴島明日香"""

        if message.guild is None:
            return

        for user in message.guild.members:
            member: Optional[Member] = message.guild.get_member(user.id)
            if member is None:
                continue

            nick: str = member.display_name

            # Error handling
            if user.bot:
                continue

            try:
                await member.edit(nick=member.display_name)
            except Exception as e:
                print(e.args)
                continue

            # Get tenki
            pf: Optional[dict[str, dict[str, str]]] = self.get_profile()

            city: str = pf[user.name]["locate"]  # type: ignore
            key: str = self.get_environvar("KEY_OPENWEATHER")
            url: str = f"http://api.openweathermap.org/data/2.5/forecast?units=metric&q={city}&APPID={key}"
            data: dict = json.loads(requests.get(url).text)

            # Forecast icons
            ficon: list[str] = [self.WEATHERS[li["weather"][0]["icon"][:-1]] for li in data["list"]]

            # Change nick
            nick_ = ""
            for i, _ in enumerate(nick):
                if nick[i] in self.WEATHERS.values():
                    nick_ += ficon.pop(0)
                else:
                    nick_ += nick[i]

            await member.edit(nick=nick_)
            await message.channel.send(f"{nick_}: {city}")

    async def uname(self, message: Message) -> None:
        """その目だれの目？"""

        reply: str = "----\n"

        # update time
        update: str = str(dt.fromtimestamp(os.path.getmtime(os.path.abspath(__file__))))
        reply += f"Update: {update}\n\n"

        for k, v in platform.uname()._asdict().items():
            reply += f"{k}: {v}\n"

        await message.channel.send(reply)
