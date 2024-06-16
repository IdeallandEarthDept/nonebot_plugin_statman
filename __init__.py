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
                        await bot.set_group_ban(group_id=event.group_id, user_id=event.user_id, duration=10*60)
                        await readFile.send(at_heading + result)
                    else:
                        print("File exists, but of a different size")

                # if os.path.exists(md5_path):

                #     with open(md5_path, 'r') as f:  # 以读取模式打开
                #         md5sums = f.read().splitlines()

                #     if user_idx in md5sums:
                #         print("Duplicate file detected")
                #         stopDiagnose = True
                #         result = "请不要重复发送文件。如果你觉得自己被后来的日志插队了，请以回复的形式引用你过去发送文件的消息。"
                #         await bot.set_group_ban(group_id=event.group_id, user_id=event.user_id, duration=10*60)
                #         await readFile.send(at_heading + result)
                #     else:
                #         with open(md5_path, 'a') as f:  # 以追加模式打开，用于写入新的MD5
                #             f.write(user_idx + "\n")
                #         print("Passed check. MD5 added to md5sums.txt")
                # else:
                #     # 如果md5sums.txt文件不存在，则创建文件并写入首个MD5
                #     with open(md5_path, 'w') as f:
                #         f.write(user_idx + "\n")
                #     print("MD5 file created and MD5 added to md5sums.txt")

                
                # stopDiagnose = True
                # result = "请不要重复发送文件。如果你觉得自己被后来的日志插队了，请以回复的形式引用你过去发送文件的消息。"
                # await bot.set_group_ban(group_id = event.group_id, user_id = event.user_id, duration = 10*60)
                # await readFile.send(at_heading+result)
            
            if not stopDiagnose:
                async with aiohttp.ClientSession() as session:
                    if await download_file(session, newFile.url, filepath):
                        if newFile.name.endswith(".zip"):
                            try:
                                unzip_file(filepath, basepath)
                                check_files(basepath)
                                
                                encode_format = "gb2312"

                                pathLatest = os.path.join(basepath, "latest.log")
                                
                                result = ""

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

                                        if ("The requested compatibility level JAVA_21 could not be set. Level is not supported by the active JRE or ASM version" in data):
                                            print("Diagnostic: j21")
                                            result = load_reply("j21.txt")
                                            await readFile.send(at_heading+result)

                                        if "Failed to install mod /djpadbit/Sound-Physics/releases/download/1.0.10-1/Sound-Physics-1.12.2" in data:
                                            print("Diagnostic: Sound-Physics")
                                            result = load_reply("sound_physics.txt")
                                            await readFile.send(at_heading+result)

                                        if "Ticking entity" in data:
                                            print("Diagnostic: Ticking entity")
                                            result = load_reply("Neruina.txt")
                                            await readFile.send(at_heading+result)

                                        if "java.lang.IllegalStateException: Not building!" in data:
                                            print("Diagnostic: Not building")
                                            result = load_reply("notbuilding.txt")
                                            await readFile.send(at_heading+result)

                                        #beikui
                                        if ("Asking for biomes before we have biomes" in data):
                                            print("Diagnostic: Asking for biomes before we have biomes")
                                            result = load_reply("beikui/Asking_for_biomes.txt")
                                            await readFile.send(at_heading+result)

                                        if ("UncheckedIOException" in data) and ("Invalid paths argument, contained no existing paths:" in data):
                                            print("Diagnostic: Invalid paths argument,")
                                            result = load_reply("beikui/Invalid_paths_argument.txt")
                                            await readFile.send(at_heading+result)

                                        if ("java.lang.Error: Watchdog" in data):
                                            print("Diagnostic: watchdog")
                                            result = load_reply("beikui/watchdog_bk.txt")
                                            await readFile.send(at_heading+result)

                                        if ("RivaTuner Statistics Server (RTSS) is not compatible with Xenon" in data):
                                            print("Diagnostic: RTSS")
                                            result = load_reply("beikui/rtss.txt")
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

                                if result == "" and os.path.exists(pathMCLG):
                                    print("minecraft.log exists")
                                    encode_format = "utf-8"
                                    with open(pathLatest, 'r', encoding=encode_format) as file:
                                        try:
                                            data = file.read()
                                        except UnicodeDecodeError:
                                            encode_format = "gb2312"

                                    with open(pathMCLG, 'r', encoding=encode_format) as file:
                                        data = file.read()

                                        if "kotlin.native.concurrent: Invalid package name: 'native' is not a Java identifier" in data:
                                            print("Diagnostic: Kotlin bug")
                                            result = load_reply("minecraft/nativeIsNotAJavaIdentifier.txt")
                                            await readFile.send(at_heading+result)


                                    #check if hmcl.log exists
                                if result == "" and os.path.exists(pathHMCL):
                                    print("hmcl.log exists")
                                    encode_format = "utf-8"
                                    with open(pathLatest, 'r', encoding=encode_format) as file:
                                        try:
                                            data = file.read()
                                        except UnicodeDecodeError:
                                            encode_format = "gb2312"

                                    with open(pathHMCL, 'r', encoding=encode_format) as file:
                                        data = file.read()

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
                                        
                                        # if "Crash cause: GRAPHICS_DRIVER" in data:
                                        #     print("Diagnostic: GRAPHICS_DRIVER")
                                        #     result = load_reply("hmcl/GRAPHICS_DRIVER.txt")
                                        #     await readFile.send(at_heading+result)

                                        # if "Java Version: 1.8.0_411, Oracle Corporation" in data:
                                        #     print("Diagnostic: Java Version: 1.8.0_411, Oracle Corporation bug")
                                        #     result = load_reply("8u411.txt")
                                        #     # await readFile.send(MessageSegment.at()+MessageSegment.text(result))
                                        #     await readFile.send(at_heading+result)
                                        # else:
                                        #     print("[Diag]Not Oracle 8u411")
                            except BadZipFile:
                                print("Zip file is corrupted")
                                result = "兄弟，你这压缩包损坏了，打不开"
                                await readFile.send(at_heading+result)            
                                    
                                    
    else:
        print(event.get_event_description())

#recall message
recallMsg = on_message(priority=100, block=False, permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER)
@recallMsg.handle()
async def handle_recall(bot: Bot, event: Event, state: T_State):
    fileTemp = open(csv_path, mode='a', buffering=-1, encoding="utf-8")
    fileTemp.write(str(event)+"\n")
    fileTemp.close()

    # write the event as a string
    # if the msg is from a qq group
    if event.get_type() == "message":
        # print(str(event.user_id))
        # print(str(event.message_type))
        # print(event.get_message())

        if event.reply:
            reply_qq = {segment.data["qq"] for segment in event.original_message["at"]}
            # print("===============Reply Detected============")

            # print(event.get_message())
            # if the message contains "反对"
            if ("反对" in str(event.get_message())) or ("撤回" in str(event.get_message())) or ("康" in str(event.get_message())):
                # if the message is from an admin
                # if event.sender.role == "admin":
                await asyncio.sleep(randint(0, 2))  # 睡眠随机时间，避免黑号
                # recall the message that is being replied
                print("===============Recalling message============")
                await bot.delete_msg(message_id=event.reply.message_id)

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

        # if event.reply:
        #     reply_qq = {segment.data["qq"] for segment in event.original_message["at"]}
        #     print("===============Reply Detected============")

        #     print(event.get_message())
        #     # if the message contains "反对"
        #     if "反对" in str(event.get_message()):
        #         # if the message is from an admin
        #         # if event.sender.role == "admin":
        #         await asyncio.sleep(randint(0, 2))  # 睡眠随机时间，避免黑号
        #         # recall the message that is being replied
        #         print("===============Recalling message============")
        #         await bot.delete_msg(message_id=event.reply.message_id)

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

            if (("为啥" in newMsg) or ("为什么" in newMsg) or ("怎么" in newMsg) or ("咋" in newMsg)) and (("踢" in newMsg) and ("我" in newMsg)) :
                if event.group_id == 666546887 or event.group_id == 625927837:
                    at_heading = MessageSegment.at(event.user_id)+MessageSegment.text("\n（自动回复）")
                    print("Auto-reply: 为什么踢我")
                    result = load_reply("hmcl/why_kick_me.txt")
                    await readFile.send(at_heading+result)
    pass