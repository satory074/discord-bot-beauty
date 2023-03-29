from typing import Literal, Optional

from discord import Interaction, TextChannel
from discord.app_commands import describe

import commands as cmd
import config as cfg


@cfg.myclient.tree.command()
async def atcoder(ctx: Interaction) -> None:
    """I am tourist."""

    await cmd.atcoder(ctx)


@cfg.myclient.tree.command()
@describe(query_="カラーコードか単語")
async def color(ctx: Interaction, query_: str) -> None:
    """色"""

    await cmd.color(ctx, query_)


@cfg.myclient.tree.command()
@describe(text="何をしゃべらす？")
async def echo(ctx: Interaction, text: str) -> None:
    """誰かになりきる"""

    await cmd.echo(ctx, text)


@cfg.myclient.tree.command()
@describe(query_="検索単語")
async def hdmi(ctx: Interaction, query_: str = "") -> None:
    """俺...HDMIかもしれん..."""

    await cmd.hdmi(ctx, query_)


@cfg.myclient.tree.command()
async def neko(ctx: Interaction) -> None:
    """すべてはここから始まった"""

    await cmd.neko(ctx)


@cfg.myclient.tree.command()
async def omikuji(ctx: Interaction) -> None:
    """今日の運勢"""

    await cmd.omikuji(ctx)


@cfg.myclient.tree.command()
@describe(channel_="チャンネルの指定")
async def pic(ctx: Interaction, channel_: Optional[TextChannel]) -> None:
    """過去を振り返る"""

    await cmd.pic(ctx, channel_)


@cfg.myclient.tree.command()
@describe(channel_="チャンネルの指定")
@describe(mode="名言")
async def pin(
    ctx: Interaction, channel_: Optional[TextChannel], mode: Optional[Literal["All", "Meigen"]] = "All",
) -> None:
    """さらし首"""

    await cmd.pin(ctx, channel_, mode)


@cfg.myclient.tree.command()
@describe(user_="ユーザ名")
@describe(lower="相対レート（下限）")
@describe(upper="相対レート（上限）")
async def shojin(ctx: Interaction, user_: str, lower: int, upper: int) -> None:
    """AtCoder"""

    await cmd.shojin(ctx, user_, lower, upper)


@cfg.myclient.tree.command()
@describe(choices="選択肢")
async def slot(ctx: Interaction, choices: str) -> None:
    """運命をUnbobotに委ねる"""

    await cmd.slot(ctx, choices)


@cfg.myclient.tree.command()
@describe(query_="どこの村の天気を知りたい？")
async def tenki(ctx: Interaction, query_: Optional[str]) -> None:
    """早速呼びかけてみましょう。木原さーん！そらジロー！"""

    await cmd.tenki(ctx, query_)


@cfg.myclient.tree.command()
@describe(text="翻訳する文章")
async def translate(ctx: Interaction, text: str, from_: Literal["EN", "JA"], to_: Literal["EN", "JA"]) -> None:
    """I love factory !!!"""

    await cmd.translate(ctx, text, from_, to_)


@cfg.myclient.tree.command()
async def uranai(ctx: Interaction) -> None:
    """今日のたなくじ"""

    await cmd.uranai(ctx)
