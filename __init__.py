from nonebot import require
from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata

from .config import Config

from random import randint
from nonebot import on_command
from nonebot import on_message
from nonebot import on_notice

from nonebot.rule import to_me
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.exception import MatcherException
import os.path

from nonebot.adapters.onebot.v11 import Message, MessageSegment, Bot, Event
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.permission import SUPERUSER

import hashlib

#require("requests")
from pip._vendor import requests
# from nonebot.drivers import aiohttp

import zipfile
from zipfile import BadZipFile

import os
import zipfile
import aiohttp
import asyncio
import random

__plugin_meta__ = PluginMetadata(
    name="nonebot_plugin_statman",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)


current_directory = os.path.dirname(os.path.abspath(__file__))
stat_directory = os.path.join(current_directory, 'stat')
reply_directory = os.path.join(current_directory, 'replies')
csv_path = os.path.join(current_directory, 'main.csv')

async def download_file(session, url, filename):
    print(f'正在下载 {url} 到 {filename}')
    async with session.get(url, ssl=False) as response:
        if response.status == 200:
            with open(filename, 'wb') as f:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    f.write(chunk)
            print(f'文件已下载并保存为 {filename}')
        else:
            print(f'下载失败，HTTP 状态码：{response.status}')
            return False
    return True

def unzip_file(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print(f"解压完成到 {extract_to}")

def check_files(directory):
    """List files in directory"""
    for root, dirs, files in os.walk(directory):
        for file in files:
            print(f"Found file: {file}")
        for dir in dirs:
            print(f"Found directory: {dir}")

def load_reply(file_path):
    reply_path = os.path.join(reply_directory, file_path)

    fileTemp = open(reply_path, mode='r', buffering=-1, encoding="utf-8")
    result = fileTemp.read()
    fileTemp.close()
    return result

def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


#   please note that if you installed the internal plugin "single_session",
# the notice will be blocked by that thing, and will hence FAIL.
readFile = on_notice(priority=3, block=False)
@readFile.handle()
async def handle_upload(bot: Bot, event: Event):
    print("On Notice:"+str(event)+"\n")
    if event.get_event_name() == "notice.group_upload":
        newFile = event.file
        if newFile.size <= 3000000 :    # 3MB
            basepath = f"./data/{__plugin_meta__.name}/{event.user_id}/{newFile.name}"
            if newFile.name.endswith(".zip"):
                basepath = f"./data/{__plugin_meta__.name}/{event.user_id}/{newFile.name[:-4]}"  # Remove '.zip' and create a directory
            
            if not os.path.exists(basepath):
                os.makedirs(basepath)

            at_heading = MessageSegment.at(event.user_id)+MessageSegment.text("\n（自动回复）"+newFile.name+"的诊断结果：\n")

            filepath = os.path.join(basepath, newFile.name)
            pathHMCL = os.path.join(basepath, "hmcl.log")
            pathMCLG = os.path.join(basepath, "minecraft.log")

            stopDiagnose = False

            if os.path.exists(filepath):
                user_idx = event.user_id
                md5_path = os.path.join(basepath, "user_id.txt")
                filesize_path = os.path.join(basepath, "size.txt")

                if os.path.exists(filepath):
                    previous_size = os.path.getsize(filepath)
                    if previous_size == newFile.size:
                        print("Duplicate file detected")
                        print("File exists")
                        print("Duplicate file detected")
                        stopDiagnose = True
                        result = "请不要重复发送文件。如果你觉得自己被后来的日志插队了，请以回复的形式引用你过去发送文件的消息。"
                        # await bot.set_group_ban(group_id=event.group_id, user_id=event.user_id, duration=10*60)
                        # await readFile.send(at_heading + result)
                    else:
                        print("File exists, but of a different size")
            
            if not stopDiagnose:
                async with aiohttp.ClientSession() as session:
                    if await download_file(session, newFile.url, filepath):
                        if newFile.name.endswith(".zip"):
                            try:
                                unzip_file(filepath, basepath)
                                check_files(basepath)
                                
                            except BadZipFile:
                                print("Zip file is corrupted")
                                result = "兄弟，你这压缩包损坏了，打不开"
                                                                   
    else:
        print(event.get_event_description())