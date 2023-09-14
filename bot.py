#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os

import sys
import telepot
import time
from telepot.loop import MessageLoop

def save_status(obj):
    with open('chats.json', 'w') as f:
        f.write(json.dumps(obj))

def save_allowed(s):
    with open('allowed.json', 'w') as f:
        f.write(json.dumps(list(s)))

if not os.path.isfile('chats.json'):
    save_status({})

if not os.path.isfile('allowed.json'):
    save_allowed(set())

chats = {}
allowed = []
TOKEN = "6612623803:AAH2qlJdAHYAbiECR3E6wsnLd6zsD8YqebY"
PASSWORD = "arnetsmg"

with open('chats.json', 'r') as f:
    chats = json.load(f)

with open('allowed.json', 'r') as f:
    allowed = set(json.load(f))

if os.path.isfile('config.json'):
    with open('config.json', 'r') as f:
        config = json.load(f)
        if config['token'] == "":
            sys.exit("No token defined. Define it in a file called token.txt.")
        if config['password'] == "":
            print("WARNING: Empty Password for registering to use the bot." +
                  " It could be dangerous, because anybody could use this bot" +
                  " and forward messages to the channels associated to it")
        TOKEN = config['token']
        PASSWORD = config['password']
else:
    sys.exit("No config file found. Remember changing the name of config-sample.json to config.json")

def is_allowed(msg):
    if msg['chat']['type'] == 'channel':
        return True #all channel admins are allowed to use the bot (channels don't have sender info)
    return 'from' in msg and msg['from']['id'] in allowed

def handle(msg):
    print("Message: " + str(msg))
    # Add person as allowed
    content_type, chat_type, chat_id = telepot.glance(msg)
    txt = ""
    if 'text' in msg:
        txt = txt + msg['text']
    elif 'caption' in msg:
        txt = txt + msg['caption']
    # Addme and rmme only valid on groups and personal chats.
    if msg['chat']['type'] != 'channel':
        if "/addme" == txt.strip()[:6]:
            if msg['chat']['type'] != 'private':
                bot.sendMessage(chat_id, "Perintah ini hanya digunakan di chat personal dengan BOT.")
            else:
                used_password = " ".join(txt.strip().split(" ")[1:])
                if used_password == PASSWORD:
                    allowed.add(msg['from']['id'])
                    save_allowed(allowed)
                    bot.sendMessage(chat_id, msg['from']['first_name'] + ", anda telah terdaftar " +
                                    "sebagai pengguna resmi BOT ini.")
                else:
                    bot.sendMessage(chat_id, "Password Salah")
        if "/rmme" == txt.strip()[:5]:
            allowed.remove(msg['from']['id'])
            save_allowed(allowed)
            bot.sendMessage(chat_id, "Status Resmi Anda untuk menggunakan Bot ini telah kami hilangkan.")
    if is_allowed(msg):
        if txt != "":
            if "/add_tag " == txt[:5]:
                txt_split = txt.strip().split(" ")
                if len(txt_split) == 2 and "#" == txt_split[1][0]:
                    tag = txt_split[1].lower()
                    name = ""
                    if msg['chat']['type'] == "private":
                        name = name + "Personal chat dengan " + msg['chat']['first_name'] + ((" " + msg['chat']['last_name']) if 'last_name' in msg['chat'] else "")
                    else:
                        name = msg['chat']['title']
                    chats[tag] = {'id': chat_id, 'name': name}
                    bot.sendMessage(chat_id, name + " ditambahkan dengan tag " + tag)
                    save_status(chats)
                else:
                    bot.sendMessage(chat_id, "Format SALAH. Format seharusnya _/add #{tag}_", parse_mode="Markdown")
            elif "/remove_tag " == txt[:4]:
                txt_split = txt.strip().split(" ")
                if len(txt_split) == 2 and "#" == txt_split[1][0]:
                    tag = txt_split[1].lower()
                    if tag in chats:
                        if chats[tag]['id'] == chat_id:
                            del chats[tag]
                            bot.sendMessage(chat_id, "Tag "+tag+" hapus dari Taglist.")
                            save_status(chats)
                            return
                        else:
                            bot.sendMessage(chat_id, "Kamu tidak dapat menghapus tag milik suatu chat dari chat yang berbeda.")
                    else:
                        bot.sendMessage(chat_id, "Tag tidak ada dalam TagList")
                else:
                    bot.sendMessage(chat_id, "Format SALAH. Format seharusnya _/rm #{tag}_", parse_mode="Markdown")

            elif "/taglist" ==  txt.strip()[:8]:
                tags_names = []
                for tag, chat in chats.items():
                    tags_names.append( (tag, chat['name']))
                response = "<b>TagList</b>"
                for (tag, name) in sorted(tags_names):
                    response = response + "\n<b>" + tag + "</b>: <i>" + name + "</i>"
                bot.sendMessage(chat_id, response, parse_mode="HTML")
            elif "#" == txt[0]:
                txt_split =txt.strip().split(" ")
                i = 0
                tags = []
                while i < len(txt_split) and txt_split[i][0] == "#":
                    tags.append(txt_split[i].lower())
                    i+=1
                if i != len(txt_split) or 'reply_to_message' in msg:
                    approved = []
                    rejected = []
                    for tag in tags:
                        if tag in chats:
                            if chats[tag]['id'] != chat_id:
                                approved.append(chats[tag]['name'])
                                bot.forwardMessage(chats[tag]['id'], chat_id, msg['message_id'])
                                print ("chat id dest : ",chats[tag]['id'])
                                bot.sendMessage(chats[tag]['id'], "<i>Pesan Laporan ini sudah diketahui oleh PIC NETAR & IS OP Witel SMG\nKetik /info untuk informasi lebih lanjut</i>",parse_mode="HTML")
                                if 'reply_to_message' in msg:
                                    bot.forwardMessage(chats[tag]['id'], chat_id, msg['reply_to_message']['message_id'])
                        else:
                            rejected.append(tag)
                    if len(rejected) > 0:
                        bot.sendMessage(chat_id, "GAGAL mengirim pesan ke tag <i>" + ", ".join(rejected) + "</i>", parse_mode="HTML")
                else:
                    bot.sendMessage(chat_id, "Gagal mengirim pesan hanya dengan tag yang bukan merupakan balasan pesan lain")

            elif "/info" == txt.strip()[:5]:
                bot.sendMessage(chat_id, "Selamat datang di LAPOR NDAN yang merupakan salah satu tool telegram grup NETAR & IS OP Witel SMG " + 
                                        "untuk melakukan auto forward suatu pesan dari grup NETAR & IS OP Witel SMG ke grup maupun channel yang dituju secara selektif dengan menggunakan hashtag tertentu, fitur yang kami sediakan meliputi :\n\n" + 
                                        "1. /info , untuk melihat fitur yang ada \n" +
                                        "2. /add_tag , untuk menambahkan tag, satu kata tag hanya dapat terintegrasi ke satu grup atau channel \n" + 
                                        "3. /remove_tag , untuk menghapus tag yang terintegrasi ke grup tertentu \n" +
                                        "4. /taglist, untuk melihat semua tag yang terintegrasi ke grup tertentu \n\n" +
                                        "Jika masih butuh info lebih lanjut harap hubungi @najarmu, Terima Kasih", parse_mode="HTML")

bot = telepot.Bot(TOKEN)

MessageLoop(bot, handle).run_as_thread()
print('Listening ...')
# Keep the program running.
while 1:
    time.sleep(10)
