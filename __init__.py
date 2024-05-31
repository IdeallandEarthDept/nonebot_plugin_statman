from nonebot import require
from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata

from .config import Config

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

#require("requests")
from pip._vendor import requests
from nonebot.drivers import aiohttp
import asyncio

import zipfile

import os
import zipfile
import aiohttp
import asyncio

__plugin_meta__ = PluginMetadata(
    name="nonebot_plugin_statman",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)


current_directory = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(current_directory, 'main.csv')
group_path = os.path.join(current_directory, 'group.csv')


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

readFile = on_notice(priority=1, block=False)
@readFile.handle()
async def handle_upload(bot: Bot, event: Event, state: T_State):
    if event.get_event_name() == "notice.group_upload":
        newFile = event.file
        if newFile.size <= 3000000:
            basepath = f"./data/{__plugin_meta__.name}/{newFile.name[:-4]}"  # Remove '.zip' and create a directory
            if not os.path.exists(basepath):
                os.makedirs(basepath)

            filepath = os.path.join(basepath, newFile.name)
            async with aiohttp.ClientSession() as session:
                if await download_file(session, newFile.url, filepath):
                    if newFile.name.endswith(".zip"):
                        unzip_file(filepath, basepath)
                        check_files(basepath)

def check_files(directory):
    """List files in directory"""
    for root, dirs, files in os.walk(directory):
        for file in files:
            print(f"Found file: {file}")
        for dir in dirs:
            print(f"Found directory: {dir}")

# async def download_file(url, filename):
#     print(f'正在下载 {url} 到 {filename}')
#     async with aiohttp.ClientSession() as session:
#         async with session.get(url) as response:
#             if response.status == 200:
#                 print(f'HTTP 状态码：{response.status}')
#                 with open(filename, 'wb') as f:
#                     while True:
#                         chunk = await response.content.read(1024)
#                         if not chunk:
#                             break
#                         f.write(chunk)
#                 print(f'文件已下载并保存为 {filename}')
#                 return None
#             else:
#                 print(f'下载失败，HTTP 状态码：{response.status}')
#                 return response.status

# def unzip_file(zip_path, extract_to):
#     with zipfile.ZipFile(zip_path, 'r') as zip_ref:
#         zip_ref.extractall(extract_to)

example = on_command("统计器测试", rule=to_me(), priority=1, block=False)
@example.handle()
async def handle_function(args: Message = CommandArg()):
    await example.finish("测试成功，机器人在线")


# readFile = on_notice(priority=1, block=False)
# @readFile.handle()
# async def handle_function(bot: Bot, event: Event, state: T_State):
#     print("On Notice:"+str(event)+"\n")
#     if event.get_event_name() == "notice.group_upload":
#         print("Group Upload\n")
#         newFile = event.file
#         if newFile.size <= 3000000:
#             print(newFile.url)
#             print(f"{newFile.name} is of {newFile.size} bytes, url is {newFile.url} \n")

#             basepath = f".\\data\\{__plugin_meta__.name}"
#             path =  f"{basepath}\\{newFile.name}"

#             if not os.path.exists(basepath):
#                 os.makedirs(basepath)
#             elif os.path.exists(path):
#                 print(f"[DISCARDED][DUPLICATE] {path} already exists\n")
#                 pass
#             else:
#                 os.makedirs(path)
#                 print(f"[CREATED] {path}\n")

#             #download the file with the given url by https protocol
#             if download_file(newFile.url, path) == None:
#                 print(f"[SAVED] {newFile.name}\n")
#                 #if newFile.name ends with .zip or .rar, extract it
#                 if newFile.name.endswith(".zip"):
#                     print(f"[EXTRACTING] {newFile.name}\n")
#                     unzip_file(path, path)
#                     pass
#         else:
#             print(f"[DISCARDED][SIZE_TOO_BIG] {newFile.name} is of {newFile.size} bytes, url is {newFile.url} \n")
            
#     print(event.get_event_description()+"\n")
#     # print(event.get_message()+"\n")
#     pass

readMsg = on_message(priority=100, block=False)
@readMsg.handle()
async def handle_function(bot: Bot, event: Event, state: T_State):
    print("Msg Recv:"+str(event)+"\n")
    print(event.get_type()+"\n")
   

    fileTemp = open(csv_path, mode='a', buffering=-1, encoding="utf-8")
    fileTemp.write(str(event)+"\n")
    fileTemp.close()
    # write the event as a string
    # if the msg is from a qq group
    if event.get_type() == "message":
        print(str(event.user_id)+"\n")
        print(str(event.message_type)+"\n")
        print(event.get_message()+"\n")

        user_unique_path = os.path.join(current_directory, str(event.user_id)+'.csv')

        fileGroup = open(user_unique_path, mode='a', buffering=-1, encoding="utf-8")
        #escape all new lines
        newMsg = str(event.get_message()).replace("\n", "\\n")
        fileGroup.write(newMsg+"\n")
        fileGroup.close()

        if event.message_type=="group":
            group_unique_path = os.path.join(current_directory, str(event.group_id)+'G.csv')
            fileTemp = open(group_unique_path, mode='a', buffering=-1, encoding="utf-8")
            fileTemp.write(str(event)+"\n")
            fileTemp.close()
    pass