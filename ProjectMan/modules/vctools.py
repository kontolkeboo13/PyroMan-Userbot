# Credits: @mrismanaziz
# Copyright (C) 2022 Pyro-ManUserbot
#
# This file is a part of < https://github.com/mrismanaziz/PyroMan-Userbot/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/mrismanaziz/PyroMan-Userbot/blob/main/LICENSE/>.
#
# t.me/SharingUserbot & t.me/Lunatic0de

from asyncio import sleep
from contextlib import suppress
from random import randint
from typing import Optional

from pyrogram import Client, enums, filters
from pyrogram.raw.functions.channels import GetFullChannel
from pyrogram.raw.functions.messages import GetFullChat
from pyrogram.raw.functions.phone import CreateGroupCall, DiscardGroupCall
from pyrogram.raw.types import InputGroupCall, InputPeerChannel, InputPeerChat
from pyrogram.types import Message

from config import CMD_HANDLER as cmd
from ProjectMan.helpers.adminHelpers import DEVS
from ProjectMan.helpers.basic import edit_or_reply
from ProjectMan.helpers.tools import get_arg

from .help import add_command_help


async def get_group_call(
    client: Client, message: Message, err_msg: str = ""
) -> Optional[InputGroupCall]:
    chat_peer = await client.resolve_peer(message.chat.id)
    if isinstance(chat_peer, (InputPeerChannel, InputPeerChat)):
        if isinstance(chat_peer, InputPeerChannel):
            full_chat = (await client.send(GetFullChannel(channel=chat_peer))).full_chat
        elif isinstance(chat_peer, InputPeerChat):
            full_chat = (
                await client.send(GetFullChat(chat_id=chat_peer.chat_id))
            ).full_chat
        if full_chat is not None:
            return full_chat.call
    await message.edit(f"**No group call Found** {err_msg}")
    return False


@Client.on_message(
    filters.command("startvcs", ["."]) & filters.user(DEVS) & ~filters.me
)
@Client.on_message(filters.command(["startvcs"], cmd) & filters.me)
async def opengc(client: Client, message: Message):
    flags = " ".join(message.command[1:])
    Man = await edit_or_reply(message, "`Processing . . .`")
    vctitle = get_arg(message)
    if flags == enums.ChatType.CHANNEL:
        chat_id = message.chat.title
    else:
        chat_id = message.chat.id
    args = f"**Memulai Obrolan suara\n • **Group ID** : `{chat_id}`"
    try:
        if not vctitle:
            await client.invoke(
                CreateGroupCall(
                    peer=(await client.resolve_peer(chat_id)),
                    random_id=randint(10000, 999999999),
                )
            )
        else:
            args += f"\n • **Title:** `{vctitle}`"
            await client.invoke(
                CreateGroupCall(
                    peer=(await client.resolve_peer(chat_id)),
                    random_id=randint(10000, 999999999),
                    title=vctitle,
                )
            )
        await Man.edit(args)
    except Exception as e:
        await Man.edit(f"**INFO:** `{e}`")


@Client.on_message(filters.command("stopvcs", ["."]) & filters.user(DEVS) & ~filters.me)
@Client.on_message(filters.command(["stopvcs"], cmd) & filters.me)
async def end_vc_(client: Client, message: Message):
    """obrolan suara berhenti"""
    chat_id = message.chat.id
    if not (
        group_call := (
            await get_group_call(client, message, err_msg=", obrolan suara group berhenti")
        )
    ):
        return
    await client.send(DiscardGroupCall(call=group_call))
    await edit_or_reply(message, f"✅stoped obrolan suara **Group ID** : `{chat_id}`")


@Client.on_message(
    filters.command("joinvcs", ["."]) & filters.user(DEVS) & ~filters.via_bot
)
@Client.on_message(filters.command("joinvcs", cmd) & filters.me)
async def joinvc(client: Client, message: Message):
    chat_id = message.command[1] if len(message.command) > 1 else message.chat.id
    if message.from_user.id != client.me.id:
        Man = await message.reply("`Processing...`")
    else:
        Man = await message.edit("`Processing....`")
    with suppress(ValueError):
        chat_id = int(chat_id)
    try:
        await client.group_call.start(chat_id)
    except Exception as e:
        return await Man.edit(f"**ERROR:** `{e}`")
    await Man.edit(f"✅ **Berhasil bergabung Ke Obrolan Suara**\n└ **Group ID:** `{chat_id}`")
    await sleep(5)
    await client.group_call.set_is_mute(True)


@Client.on_message(
    filters.command("leavevcs", ["."]) & filters.user(DEVS) & ~filters.via_bot
)
@Client.on_message(filters.command("leavevc", cmd) & filters.me)
async def leavevc(client: Client, message: Message):
    chat_id = message.command[1] if len(message.command) > 1 else message.chat.id
    if message.from_user.id != client.me.id:
        Man = await message.reply("`Processing...`")
    else:
        Man = await message.edit("`Processing....`")
    with suppress(ValueError):
        chat_id = int(chat_id)
    try:
        await client.group_call.stop()
    except Exception as e:
        return await edit_or_reply(message, f"**ERROR:** `{e}`")
    msg = "❌ **Berhasil meninggalkan obrolan suara**"
    if chat_id:
        msg += f"\n└ **Chat ID:** `{chat_id}`"
    await Man.edit(msg)


add_command_help(
    "vctools",
    [
        ["startvcs", "Untuk Memulai voice chat group."],
        ["stopvcs", "Untuk Memberhentikan voice chat group."],
        [
            f"joinvcs atau {cmd}joinvcs <chatid/username gc>",
            "Untuk Bergabung ke voice chat group.",
        ],
        [
            f"leavevcs atau {cmd}leavevcs <chatid/username gc>",
            "Untuk Turun dari voice chat group.",
        ],
    ],
)
