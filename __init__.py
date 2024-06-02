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
                                
                                #--fml.mcVersion, 1.20
                                if ("is not supported by active ASM" in data) and (("--fml.mcVersion, 1.20" in data) or ("--fml.mcVersion, 1.19" in data) or ("--fml.mcVersion, 1.18" in data)):
                                    print("Diagnostic: ASM Java bug")
                                    result = load_reply("asmj17.txt")
                                    await readFile.send(at_heading+result)

                                if (("is not supported by active ASM" in data) or ("Unsupported JNI version detected" in data)) and ("--fml.mcVersion, 1.16" in data):
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

                                if "The driver does not appear to support OpenGL" in data:
                                    print("Diagnostic: driver")
                                    result = load_reply("驱动.txt")
                                    await readFile.send(at_heading+result)
                            
                                if ("OutOfMemoryError" in data) or ("GL_OUT_OF_MEMORY" in data):
                                    print("Diagnostic: OOM")
                                    result = load_reply("OOM.txt")
                                    await readFile.send(at_heading+result)

                                #3TUSK
                                if "at nova.committee.enhancedarmaments.init.callback.ProjectileImpactCallback.lambda$static$0(ProjectileImpactCallback.java:17)" in data:
                                    print("Diagnostic: Enchanted Armaments Reloaded")
                                    result = load_reply("Enchanted Armaments Reloaded.txt")
                                    await readFile.send(at_heading+result)

                                if "java.lang.IllegalArgumentException: : Invalid module name: '' is not a Java identifier" in data:
                                    print("Diagnostic: Mod name bug")
                                    result = load_reply("mod文件名纯中文.txt")
                                    await readFile.send(at_heading+result)
                                
                                if "java.lang.IllegalArgumentException: Unsupported class file major version" in data:
                                    print("Diagnostic: booting ASM 9.3.0 higher than Java 17")
                                    result = load_reply("asmj17.txt")
                                    await readFile.send(at_heading+result)

                                if "java.lang.NoSuchMethodError: sun.security.util.ManifestEntryVerifier.<init>(Ljava/util/jar/Manifest;)V" in data:
                                    print("Diagnostic:Forge 36.2.26")
                                    result = load_reply("Forge36.2.26.txt")
                                    await readFile.send(at_heading+result)

                                if "java.lang.UnsupportedClassVersionError: icyllis/modernui/forge/MixinConnector has been compiled by a more recent version of the Java Runtime (class file version 55.0), this version of the Java Runtime only recognizes class file versions up to 52.0" in data:
                                    print("Diagnostic: j11ModernUI")
                                    result = load_reply("j11ModernUI.txt")
                                    await readFile.send(at_heading+result)
                            
                                if "java.lang.NoSuchMethodError: net.minecraft.entity.Entity.getDimensionsForge(Lnet/minecraft/entity/Pose;)Lnet/minecraft/entity/EntitySize;" in data:
                                    print("Diagnostic: Forge 36.2.26 getDimensionsForge")
                                    result = load_reply("Forge_36.2.26_getDimensionsForge.txt")
                                    await readFile.send(at_heading+result)

                                if "java.lang.NoSuchMethodError: 'void net.minecraft.server.level.DistanceManager.addRegionTicket" in data:
                                    print("Diagnostic: OptiFine 1.18.2 H9 pre2")
                                    result = load_reply("OptiFine_1.18.2_H9_pre.txt")
                                    await readFile.send(at_heading+result)

                                if "cannot access class sun.security.util.ManifestEntryVerifier" in data:
                                    print("Diagnostic: ManifestEntryVerifier")
                                    result = load_reply("ManifestEntryVerifier.txt")
                                    await readFile.send(at_heading+result)

                                if ("sun.misc.Unsafe.defineAnonymousClass" in data) and ("java.lang.NoSuchMethodException" in data):
                                    print("Diagnostic: defineAnonymousClass")
                                    result = load_reply("defineAnonymousClass.txt")
                                    await readFile.send(at_heading+result)

                                if ("@Redirect conflict. Skipping dungeons_gear.mixins.json:GameRendererMixin" in data) and ("Critical injection failure: Redirector getModifiedDistance1" in data):
                                    print("Diagnostic: ValkyrienSkies-DungeonGears.txt")
                                    result = load_reply("defineAnonymousClass.txt")
                                    await readFile.send(at_heading+result)

                            #check if hmcl.log exists
                        if os.path.exists(pathHMCL):
                            print("hmcl.log exists")
                            encode_format = "utf-8"
                            with open(pathLatest, 'r', encoding=encode_format) as file:
                                try:
                                    data = file.read()
                                except UnicodeDecodeError:
                                    encode_format = "gb2312"

                            with open(pathHMCL, 'r', encoding=encode_format) as file:
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
                                
                                if "Crash cause: MEMORY_EXCEEDED" in data:
                                    print("Diagnostic: MEMORY_EXCEEDED")
                                    result = load_reply("MEMORY_EXCEEDED.txt")
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