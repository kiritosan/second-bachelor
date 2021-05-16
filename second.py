import requests
from bs4 import BeautifulSoup
import re

from nonebot import on_command
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event



second = on_command("第二学士", rule=to_me(), priority=1)

@second.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip()  # 首次发送命令时跟随的参数，例：/天气 上海，则args为上海
    if args:
        state["num"] = args  # 如果用户发送了参数则直接赋值

@second.got("num", prompt="请在命令后输入汉字“一”或“五”，查询最新一所或最新五所第二学士招生学校")
async def handle_num(bot: Bot, event: Event, state: T_State):
    num = state["num"]
    if num not in ["一", "五"]:
        await second.reject("当前命令不受支持，请重新输入")
    school_result = await get_school(num)
    await second.finish(school_result)


async def get_school(num: str):
    url = 'https://zhuanlan.zhihu.com/p/359959168'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.56'
    }
    # 获得内容
    r = requests.get(url,headers=headers)
    # 解析
    soup = BeautifulSoup(r.text,"lxml")

    # # 函数方式匹配学校信息 获得Match对象
    # res = re.search("一、对外招生院校(.*)（限海南生源）",soup.get_text())

    # 不知道为什么使用上面的方式返回NoneType得不到值 采用下面的方法 
    # 对象方式匹配 .get_text方法得到的文本 得到match对象
    pattern = re.compile(r'一、对外招生院校(.*)（限海南生源）')
    res = pattern.search(soup.get_text())

    # 获取re.Match对象里面的内容
    messy = res.group(0)

    # 通过替换字符将学校分行 https://blog.csdn.net/xuezhangjun0121/article/details/78470471
    result = re.sub('No.','\nNo.',messy)
    # 或许最新公布的一所对外招收第二学位的学校
    head = result.split('\n')[1]
    # 返回前五所对外招收第二学位的学校
    top = result.split('\n')[1:6]
    if num == '一':
        return f"最新一所为{head}"
    if num == '五':
        return f"最新五所为{top}"