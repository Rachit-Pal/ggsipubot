import asyncio
import importlib
import re
from contextlib import (
    closing,
    suppress
)
from Rose.utils.lang import *
from uvloop import install
from pyrogram import ( 
    filters, 
    idle
)
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup, 
    Message
)
from Rose import (
    app,
    BOT_USERNAME,
    bot,
    BOT_NAME,
    aiohttpsession
)
from Rose.plugins import ALL_MODULES
from Rose.utils import paginate_modules
from lang import get_command
from Rose.utils.lang import (
    language,
    languageCB
)
from Rose.utils.start import (
    get_private_rules,
    get_learn
)
from Rose.mongo.usersdb import (
    adds_served_user,
    add_served_user
)
from Rose.mongo.chatsdb import add_served_chat
from Rose.plugins.fsub import ForceSub
from config import Config
loop = asyncio.get_event_loop()

flood = {}
HELPABLE = {}

async def start_bot():
    global HELPABLE
    for module in ALL_MODULES:
        imported_module = importlib.import_module("Rose.plugins." + module)
        if (
            hasattr(imported_module, "__MODULE__")
            and imported_module.__MODULE__
        ):
            imported_module.__MODULE__ = imported_module.__MODULE__
            if (
                hasattr(imported_module, "__HELP__")
                and imported_module.__HELP__
            ):
                HELPABLE[
                    imported_module.__MODULE__.replace(" ", "_").lower()
                ] = imported_module
    all_module = ""
    j = 1
    for i in ALL_MODULES:
        if j == 1:
            all_module += "•≫ Successfully imported:{:<15}.py\n".format(i)
            j = 0
        else:
            all_module += "•≫ Successfully imported:{:<15}.py".format(i)
        j += 1   
    print(f"{all_module}")
    print("""
 _____________________________________________   
|                                             |  
|          Deployed Successfully              |  
|         (C) 2021-2022 by @szteambots        | 
|          Greetings from supun  :)           |
|_____________________________________________| """)
    await idle()
    await aiohttpsession.close()
    await app.stop()
    for task in asyncio.all_tasks():
        task.cancel() 
    print("Bot gone offline ):")



home_keyboard_pm = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text=" ➕ Add Me To Your Group ➕ ",
            url=f"http://t.me/{BOT_USERNAME}?startgroup=new")
        ],
        [
            InlineKeyboardButton(text="📃 About", 
            callback_data="_about"),
            InlineKeyboardButton(text="🌐 Website", 
            url=f"http://www.ipu.ac.in/")
        ],
        [
            InlineKeyboardButton(text="🔔 Updates", 
            url=f"https://t.me/StrawHatNetwork"),
            InlineKeyboardButton(text="🚑 Support", 
            url=f"https://t.me/StrawHatTeam")
        ]
        [
            InlineKeyboardButton(text="[► Help ◄]", 
            callback_data="bot_commands")
        ],
    ]
)

keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text="⚙️ Commands & Help", 
            url=f"t.me/{BOT_USERNAME}?start=help")
        ]
    ]
)

@app.on_message(filters.command("start"))
@language
async def start(client, message: Message, _):
    chat_id = message.chat.id
    print(chat_id)
    FSub = await ForceSub(bot, message)
    if FSub == 400:
        return
    if message.chat.type == "private":
        await message.reply_text(_["main2"], reply_markup=keyboard)
        await adds_served_user(message.from_user.id)     
        return await add_served_chat(chat_id) 

    if len(message.text.split()) > 1:
        name = (message.text.split(None, 1)[1]).lower()
        print(name)
        if name.startswith("rules"):
                return await get_private_rules(app, message, name)
        if name.startswith("learn"):
                return await get_learn(app, message, name)
        if "_" in name:
            module = name.split("_", 1)[1]
            text = (_["main6"].format({HELPABLE[module].__MODULE__}
                + HELPABLE[module].__HELP__)
            )
            await message.reply(text, disable_web_page_preview=True)
        if name == "help":
            text, keyb = await help_parser(message.from_user.first_name)
            await message.reply(_["main5"],reply_markup=keyb, disable_web_page_preview=True)
        if name == "connections":
            await message.reply("** Run /connections to view or disconnect from groups!**")
    else:
        await message.reply_text(f"""
Hey there {message.from_user.mention}, 

My name is {BOT_NAME} an  advanced telegram Group management Bot For helpYou Protect Your Groups & Suit For All Your Needs.feel free to add me to your groups! """,reply_markup=home_keyboard_pm)
        return await add_served_user(chat_id) 


fbuttons = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text="🔔 Updates", url="https://t.me/StrawHatNetwork"),
          InlineKeyboardButton(text="🚑 Support", url="https://t.me/StrawHatTeam")], 
        [ InlineKeyboardButton(text="💾 Source Code", url="https://github.com/Rachit-Pal/GGSIPUBOT"),
          InlineKeyboardButton(text="🌐 Website", url="http://www.ipu.ac.in/")], 
        [InlineKeyboardButton(text="👑 Owner", url="https://t.me/SAlTAM4")
        ],[InlineKeyboardButton("🔙 Back", callback_data='startcq')]])

keyboard =InlineKeyboardMarkup(
    [[InlineKeyboardButton(text="🇱🇷 English", callback_data="languages_en")],
     [InlineKeyboardButton(text="🇱🇰 සිංහල", callback_data="languages_si"), 
      InlineKeyboardButton(text="🇮🇳 हिन्दी", callback_data="languages_hi")], 
     [InlineKeyboardButton(text="🇮🇹 Italiano", callback_data="languages_it"), 
      InlineKeyboardButton(text="🇮🇳 తెలుగు", callback_data="languages_ta")], 
     [InlineKeyboardButton(text="🇮🇩 Indonesia", callback_data="languages_id"), 
      InlineKeyboardButton(text="🇦🇪 عربي", callback_data="languages_ar")], 
     [InlineKeyboardButton(text="🇮🇳 മലയാളം", callback_data="languages_ml"), 
      InlineKeyboardButton(text="🇲🇼 Chichewa", callback_data="languages_ny")], 
     [InlineKeyboardButton(text="🇩🇪 German", callback_data="languages_ge"), 
      InlineKeyboardButton(text="🇷🇺 Russian", callback_data="languages_ru")], 
     [InlineKeyboardButton("« Back", callback_data='startcq')]])

@app.on_callback_query(filters.regex("_langs"))
@languageCB
async def commands_callbacc(client, CallbackQuery, _):
    await CallbackQuery.message.edit(
        text= "Choose Your languages:",
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )
    
@app.on_callback_query(filters.regex("_about"))
@languageCB
async def commands_callbacc(client, CallbackQuery, _):
    await CallbackQuery.message.edit(
        text=_["menu"],
        reply_markup=fbuttons,
        disable_web_page_preview=True,
    )
    
@app.on_message(filters.command("help"))
@language
async def help_command(client, message: Message, _):
    if message.chat.type != "private":
        if len(message.command) >= 2:
            name = (message.text.split(None, 1)[1]).replace(" ", "_").lower()
            if str(name) in HELPABLE:
                key = InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text=_["main3"], url=f"t.me/{BOT_USERNAME}?start=help_{name}")]])
                await message.reply_text(_["main4"],reply_markup=key)
            else:
                await message.reply_text(_["main2"], reply_markup=keyboard)
        else:
            await message.reply_text(_["main2"], reply_markup=keyboard)
    else:
        if len(message.command) >= 2:
            name = (message.text.split(None, 1)[1]).replace(" ", "_").lower()
            print(name)
            if str(name) in HELPABLE:
                text = (_["main6"].format({HELPABLE[name].__MODULE__}
                + HELPABLE[name].__HELP__))
                if hasattr(HELPABLE[name], "__helpbtns__"):
                       button = (HELPABLE[name].__helpbtns__) + [[InlineKeyboardButton("Back", callback_data="bot_commands")]]
                if not hasattr(HELPABLE[name], "__helpbtns__"): button = [[InlineKeyboardButton("Back", callback_data="bot_commands")]]
                await message.reply_text(text,reply_markup=InlineKeyboardMarkup(button),disable_web_page_preview=True)
            else:
                text, help_keyboard = await help_parser(message.from_user.first_name)
                await message.reply_text(_["main5"],reply_markup=help_keyboard,disable_web_page_preview=True)
        else:
            text, help_keyboard = await help_parser(message.from_user.first_name)
            await message.reply_text(
                text, reply_markup=help_keyboard, disable_web_page_preview=True
            )
    return
  
@app.on_callback_query(filters.regex("startcq"))
@languageCB
async def startcq(client,CallbackQuery, _):
    await CallbackQuery.message.edit(
        text=f"""
────「 [IPU Assistant](https://telegra.ph/file/cfe86b1cbc66ab7476a66.jpg) 」────
Hey there {CallbackQuery.from_user.mention}, 
I am IPU Assistant, an advanced telegram group management bot to help you protect your groups and suit all your needs. Feel free to add me to your groups! """,
        disable_web_page_preview=True,
        reply_markup=home_keyboard_pm)


async def help_parser(name, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    return (
"""
**Welcome to Help Menu**

I'm a group management bot with some useful features.
You can choose an option below, by clicking a button.

🎛 *Main commands available:*
 • /start: Starts me, can be used to check I'm alive or not.
 • /help <module name>: PM's you this message.
 • /settings:
   - in PM: will send you your settings for all supported modules.
   - in a group: will redirect you to pm, with all that chat's settings.
   
**All commands can be used with the following: / **""",keyboard)


@app.on_callback_query(filters.regex("bot_commands"))
@languageCB
async def commands_callbacc(client,CallbackQuery, _):

    text ,keyboard = await help_parser(CallbackQuery.from_user.mention)

    await CallbackQuery.message.edit(text=_["main5"],reply_markup=keyboard,disable_web_page_preview=True)


@app.on_callback_query(filters.regex(r"help_(.*?)"))
@languageCB
async def help_button(client, query, _):

    home_match = re.match(r"help_home\((.+?)\)", query.data)
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)
    create_match = re.match(r"help_create", query.data)

    top_text = _["main5"]

    if mod_match:

        module = (mod_match.group(1)).replace(" ", "_")

        text = (
            "{} **{}**:\n".format(
                "Here is the help for", HELPABLE[module].__MODULE__
            )
            + HELPABLE[module].__HELP__)

        if hasattr(HELPABLE[module], "__helpbtns__"):
                       button = (HELPABLE[module].__helpbtns__) + [[InlineKeyboardButton("Back", callback_data="bot_commands")]]

        if not hasattr(HELPABLE[module], "__helpbtns__"): button = [[InlineKeyboardButton("Back", callback_data="bot_commands")]]

        await query.message.edit(text=text,reply_markup=InlineKeyboardMarkup(button),disable_web_page_preview=True,)

    elif home_match:
        await query.message.edit(query.from_user.id,text= _["main2"],reply_markup=home_keyboard_pm)

    elif prev_match:
        curr_page = int(prev_match.group(1))

        await query.message.edit(text=top_text,reply_markup=InlineKeyboardMarkup(paginate_modules(curr_page - 1, HELPABLE, "help")),disable_web_page_preview=True)

    elif next_match:
        next_page = int(next_match.group(1))

        await query.message.edit(text=top_text,reply_markup=InlineKeyboardMarkup(paginate_modules(next_page + 1, HELPABLE, "help")),disable_web_page_preview=True)

    elif back_match:
        await query.message.edit(text=top_text,reply_markup=InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help")),disable_web_page_preview=True)

    elif create_match:
        text, keyboard = await help_parser(query)

        await query.message.edit(text=text,reply_markup=keyboard,disable_web_page_preview=True)

    return await client.answer_callback_query(query.id)



if __name__ == "__main__":

    install()

    with closing(loop):

        with suppress(asyncio.exceptions.CancelledError):
            loop.run_until_complete(start_bot())

        loop.run_until_complete(asyncio.sleep(1.0)) 
