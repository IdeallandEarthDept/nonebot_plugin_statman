from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata

from .config import Config

from nonebot import on_command
from nonebot import on
from nonebot.rule import to_me
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.exception import MatcherException
import os.path

from nonebot.adapters.onebot.v11 import Message, MessageSegment, Bot, Event
from nonebot.typing import T_State

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

#from nonebot.adapters.console import Message, MessageSegment

example = on_command("统计器测试", rule=to_me(), priority=1, block=False)
@example.handle()
async def handle_function(args: Message = CommandArg()):
    await example.finish("测试成功，机器人在线")

readMsg = on("", priority=1, block=False)
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