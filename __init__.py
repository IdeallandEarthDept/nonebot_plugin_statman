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
# from nonebot.drivers import aiohttp
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

#   please note that if you installed the internal plugin "single_session",
# the notice will be blocked by that thing, and will hence FAIL.
readFile = on_notice(priority=3, block=False)
@readFile.handle()
async def handle_upload(bot: Bot, event: Event):
    print("On Notice:"+str(event)+"\n")
    if event.get_event_name() == "notice.group_upload":
        newFile = event.file
        if newFile.size <= 3000000 :    # 3MB
            basepath = f"./data/{__plugin_meta__.name}/{newFile.name}"
            if newFile.name.endswith(".zip"):
                basepath = f"./data/{__plugin_meta__.name}/{newFile.name[:-4]}"  # Remove '.zip' and create a directory
            
            if not os.path.exists(basepath):
                os.makedirs(basepath)

            at_heading = MessageSegment.at(event.user_id)+MessageSegment.text("\n（自动回复）"+newFile.name+"的诊断结果：\n")

            filepath = os.path.join(basepath, newFile.name)
            pathHMCL = os.path.join(basepath, "hmcl.log")
            async with aiohttp.ClientSession() as session:
                if await download_file(session, newFile.url, filepath):
                    if newFile.name.endswith(".zip"):
                        unzip_file(filepath, basepath)
                        check_files(basepath)
                        
                        encode_format = "gb2312"
                        if os.path.exists(pathHMCL):
                            encode_format = "utf-8"

                        #check if hmcl.log exists
                        
                        if os.path.exists(pathHMCL):
                            print("hmcl.log exists")
                            #search the file for string "Java Version: 1.8.0_411, Oracle Corporation"
                            with open(pathHMCL, 'r', encoding=encode_format) as file:
                                try:
                                    data = file.read()
                                except UnicodeDecodeError:
                                    encode_format = "utf-8"
                                    file.seek(0)
                                    data = file.read()
                                if "Java Version: 1.8.0_411, Oracle Corporation" in data:
                                    print("Diagnostic: Java Version: 1.8.0_411, Oracle Corporation bug")
                                    result = load_reply("8u411.txt")
                                    # await readFile.send(MessageSegment.at()+MessageSegment.text(result))
                                    await readFile.send(at_heading+result)
                                else:
                                    print("[Diag]Not Oracle 8u411")

                                if "Operating System: Mac OS" in data:
                                    print("Diagnostic: MacOS bug")
                                    result = load_reply("Mac88.txt")
                                    await readFile.send(at_heading+result)
                                else:
                                    print("[Diag]Not MacOS")

                        pathLatest = os.path.join(basepath, "latest.log")
                        
                        if os.path.exists(pathLatest):
                            print("latest.log exists")

                            with open(pathLatest, 'r', encoding=encode_format) as file:
                                try:
                                    data = file.read()
                                except UnicodeDecodeError:
                                    encode_format = "utf-8"

                            #search the file for string "Java Version: 1.8.0_411, Oracle Corporation"
                            with open(pathLatest, 'r', encoding=encode_format) as file:
                                try:
                                    data = file.read()
                                except UnicodeDecodeError:
                                    encode_format = "utf-8"
                                    file.seek(0)
                                    data = file.read()
                                
                                if "is not supported by active ASM" in data:
                                    print("Diagnostic: ASM Java bug")
                                    result = load_reply("aj11.txt")
                                    await readFile.send(at_heading+result)
                                
                                if "You are currently using SerializationIsBad without any patch modules configured." in data:
                                    print("Diagnostic: serializationisbad")
                                    result = load_reply("serializationisbad.txt")
                                    await readFile.send(at_heading+result)
                                
                                if "com.electronwill.nightconfig.core.io.ParsingException: Not enough data available" in data:
                                    print("Diagnostic: nightconfig")
                                    result = load_reply("nightconfig.txt")
                                    await readFile.send(at_heading+result)
                            
                                if ("OutOfMemoryError" in data) or ("GL_OUT_OF_MEMORY" in data):
                                    print("Diagnostic: OOM")
                                    result = load_reply("OOM.txt")
                                    await readFile.send(at_heading+result)
                            

                                
                                    
    else:
        print(event.get_event_description())

#statistic of text messages
readMsg = on_message(priority=100, block=False)
@readMsg.handle()
async def handle_function(bot: Bot, event: Event, state: T_State):
    fileTemp = open(csv_path, mode='a', buffering=-1, encoding="utf-8")
    fileTemp.write(str(event)+"\n")
    fileTemp.close()
    # write the event as a string
    # if the msg is from a qq group
    if event.get_type() == "message":
        print(str(event.user_id))
        print(str(event.message_type))
        print(event.get_message())

        if not os.path.exists(stat_directory):
            os.makedirs(stat_directory)

        user_unique_path = os.path.join(stat_directory, str(event.user_id)+'.csv')

        fileGroup = open(user_unique_path, mode='a', buffering=-1, encoding="utf-8")
        #escape all new lines
        newMsg = str(event.get_message()).replace("\n", "\\n")
        fileGroup.write(newMsg+"\n")
        fileGroup.close()

        if event.message_type=="group":
            group_unique_path = os.path.join(stat_directory, str(event.group_id)+'G.csv')
            fileTemp = open(group_unique_path, mode='a', buffering=-1, encoding="utf-8")
            fileTemp.write(str(event)+"\n")
            fileTemp.close()
    pass