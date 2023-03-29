import json
import os
import re
from typing import Any, Optional, Tuple, Union

from discord import Guild, Interaction, Member, Message, TextChannel, User, Webhook, utils
from pykakasi import kakasi


class BotUtility:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.EMOJI_PATTERN: str = r"<:[0-9|a-z|_]+:[0-9]+>"  # Regex custom emoji

        kks = kakasi()
        kks.setMode("H", "a")
        kks.setMode("K", "a")
        kks.setMode("J", "a")
        self.kksconv = kks.getConverter()

    async def convert_orgmsg(
        self, orgmsg: Union[Interaction, Message]
    ) -> Tuple[Optional[TextChannel], Optional[Union[Member, User]]]:
        """ slash commandかMessageから情報を抽出する """

        # Error handling
        if orgmsg is None:
            return None, None

        # channel
        if type(orgmsg.channel) is not TextChannel:
            return None, None

        channel: TextChannel = orgmsg.channel

        # user
        user: Optional[Union[Member, User]] = None

        if type(orgmsg) is Interaction:
            if orgmsg.user is None:
                return None, None

            user = orgmsg.user

            await orgmsg.response.send_message(orgmsg.namespace)

        if type(orgmsg) is Message:
            if orgmsg.author is None:
                return None, None

            user = orgmsg.author

        # return
        return channel, user

    def get_environvar(self, key: str) -> str:
        """Return environments"""

        if key in os.environ:  # Heroku
            return os.environ[key]
        else:  # Local
            path: str = f'{os.environ["HOME"]}/Dropbox/discord/data/vars.json'
            with open(path) as f:
                vars: dict[str, str] = json.load(f)

            if key in vars:
                return vars[key]
            else:  # Error
                exit(f"Environment variable not found: {path}, {key}")

    def disassemble_content(self, content: str) -> list[str]:
        """文字列を絵文字を考慮しつつリストにする"""

        EMOJI_PATTERN: str = r"<:[0-9|a-z|_]+:[0-9]+>|."  # カスタム絵文字の正規表現 | 任意の文字

        ret: list[str] = [e.group() for e in re.finditer(EMOJI_PATTERN, content)]
        return [e for e in ret if e != " "]

    def limitnchar(self, s: str, nchar: int = 1950) -> str:
        """文字数を制限する"""

        if len(s) > nchar:
            return s[:nchar] + "\n<--- 2000文字以上の文章は捨てた --->"
        else:
            return s

    async def post_subreply(self, guild: Optional[Guild], reply: str) -> None:
        """ Temporaryチャンネルに投稿する """

        # Error handling
        if not guild:
            print("Guild not found")
            return

        channel: Optional[TextChannel] = utils.find(lambda c: c.name == "うんち", guild.text_channels)

        # Error handling
        if not channel:
            print("Temporaryチャンネルが見つかりませんでした")
            return

        data: dict[str, Any] = {"channel": channel, "reply": reply}
        await self.webhook(**data)

    async def webhook(
        self, channel: TextChannel, reply: str, avatar_url: Optional[str] = None, username: Optional[str] = None,
    ) -> None:
        """Post webhook message"""

        # Create webhook data
        data: dict[str, Union[str, TextChannel]] = {
            "content": reply,
        }

        if avatar_url:
            data["avatar_url"] = avatar_url

        if username:
            data["username"] = username

        # Get webhook
        webhooks: list[Webhook] = await channel.webhooks()

        # webhookを1つ拝借
        for w in webhooks:
            if w.token:  # 使えるwebhookがある場合
                webhook: Webhook = w
                break
        else:  # 使えるwebhookがない場合は作成
            webhook: Webhook = await channel.create_webhook(name="unbobo-webhook")

        await webhook.send(**data)
