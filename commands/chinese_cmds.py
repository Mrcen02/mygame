"""
中文指令集 (Chinese Command Set)

为 Evennia 游戏提供中文自然语言指令支持，模拟真实人类常用操作。
包括: 移动、物品交互、装备、社交表情、生理行为、环境交互等。

覆盖类别:
  一、移动: 东/南/西/北/东北/西北/东南/西南/上/下/进入/离开
  二、观察: 看/打量/端详/凝视/瞥
  三、物品: 拿/捡/扔/放/给/背包/查看背包
  四、饮食: 吃/喝/咬/啃/尝/品
  五、装备: 穿/脱/装备/手持/佩戴
  六、社交: 说/喊/耳语/笑/哭/微笑/点头/摇头/挥手/鼓掌/拥抱/亲吻/鞠躬/跪下/磕头
  七、体态: 坐/站/躺/蹲/爬/睡/藏/跳/跑/走
  八、表情: 叹气/打哈欠/唱歌/跳舞/吹口哨/耸肩/指/眨眼/闭眼/揉眼/挠头/搓手/伸懒腰/捂脸/捂嘴/抱胸/叉腰/背手/张开双臂/扶额
  九、生理: 拉屎/拉尿/吐/吐口水/打喷嚏/咳嗽/抹汗/发抖
  十、战斗: 打/踢/扇耳光/戳/掐/拧/揪/拍/推人/拉人
  十一、经济: 乞讨/讨钱/给钱/偷/数钱/付钱
  十二、环境: 打开/关闭/推/拉/挖/埋/烧/点火/生火/熄灭/钓鱼/读书/写字/修理/破坏/使用/搜索/翻找/剪/贴/涂/擦/洗/扫
  十三、状态: 装死/装睡/发抖/抽泣/嚎啕/哽咽/抹泪/抹汗/扇风/烤火/搓手取暖
"""

from evennia.commands.command import Command
from evennia import default_cmds
from evennia.utils import search
import random


# =============================================================================
# 基础命令基类
# =============================================================================

# 方向关键词到出口关键字的映射
DIRECTION_MAP = {
    "东": "east", "east": "east", "e": "east",
    "西": "west", "west": "west", "w": "west",
    "南": "south", "south": "south", "s": "south",
    "北": "north", "north": "north", "n": "north",
    "东北": "northeast", "northeast": "northeast", "ne": "northeast",
    "西北": "northwest", "northwest": "northwest", "nw": "northwest",
    "东南": "southeast", "southeast": "southeast", "se": "southeast",
    "西南": "southwest", "southwest": "southwest", "sw": "southwest",
    "上": "up", "up": "up", "u": "up",
    "下": "down", "down": "down", "d": "down",
}

# 方向中文名
DIRECTION_CN = {
    "east": "东", "west": "西", "south": "南", "north": "北",
    "northeast": "东北", "northwest": "西北",
    "southeast": "东南", "southwest": "西南",
    "up": "上", "down": "下",
}


class ChineseCommand(Command):
    """中文指令基类"""
    def parse(self):
        self.args = self.args.strip()

    def get_target(self, search_str=None):
        target_str = (search_str or self.args).strip()
        if not target_str:
            return None
        return self.caller.search(target_str, location=self.caller.location, quiet=True)

    def _find_exit(self, direction):
        """
        在当前房间查找指定方向的出口。
        返回找到的出口对象，或 None。
        """
        # 按方向英文名查找出口
        exits = self.caller.location.exits
        for ex in exits:
            # 检查出口的 key 或 aliases 是否匹配
            exit_key = ex.key.lower()
            exit_aliases = [a.lower() for a in ex.aliases.all()]
            if exit_key == direction or direction in exit_aliases:
                return ex
        return None

    def _move(self, direction):
        """
        尝试向指定方向移动。
        direction 是英文方向名（如 'east', 'north'）。
        成功返回 True，失败返回 False。
        """
        exit_obj = self._find_exit(direction)
        if exit_obj:
            # 直接调用出口的遍历方法
            self.caller.move_to(exit_obj.destination)
            return True
        else:
            dir_cn = DIRECTION_CN.get(direction, direction)
            self.caller.msg(f"那个方向没有路，你无法往{dir_cn}走。")
            return False


# =============================================================================
# 一、移动指令
# =============================================================================

class CmdEast(ChineseCommand):
    """向东走"""
    __doc__ = "向东走"
    key = "东"
    aliases = ["east", "e", "向东", "往东"]

    def func(self):
        self._move("east")


class CmdWest(ChineseCommand):
    """向西走"""
    __doc__ = "向西走"
    key = "西"
    aliases = ["west", "w", "向西", "往西"]

    def func(self):
        self._move("west")


class CmdSouth(ChineseCommand):
    """向南走"""
    __doc__ = "向南走"
    key = "南"
    aliases = ["south", "s", "向南", "往南"]

    def func(self):
        self._move("south")


class CmdNorth(ChineseCommand):
    """向北走"""
    __doc__ = "向北走"
    key = "北"
    aliases = ["north", "n", "向北", "往北"]

    def func(self):
        self._move("north")


class CmdNortheast(ChineseCommand):
    """向东北走"""
    __doc__ = "向东北走"
    key = "东北"
    aliases = ["northeast", "ne"]

    def func(self):
        self._move("northeast")


class CmdNorthwest(ChineseCommand):
    """向西北走"""
    __doc__ = "向西北走"
    key = "西北"
    aliases = ["northwest", "nw"]

    def func(self):
        self._move("northwest")


class CmdSoutheast(ChineseCommand):
    """向东南走"""
    __doc__ = "向东南走"
    key = "东南"
    aliases = ["southeast", "se"]

    def func(self):
        self._move("southeast")


class CmdSouthwest(ChineseCommand):
    """向西南走"""
    __doc__ = "向西南走"
    key = "西南"
    aliases = ["southwest", "sw"]

    def func(self):
        self._move("southwest")


class CmdUp(ChineseCommand):
    """向上走"""
    __doc__ = "向上走"
    key = "上"
    aliases = ["up", "u", "向上"]

    def func(self):
        self._move("up")


class CmdDown(ChineseCommand):
    """向下走"""
    __doc__ = "向下走"
    key = "下"
    aliases = ["down", "d", "向下"]

    def func(self):
        self._move("down")


class CmdEnter(ChineseCommand):
    """进入某处"""
    __doc__ = "进入某处"
    key = "进入"
    aliases = ["enter", "进", "进去"]

    def func(self):
        if self.args:
            self.caller.execute_cmd(f"enter {self.args}")
        else:
            self.caller.execute_cmd("enter")


class CmdExit(ChineseCommand):
    """离开"""
    __doc__ = "离开当前所在"
    key = "离开"
    aliases = ["exit", "出", "出去"]

    def func(self):
        self.caller.execute_cmd("exit")


# =============================================================================
# 二、观察指令
# =============================================================================

class CmdLook(ChineseCommand):
    __doc__ = "查看周围环境或目标"
    key = "看"
    aliases = ["look", "l", "查看", "观察", "瞧瞧", "打量", "端详", "凝视", "瞥", "东张西望"]

    def func(self):
        if self.args:
            self.caller.execute_cmd(f"look {self.args}")
        else:
            self.caller.execute_cmd("look")


# =============================================================================
# 三、物品交互指令
# =============================================================================

class CmdGet(ChineseCommand):
    __doc__ = "拿起物品"
    key = "拿"
    aliases = ["get", "捡", "拾", "捡起", "拾起", "取", "拿起", "捧起", "拎起", "拾取"]

    def func(self):
        if not self.args:
            self.caller.msg("你想拿什么？")
            return
        self.caller.execute_cmd(f"get {self.args}")


class CmdDrop(ChineseCommand):
    __doc__ = "丢弃物品"
    key = "扔"
    aliases = ["drop", "丢弃", "丢掉", "扔掉", "放下", "丢"]

    def func(self):
        if not self.args:
            self.caller.msg("你想扔什么？")
            return
        self.caller.execute_cmd(f"drop {self.args}")


class CmdGive(ChineseCommand):
    __doc__ = "将物品给予他人"
    key = "给"
    aliases = ["give", "给予", "递给", "交给", "送给", "赠予", "送"]

    def func(self):
        if not self.args:
            self.caller.msg("你想给谁什么东西？格式：给 <物品> 给 <目标> 或 给 <目标>=<物品>")
            return
        self.caller.execute_cmd(f"give {self.args}")


class CmdPut(ChineseCommand):
    __doc__ = "将物品放入容器"
    key = "放"
    aliases = ["put", "放入", "放进", "装进", "塞进", "存入"]

    def func(self):
        if not self.args:
            self.caller.msg("你想放什么？放到哪里？格式：放 <物品> 在 <容器>")
            return
        self.caller.execute_cmd(f"put {self.args}")


class CmdInventory(ChineseCommand):
    __doc__ = "查看背包"
    key = "背包"
    aliases = ["inventory", "i", "inv", "物品", "行囊", "包里", "口袋", "查看背包", "翻背包", "翻包", "清点"]

    def func(self):
        self.caller.execute_cmd("inventory")


# =============================================================================
# 四、饮食指令
# =============================================================================

class CmdEat(ChineseCommand):
    __doc__ = "吃食物"
    key = "吃"
    aliases = ["eat", "食用", "吃下", "吃一口", "尝", "品尝", "尝尝", "啃", "咬",
               "咬一口", "狼吞虎咽", "细嚼慢咽", "吞", "咀嚼"]

    def func(self):
        if not self.args:
            self.caller.msg("你想吃什么？")
            return
        target = self.get_target()
        if target:
            self.caller.location.msg_contents(
                f"{self.caller.name} 吃下了 {target.name}。",
                exclude=[self.caller]
            )
            self.caller.msg(f"你吃下了 {target.name}。")
            try:
                target.delete()
            except Exception:
                pass
        else:
            self.caller.msg(f"这里没有 '{self.args}' 可以吃。")


class CmdDrink(ChineseCommand):
    __doc__ = "喝液体"
    key = "喝"
    aliases = ["drink", "饮", "喝下", "喝一口", "灌", "品", "干杯", "一饮而尽", "喝光"]

    def func(self):
        if not self.args:
            self.caller.msg("你想喝什么？")
            return
        target = self.get_target()
        if target:
            self.caller.location.msg_contents(
                f"{self.caller.name} 喝下了 {target.name}。",
                exclude=[self.caller]
            )
            self.caller.msg(f"你喝下了 {target.name}。")
            try:
                target.delete()
            except Exception:
                pass
        else:
            self.caller.msg(f"这里没有 '{self.args}' 可以喝。")


# =============================================================================
# 五、装备指令
# =============================================================================

class CmdWear(ChineseCommand):
    __doc__ = "穿上装备或衣物"
    key = "穿"
    aliases = ["wear", "穿上", "穿戴", "套上", "披上", "戴上", "系上", "着装"]

    def func(self):
        if not self.args:
            self.caller.msg("你想穿什么？")
            return
        self.caller.execute_cmd(f"wear {self.args}")


class CmdRemove(ChineseCommand):
    __doc__ = "脱掉装备或衣物"
    key = "脱"
    aliases = ["remove", "脱下", "脱掉", "摘掉", "解下", "卸下", "褪下"]

    def func(self):
        if not self.args:
            self.caller.msg("你想脱什么？")
            return
        self.caller.execute_cmd(f"remove {self.args}")


class CmdWield(ChineseCommand):
    __doc__ = "装备武器"
    key = "装备"
    aliases = ["wield", "手持", "拿起武器", "抄起", "握", "持", "举", "扛"]

    def func(self):
        if not self.args:
            self.caller.msg("你想装备什么武器？")
            return
        self.caller.execute_cmd(f"wield {self.args}")


# =============================================================================
# 六、社交/表情指令
# =============================================================================

class CmdSpeak(ChineseCommand):
    __doc__ = "说话"
    key = "说"
    aliases = ["say", "说话", "讲", "道", "说道", "自言自语", "喃喃自语", "喃喃"]

    def func(self):
        if not self.args:
            self.caller.msg("你想说什么？")
            return
        self.caller.execute_cmd(f"say {self.args}")


class CmdShout(ChineseCommand):
    __doc__ = "大声喊叫"
    key = "喊"
    aliases = ["shout", "大喊", "叫", "嚷", "大吼", "咆哮", "怒吼", "喝道", "叫道"]

    def func(self):
        if not self.args:
            self.caller.msg("你想喊什么？")
            return
        self.caller.execute_cmd(f"shout {self.args}")


class CmdWhisper(ChineseCommand):
    __doc__ = "对某人耳语"
    key = "耳语"
    aliases = ["whisper", "悄悄话", "低声", "附耳", "小声说", "悄声", "低语", "咬耳朵"]

    def func(self):
        if not self.args:
            self.caller.msg("你想对谁耳语？格式：耳语 <目标>=<话>")
            return
        self.caller.execute_cmd(f"whisper {self.args}")


class CmdLaugh(ChineseCommand):
    __doc__ = "发出笑声"
    key = "笑"
    aliases = ["laugh", "大笑", "哈哈", "呵呵", "嘻嘻", "嘿嘿", "冷笑", "狂笑", "坏笑", "微笑",
               "大笑起来", "笑出声", "捧腹大笑", "开怀大笑", "仰天大笑", "含笑", "奸笑", "偷笑"]

    def func(self):
        emote = self.cmdstring
        if emote == "笑":
            emote = random.choice(["笑了笑", "呵呵一笑", "微微一笑", "哈哈一笑"])
        elif emote in ("哈哈", "呵呵", "嘻嘻", "嘿嘿"):
            emote = f"{emote}一笑"
        self.caller.location.msg_contents(f"{self.caller.name} {emote}。")
        self.caller.msg(f"你{emote}。")


class CmdCry(ChineseCommand):
    __doc__ = "哭"
    key = "哭"
    aliases = ["cry", "哭泣", "流泪", "落泪", "抽泣", "嚎啕大哭", "嚎啕", "哽咽", "抹泪",
               "泪如雨下", "泪流满面", "泣不成声", "痛哭流涕", "大哭", "呜呜哭"]

    def func(self):
        emote = self.cmdstring
        if emote == "哭":
            emote = random.choice(["哭了起来", "流下了眼泪", "抽泣着", "泪流满面"])
        self.caller.location.msg_contents(f"{self.caller.name} {emote}。")
        self.caller.msg(f"你{emote}。")


class CmdSmile(ChineseCommand):
    __doc__ = "微笑"
    key = "微笑"
    aliases = ["smile", "展颜", "莞尔", "浅笑", "抿嘴笑", "嘴角上扬", "面带笑意", "甜甜地笑"]

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.name} 露出了微笑。")
        self.caller.msg("你露出了微笑。")


class CmdNod(ChineseCommand):
    __doc__ = "点头"
    key = "点头"
    aliases = ["nod", "颔首", "点点头", "微微点头", "重重点头", "连连点头", "首肯"]

    def func(self):
        if self.args:
            self.caller.location.msg_contents(f"{self.caller.name} 对 {self.args} 点了点头。")
            self.caller.msg(f"你对 {self.args} 点了点头。")
        else:
            self.caller.location.msg_contents(f"{self.caller.name} 点了点头。")
            self.caller.msg("你点了点头。")


class CmdShakeHead(ChineseCommand):
    __doc__ = "摇头"
    key = "摇头"
    aliases = ["shake", "摇摇头", "连连摇头", "摇头叹息", "摇首", "摆了摆头"]

    def func(self):
        if self.args:
            self.caller.location.msg_contents(f"{self.caller.name} 对 {self.args} 摇了摇头。")
            self.caller.msg(f"你对 {self.args} 摇了摇头。")
        else:
            self.caller.location.msg_contents(f"{self.caller.name} 摇了摇头。")
            self.caller.msg("你摇了摇头。")


class CmdWave(ChineseCommand):
    __doc__ = "挥手"
    key = "挥手"
    aliases = ["wave", "招手", "挥挥手", "挥手告别", "挥手示意", "摆了摆手", "扬手"]

    def func(self):
        if self.args:
            self.caller.location.msg_contents(f"{self.caller.name} 朝 {self.args} 挥了挥手。")
            self.caller.msg(f"你朝 {self.args} 挥了挥手。")
        else:
            self.caller.location.msg_contents(f"{self.caller.name} 挥了挥手。")
            self.caller.msg("你挥了挥手。")


class CmdClap(ChineseCommand):
    __doc__ = "鼓掌"
    key = "鼓掌"
    aliases = ["clap", "拍手", "拍掌", "喝彩", "叫好", "拍手叫好", "鼓掌叫好", "鼓掌欢呼"]

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.name} 鼓起掌来。")
        self.caller.msg("你鼓起掌来。")


class CmdHug(ChineseCommand):
    __doc__ = "拥抱某人"
    key = "拥抱"
    aliases = ["hug", "抱", "抱住", "搂", "搂住", "紧抱", "熊抱", "抱抱", "相拥"]

    def func(self):
        if not self.args:
            self.caller.msg("你想拥抱谁？")
            return
        self.caller.location.msg_contents(f"{self.caller.name} 拥抱了 {self.args}。")
        self.caller.msg(f"你拥抱了 {self.args}。")


class CmdKiss(ChineseCommand):
    __doc__ = "亲吻"
    key = "亲吻"
    aliases = ["kiss", "亲", "吻", "亲一下", "亲一口", "热吻", "轻吻"]

    def func(self):
        if not self.args:
            self.caller.msg("你想亲吻谁？")
            return
        self.caller.location.msg_contents(f"{self.caller.name} 亲吻了 {self.args}。")
        self.caller.msg(f"你亲吻了 {self.args}。")


class CmdBow(ChineseCommand):
    __doc__ = "鞠躬行礼"
    key = "鞠躬"
    aliases = ["bow", "行礼", "作揖", "抱拳", "拱手", "躬身", "欠身", "一躬到地"]

    def func(self):
        if self.args:
            self.caller.location.msg_contents(f"{self.caller.name} 向 {self.args} 鞠了一躬。")
            self.caller.msg(f"你向 {self.args} 鞠了一躬。")
        else:
            self.caller.location.msg_contents(f"{self.caller.name} 鞠了一躬。")
            self.caller.msg("你鞠了一躬。")


class CmdKneel(ChineseCommand):
    __doc__ = "跪下"
    key = "跪下"
    aliases = ["kneel", "跪", "跪倒", "跪地", "下跪", "屈膝"]

    def func(self):
        if self.args:
            self.caller.location.msg_contents(f"{self.caller.name} 向 {self.args} 跪了下来。")
            self.caller.msg(f"你向 {self.args} 跪了下来。")
        else:
            self.caller.location.msg_contents(f"{self.caller.name} 跪了下来。")
            self.caller.msg("你跪了下来。")


class CmdKowtow(ChineseCommand):
    __doc__ = "磕头"
    key = "磕头"
    aliases = ["kowtow", "叩首", "叩头", "磕了个头", "拜倒", "纳头便拜"]

    def func(self):
        if self.args:
            self.caller.location.msg_contents(f"{self.caller.name} 向 {self.args} 磕了几个响头。")
            self.caller.msg(f"你向 {self.args} 磕了几个响头。")
        else:
            self.caller.location.msg_contents(f"{self.caller.name} 重重地磕了几个响头。")
            self.caller.msg("你重重地磕了几个响头。")


# =============================================================================
# 七、体态指令
# =============================================================================

class CmdSit(ChineseCommand):
    __doc__ = "坐下"
    key = "坐"
    aliases = ["sit", "坐下", "端坐", "盘腿坐", "席地而坐"]

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.name} 坐了下来。")
        self.caller.msg("你坐了下来。")


class CmdStand(ChineseCommand):
    __doc__ = "站起来"
    key = "站"
    aliases = ["stand", "站起来", "起身", "起立", "站立", "笔直站立"]

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.name} 站了起来。")
        self.caller.msg("你站了起来。")


class CmdLie(ChineseCommand):
    __doc__ = "躺下"
    key = "躺"
    aliases = ["lie", "躺下", "侧卧", "仰卧", "俯卧", "躺倒", "卧倒"]

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.name} 躺了下来。")
        self.caller.msg("你躺了下来。")


class CmdSquat(ChineseCommand):
    __doc__ = "蹲下"
    key = "蹲"
    aliases = ["squat", "蹲下", "蹲着", "蹲伏"]

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.name} 蹲了下来。")
        self.caller.msg("你蹲了下来。")


class CmdCrawl(ChineseCommand):
    __doc__ = "爬行"
    key = "爬"
    aliases = ["crawl", "爬行", "趴下", "匍匐", "爬着"]

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.name} 趴下开始爬行。")
        self.caller.msg("你趴下开始爬行。")


class CmdSleep(ChineseCommand):
    __doc__ = "睡觉"
    key = "睡"
    aliases = ["sleep", "睡觉", "睡着", "入睡", "躺下睡觉", "安睡"]

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.name} 躺下睡着了。")
        self.caller.msg("你躺下睡着了。")


class CmdHide(ChineseCommand):
    __doc__ = "躲藏"
    key = "藏"
    aliases = ["hide", "躲藏", "躲", "躲起来", "隐藏", "藏起来", "猫着"]

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.name} 躲了起来。")
        self.caller.msg("你躲了起来。")


class CmdJump(ChineseCommand):
    __doc__ = "跳"
    key = "跳"
    aliases = ["jump", "跳跃", "蹦", "跳起来", "蹦跳", "跳了一下"]

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.name} 跳了起来。")
        self.caller.msg("你跳了起来。")


class CmdRun(ChineseCommand):
    __doc__ = "奔跑"
    key = "跑"
    aliases = ["run", "奔跑", "跑起来", "飞奔", "狂奔", "跑着"]

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.name} 跑了起来。")
        self.caller.msg("你跑了起来。")


class CmdWalk(ChineseCommand):
    __doc__ = "走"
    key = "走"
    aliases = ["walk", "走路", "行走", "踱步", "散步", "溜达", "信步", "慢走"]

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.name} 走了起来。")
        self.caller.msg("你走了起来。")


# =============================================================================
# 八、表情/肢体动作指令
# =============================================================================

class CmdSigh(ChineseCommand):
    __doc__ = "叹气"
    key = "叹气"
    aliases = ["sigh", "叹息", "长叹", "唉", "哎", "唉声叹气", "叹了口气", "长叹一声", "深深叹气", "叹道"]

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.name} 叹了口气。")
        self.caller.msg("你叹了口气。")


class CmdYawn(ChineseCommand):
    __doc__ = "打哈欠"
    key = "打哈欠"
    aliases = ["yawn", "哈欠", "打了个哈欠", "伸懒腰", "伸了个懒腰", "哈欠连天"]

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.name} 打了个哈欠。")
        self.caller.msg("你打了个哈欠。")


class CmdSing(ChineseCommand):
    __doc__ = "唱歌"
    key = "唱"
    aliases = ["sing", "唱歌", "歌唱", "哼唱", "哼", "高歌一曲", "唱了起来", "引吭高歌"]

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.name} 唱起歌来。")
        self.caller.msg("你唱起歌来。")


class CmdDance(ChineseCommand):
    __doc__ = "跳舞"
    key = "跳舞"
    aliases = ["dance", "舞", "舞蹈", "翩翩起舞", "跳起舞来", "手舞足蹈", "舞动"]

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.name} 跳起舞来。")
        self.caller.msg("你跳起舞来。")


class CmdWhistle(ChineseCommand):
    __doc__ = "吹口哨"
    key = "吹口哨"
    aliases = ["whistle", "口哨", "吹哨", "吹了一声口哨", "吹起口哨", "吹着口哨"]

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.name} 吹起了口哨。")
        self.caller.msg("你吹起了口哨。")


class CmdShrug(ChineseCommand):
    __doc__ = "耸肩"
    key = "耸肩"
    aliases = ["shrug", "耸耸肩", "耸了耸肩", "摊手"]

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.name} 耸了耸肩。")
        self.caller.msg("你耸了耸肩。")


class CmdPoint(ChineseCommand):
    __doc__ = "指向"
    key = "指"
    aliases = ["point", "指向", "指着", "指了指", "指点", "指去"]

    def func(self):
        if not self.args:
            self.caller.msg("你想指什么？")
            return
        self.caller.location.msg_contents(f"{self.caller.name} 指了指 {self.args}。")
        self.caller.msg(f"你指了指 {self.args}。")


class CmdWink(ChineseCommand):
    __doc__ = "眨眼"
    key = "眨眼"
    aliases = ["wink", "眨眨眼", "眨了眨眼", "抛了个媚眼", "使眼色", "挤眼", "眨了一下眼"]

    def func(self):
        if self.args:
            self.caller.location.msg_contents(f"{self.caller.name} 朝 {self.args} 眨了眨眼。")
            self.caller.msg(f"你朝 {self.args} 眨了眨眼。")
        else:
            self.caller.location.msg_contents(f"{self.caller.name} 眨了眨眼。")
            self.caller.msg("你眨了眨眼。")


class CmdBlink(ChineseCommand):
    __doc__ = "闭眼"
    key = "闭眼"
    aliases = ["blink", "闭上眼睛", "合眼", "闭目", "闭目养神", "紧闭双眼", "闭眼休息"]

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.name} 闭上了眼睛。")
        self.caller.msg("你闭上了眼睛。")


class CmdRubEyes(ChineseCommand):
    __doc__ = "揉眼睛"
    key = "揉眼"
    aliases = ["rub_eyes", "揉眼睛", "揉了揉眼睛", "揉揉眼", "揉揉眼睛", "揉眼细看"]

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.name} 揉了揉眼睛。")
        self.caller.msg("你揉了揉眼睛。")


class CmdScratchHead(ChineseCommand):
    __doc__ = "挠头"
    key = "挠头"
    aliases = ["scratch_head", "挠了挠头", "挠挠头", "抓头", "抓抓头", "搔头", "摸头发", "摸下巴"]

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.name} 挠了挠头。")
        self.caller.msg("你挠了挠头。")


class CmdRubHands(ChineseCommand):
    __doc__ = "搓手"
    key = "搓手"
    aliases = ["rub_hands", "搓搓手", "搓了搓手", "搓手取暖", "搓着手", "摩拳擦掌"]

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.name} 搓了搓手。")
        self.caller.msg("你搓了搓手。")


class CmdStretch(ChineseCommand):
    __doc__ = "伸懒腰"
    key = "伸懒腰"
    aliases = ["stretch", "伸了个懒腰", "伸伸懒腰", "伸腰", "舒展身体", "伸展四肢", "活动筋骨"]

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.name} 伸了个懒腰。")
        self.caller.msg("你伸了个懒腰。")


class CmdFacepalm(ChineseCommand):
    __doc__ = "扶额/捂脸"
    key = "扶额"
    aliases = ["facepalm", "捂脸", "捂住了脸", "掩面", "以手扶额", "扶额叹息", "扶额无语"]

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.name} 扶额叹息。")
        self.caller.msg("你扶额叹息。")


class CmdCoverMouth(ChineseCommand):
    __doc__ = "捂嘴"
    key = "捂嘴"
    aliases = ["cover_mouth", "捂住嘴", "捂着嘴", "捂嘴偷笑", "捂嘴笑", "捂嘴惊呼"]

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.name} 捂住了嘴。")
        self.caller.msg("你捂住了嘴。")


class CmdArmsCrossed(ChineseCommand):
    __doc__ = "抱胸"
    key = "抱胸"
    aliases = ["arms_crossed", "双手抱胸", "抱臂", "双手抱臂", "抱起胳膊", "抄着手", "袖手"]

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.name} 双手抱胸。")
        self.caller.msg("你双手抱胸。")


class CmdAkimbo(ChineseCommand):
    __doc__ = "叉腰"
    key = "叉腰"
    aliases = ["akimbo", "双手叉腰", "手叉腰", "叉着腰", "掐腰"]

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.name} 双手叉腰。")
        self.caller.msg("你双手叉腰。")


class CmdHandsBehindBack(ChineseCommand):
    __doc__ = "背手"
    key = "背手"
    aliases = ["hands_behind", "背着手", "手背在身后", "双手背后", "负手", "负手而立", "倒背着手"]

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.name} 双手背在身后。")
        self.caller.msg("你双手背在身后。")


class CmdOpenArms(ChineseCommand):
    __doc__ = "张开双臂"
    key = "张开双臂"
    aliases = ["open_arms", "张开双手", "张开怀抱", "展开双臂", "伸出双臂", "敞开怀抱"]

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.name} 张开了双臂。")
        self.caller.msg("你张开了双臂。")


# =============================================================================
# 九、生理行为指令
# =============================================================================

class CmdShit(ChineseCommand):
    __doc__ = "拉屎"
    key = "拉屎"
    aliases = ["shit", "大便", "排便", "出恭", "解手", "方便", "蹲坑"]

    def func(self):
        self.caller.location.msg_contents(
            f"{self.caller.name} 蹲在角落里拉了一泡屎，空气中弥漫着臭味。"
        )
        self.caller.msg("你蹲在角落里拉了一泡屎，顿时感觉浑身轻松。")


class CmdPee(ChineseCommand):
    __doc__ = "拉尿"
    key = "拉尿"
    aliases = ["pee", "小便", "撒尿", "尿尿", "解手", "方便", "放水"]

    def func(self):
        self.caller.location.msg_contents(
            f"{self.caller.name} 走到墙角撒了一泡尿。"
        )
        self.caller.msg("你走到墙角撒了一泡尿，舒服多了。")


class CmdSpit(ChineseCommand):
    __doc__ = "吐口水"
    key = "吐"
    aliases = ["spit", "吐口水", "啐", "啐了一口", "唾", "吐痰"]

    def func(self):
        if self.args:
            self.caller.location.msg_contents(f"{self.caller.name} 朝 {self.args} 吐了一口口水。")
            self.caller.msg(f"你朝 {self.args} 吐了一口口水。")
        else:
            self.caller.location.msg_contents(f"{self.caller.name} 吐了一口口水。")
            self.caller.msg("你吐了一口口水。")


class CmdVomit(ChineseCommand):
    __doc__ = "呕吐"
    key = "呕吐"
    aliases = ["vomit", "吐了", "干呕", "呕", "吐了一地", "作呕"]

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.name} 呕吐了起来。")
        self.caller.msg("你呕吐了起来，胃里翻江倒海。")


class CmdSneeze(ChineseCommand):
    __doc__ = "打喷嚏"
    key = "打喷嚏"
    aliases = ["sneeze", "喷嚏", "阿嚏", "打了个喷嚏", "打了一个喷嚏"]

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.name} 打了个喷嚏——阿嚏！")
        self.caller.msg("你打了个喷嚏——阿嚏！")


class CmdCough(ChineseCommand):
    __doc__ = "咳嗽"
    key = "咳嗽"
    aliases = ["cough", "咳", "咳了几声", "咳了一声", "干咳", "咳个不停"]

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.name} 咳了几声。")
        self.caller.msg("你咳了几声。")


class CmdSweat(ChineseCommand):
    __doc__ = "抹汗"
    key = "抹汗"
    aliases = ["sweat", "擦汗", "抹了抹汗", "擦了擦汗", "满头大汗", "汗流浃背"]

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.name} 抹了抹额头上的汗。")
        self.caller.msg("你抹了抹额头上的汗。")


class CmdShiver(ChineseCommand):
    __doc__ = "发抖"
    key = "发抖"
    aliases = ["shiver", "发抖", "打颤", "瑟瑟发抖", "哆嗦", "浑身发抖", "颤抖", "战栗"]

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.name} 浑身发抖。")
        self.caller.msg("你浑身发抖。")


# =============================================================================
# 十、战斗指令
# =============================================================================

class CmdHit(ChineseCommand):
    __doc__ = "打某人"
    key = "打"
    aliases = ["hit", "揍", "打人", "挥拳", "打了", "揍了", "殴打", "拳打", "抡起拳头"]

    def func(self):
        if not self.args:
            self.caller.msg("你想打谁？")
            return
        self.caller.location.msg_contents(f"{self.caller.name} 挥拳打了 {self.args}！")
        self.caller.msg(f"你挥拳打了 {self.args}！")


class CmdKick(ChineseCommand):
    __doc__ = "踢某人"
    key = "踢"
    aliases = ["kick", "踹", "踢了", "踢了一脚", "飞踢", "一脚踢去", "踢飞"]

    def func(self):
        if not self.args:
            self.caller.msg("你想踢谁？")
            return
        self.caller.location.msg_contents(f"{self.caller.name} 一脚踢向 {self.args}！")
        self.caller.msg(f"你一脚踢向 {self.args}！")


class CmdSlap(ChineseCommand):
    __doc__ = "扇耳光"
    key = "扇耳光"
    aliases = ["slap", "扇", "扇了一巴掌", "打耳光", "啪", "抽耳光", "扇了"]

    def func(self):
        if not self.args:
            self.caller.msg("你想扇谁耳光？")
            return
        self.caller.location.msg_contents(f"{self.caller.name} 啪地扇了 {self.args} 一记耳光！")
        self.caller.msg(f"你啪地扇了 {self.args} 一记耳光！")


class CmdPoke(ChineseCommand):
    __doc__ = "戳某人"
    key = "戳"
    aliases = ["poke", "戳了戳", "戳了一下", "捅", "捅了捅", "戳了"]

    def func(self):
        if not self.args:
            self.caller.msg("你想戳谁？")
            return
        self.caller.location.msg_contents(f"{self.caller.name} 戳了戳 {self.args}。")
        self.caller.msg(f"你戳了戳 {self.args}。")


class CmdPinch(ChineseCommand):
    __doc__ = "掐/拧某人"
    key = "掐"
    aliases = ["pinch", "拧", "捏", "掐了一下", "拧了拧", "拧耳朵", "揪头发"]

    def func(self):
        if not self.args:
            self.caller.msg("你想掐谁？")
            return
        self.caller.location.msg_contents(f"{self.caller.name} 掐了 {self.args} 一下。")
        self.caller.msg(f"你掐了 {self.args} 一下。")


class CmdPushPerson(ChineseCommand):
    __doc__ = "推人"
    key = "推人"
    aliases = ["push_person", "推开", "推了", "推搡", "推了一把", "用力推"]

    def func(self):
        if not self.args:
            self.caller.msg("你想推谁？")
            return
        self.caller.location.msg_contents(f"{self.caller.name} 用力推了 {self.args} 一把。")
        self.caller.msg(f"你用力推了 {self.args} 一把。")


class CmdPullPerson(ChineseCommand):
    __doc__ = "拉人"
    key = "拉人"
    aliases = ["pull_person", "拉住", "拉了一把", "拉过来", "拽", "拽住", "拉着手"]

    def func(self):
        if not self.args:
            self.caller.msg("你想拉谁？")
            return
        self.caller.location.msg_contents(f"{self.caller.name} 拉住了 {self.args}。")
        self.caller.msg(f"你拉住了 {self.args}。")


# =============================================================================
# 十一、经济/社交互动指令
# =============================================================================

class CmdBeg(ChineseCommand):
    __doc__ = "乞讨"
    key = "乞讨"
    aliases = ["beg", "讨钱", "要饭", "讨饭", "行乞", "乞求", "哀求", "求"]

    def func(self):
        if not self.args:
            self.caller.location.msg_contents(
                f"{self.caller.name} 跪在地上向周围的人乞讨。"
            )
            self.caller.msg("你跪在地上向周围的人乞讨。")
        else:
            self.caller.location.msg_contents(
                f"{self.caller.name} 向 {self.args} 乞讨。"
            )
            self.caller.msg(f"你向 {self.args} 乞讨。")


class CmdPay(ChineseCommand):
    __doc__ = "付钱"
    key = "付钱"
    aliases = ["pay", "付款", "给钱", "付账", "付", "数钱", "掏钱", "交钱"]

    def func(self):
        if not self.args:
            self.caller.msg("你想付多少钱给谁？格式：付钱 <金额> 给 <目标>")
            return
        self.caller.location.msg_contents(f"{self.caller.name} 掏出钱来。")
        self.caller.msg(f"你掏出钱来。")


class CmdSteal(ChineseCommand):
    __doc__ = "偷窃"
    key = "偷"
    aliases = ["steal", "偷窃", "偷东西", "扒窃", "顺手牵羊", "偷了", "盗窃"]

    def func(self):
        if not self.args:
            self.caller.msg("你想偷什么？")
            return
        self.caller.location.msg_contents(
            f"{self.caller.name} 鬼鬼祟祟地靠近 {self.args}……"
        )
        self.caller.msg(f"你鬼鬼祟祟地靠近 {self.args}……")


# =============================================================================
# 十二、环境交互指令
# =============================================================================

class CmdOpen(ChineseCommand):
    __doc__ = "打开某物"
    key = "打开"
    aliases = ["open", "开启", "开", "拧开", "推开", "推开", "掀开"]

    def func(self):
        if not self.args:
            self.caller.msg("你想打开什么？")
            return
        self.caller.execute_cmd(f"open {self.args}")


class CmdClose(ChineseCommand):
    __doc__ = "关闭某物"
    key = "关闭"
    aliases = ["close", "关", "关上", "合上", "闭上", "拉上", "盖住"]

    def func(self):
        if not self.args:
            self.caller.msg("你想关闭什么？")
            return
        self.caller.execute_cmd(f"close {self.args}")


class CmdPush(ChineseCommand):
    __doc__ = "推某物"
    key = "推"
    aliases = ["push", "推开", "推动", "推门", "推了推", "推倒"]

    def func(self):
        if not self.args:
            self.caller.msg("你想推什么？")
            return
        self.caller.location.msg_contents(f"{self.caller.name} 推了推 {self.args}。")
        self.caller.msg(f"你推了推 {self.args}。")


class CmdPull(ChineseCommand):
    __doc__ = "拉某物"
    key = "拉"
    aliases = ["pull", "拉动", "拽", "拉开", "拉绳子", "拉环", "拉杆"]

    def func(self):
        if not self.args:
            self.caller.msg("你想拉什么？")
            return
        self.caller.location.msg_contents(f"{self.caller.name} 拉了拉 {self.args}。")
        self.caller.msg(f"你拉了拉 {self.args}。")


class CmdDig(ChineseCommand):
    __doc__ = "挖"
    key = "挖"
    aliases = ["dig", "挖掘", "铲", "刨", "挖土", "挖坑", "挖洞", "掘"]

    def func(self):
        if self.args:
            self.caller.location.msg_contents(f"{self.caller.name} 开始挖 {self.args}。")
            self.caller.msg(f"你开始挖 {self.args}。")
        else:
            self.caller.location.msg_contents(f"{self.caller.name} 在地上挖了起来。")
            self.caller.msg("你在地上挖了起来。")


class CmdBury(ChineseCommand):
    __doc__ = "埋"
    key = "埋"
    aliases = ["bury", "掩埋", "埋起来", "填埋", "埋了", "埋掉"]

    def func(self):
        if not self.args:
            self.caller.msg("你想埋什么？")
            return
        self.caller.location.msg_contents(f"{self.caller.name} 把 {self.args} 埋了起来。")
        self.caller.msg(f"你把 {self.args} 埋了起来。")


class CmdBurn(ChineseCommand):
    __doc__ = "烧"
    key = "烧"
    aliases = ["burn", "焚烧", "烧掉", "烧了", "点燃", "烧毁", "纵火", "放火"]

    def func(self):
        if not self.args:
            self.caller.msg("你想烧什么？")
            return
        self.caller.location.msg_contents(f"{self.caller.name} 点燃了 {self.args}。")
        self.caller.msg(f"你点燃了 {self.args}。")


class CmdLightFire(ChineseCommand):
    __doc__ = "生火/点火"
    key = "生火"
    aliases = ["light_fire", "点火", "生火", "点燃", "烧火", "点起篝火", "点起火堆", "烤火"]

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.name} 生起了一堆火。")
        self.caller.msg("你生起了一堆火，火焰噼啪作响。")


class CmdExtinguish(ChineseCommand):
    __doc__ = "熄灭"
    key = "熄灭"
    aliases = ["extinguish", "灭", "熄灭", "吹灭", "扑灭", "灭火", "浇灭", "熄火"]

    def func(self):
        if not self.args:
            self.caller.msg("你想熄灭什么？")
            return
        self.caller.location.msg_contents(f"{self.caller.name} 熄灭了 {self.args}。")
        self.caller.msg(f"你熄灭了 {self.args}。")


class CmdFish(ChineseCommand):
    __doc__ = "钓鱼"
    key = "钓鱼"
    aliases = ["fish", "垂钓", "钓鱼", "撒网", "下网", "捕鱼"]

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.name} 开始钓鱼。")
        self.caller.msg("你开始钓鱼。")


class CmdRead(ChineseCommand):
    __doc__ = "读书"
    key = "读书"
    aliases = ["read", "读", "阅读", "看书", "翻阅", "浏览", "翻看", "研读", "诵读"]

    def func(self):
        if not self.args:
            self.caller.msg("你想读什么？")
            return
        self.caller.location.msg_contents(f"{self.caller.name} 开始读 {self.args}。")
        self.caller.msg(f"你开始读 {self.args}。")


class CmdWrite(ChineseCommand):
    __doc__ = "写字"
    key = "写字"
    aliases = ["write", "写", "书写", "记下", "写下", "记录", "刻", "刻画", "题字", "涂写"]

    def func(self):
        if not self.args:
            self.caller.msg("你想写什么？")
            return
        self.caller.location.msg_contents(f"{self.caller.name} 写下了些什么。")
        self.caller.msg(f"你写下了：{self.args}")


class CmdRepair(ChineseCommand):
    __doc__ = "修理"
    key = "修理"
    aliases = ["repair", "修", "修复", "维修", "修补", "补", "修好"]

    def func(self):
        if not self.args:
            self.caller.msg("你想修理什么？")
            return
        self.caller.location.msg_contents(f"{self.caller.name} 开始修理 {self.args}。")
        self.caller.msg(f"你开始修理 {self.args}。")


class CmdDestroy(ChineseCommand):
    __doc__ = "破坏"
    key = "破坏"
    aliases = ["destroy", "摧毁", "砸", "砸烂", "砸碎", "摔", "撕", "扯", "拆", "拆掉"]

    def func(self):
        if not self.args:
            self.caller.msg("你想破坏什么？")
            return
        self.caller.location.msg_contents(f"{self.caller.name} 开始破坏 {self.args}！")
        self.caller.msg(f"你开始破坏 {self.args}！")


class CmdUse(ChineseCommand):
    __doc__ = "使用物品"
    key = "使用"
    aliases = ["use", "用", "使用", "运用", "动用"]

    def func(self):
        if not self.args:
            self.caller.msg("你想使用什么？")
            return
        self.caller.execute_cmd(f"use {self.args}")


class CmdSearch(ChineseCommand):
    __doc__ = "搜索"
    key = "搜索"
    aliases = ["search", "搜寻", "查找", "翻找", "翻", "搜", "寻找", "找", "搜查", "搜身"]

    def func(self):
        if self.args:
            self.caller.location.msg_contents(f"{self.caller.name} 开始搜索 {self.args}。")
            self.caller.msg(f"你开始搜索 {self.args}。")
        else:
            self.caller.location.msg_contents(f"{self.caller.name} 四处搜索着。")
            self.caller.msg("你四处搜索着。")


class CmdCut(ChineseCommand):
    __doc__ = "剪/切"
    key = "剪"
    aliases = ["cut", "切", "割", "砍", "劈", "剪开", "切开", "割开", "剁", "削"]

    def func(self):
        if not self.args:
            self.caller.msg("你想剪什么？")
            return
        self.caller.location.msg_contents(f"{self.caller.name} 剪开了 {self.args}。")
        self.caller.msg(f"你剪开了 {self.args}。")


class CmdStick(ChineseCommand):
    __doc__ = "贴"
    key = "贴"
    aliases = ["stick", "粘贴", "贴上去", "贴上", "张贴", "贴住", "贴在"]

    def func(self):
        if not self.args:
            self.caller.msg("你想贴什么？")
            return
        self.caller.location.msg_contents(f"{self.caller.name} 贴上了 {self.args}。")
        self.caller.msg(f"你贴上了 {self.args}。")


class CmdDaub(ChineseCommand):
    __doc__ = "涂抹"
    key = "涂"
    aliases = ["daub", "涂抹", "擦", "刷", "涂上", "抹上", "抹", "涂改", "污损"]

    def func(self):
        if not self.args:
            self.caller.msg("你想涂什么？")
            return
        self.caller.location.msg_contents(f"{self.caller.name} 涂了涂 {self.args}。")
        self.caller.msg(f"你涂了涂 {self.args}。")


class CmdWash(ChineseCommand):
    __doc__ = "洗"
    key = "洗"
    aliases = ["wash", "清洗", "冲洗", "洗涤", "洗刷", "涮", "漂洗", "洗手", "洗脸", "洗澡"]

    def func(self):
        if not self.args:
            self.caller.msg("你想洗什么？")
            return
        self.caller.location.msg_contents(f"{self.caller.name} 开始洗 {self.args}。")
        self.caller.msg(f"你开始洗 {self.args}。")


class CmdSweep(ChineseCommand):
    __doc__ = "扫"
    key = "扫"
    aliases = ["sweep", "清扫", "打扫", "扫除", "扫地", "扫干净", "扫一扫"]

    def func(self):
        if self.args:
            self.caller.location.msg_contents(f"{self.caller.name} 开始扫 {self.args}。")
            self.caller.msg(f"你开始扫 {self.args}。")
        else:
            self.caller.location.msg_contents(f"{self.caller.name} 开始打扫。")
            self.caller.msg("你开始打扫。")


# =============================================================================
# 十三、特殊状态指令
# =============================================================================

class CmdPlayDead(ChineseCommand):
    __doc__ = "装死"
    key = "装死"
    aliases = ["play_dead", "假装死", "装死", "躺尸", "装尸体"]

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.name} 突然倒地，一动不动，像是死了。")
        self.caller.msg("你突然倒地，一动不动，假装死了。")


class CmdPlaySleep(ChineseCommand):
    __doc__ = "装睡"
    key = "装睡"
    aliases = ["play_sleep", "假装睡", "装睡", "假寐", "闭眼装睡", "打呼噜"]

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.name} 闭上眼睛，假装睡着了。")
        self.caller.msg("你闭上眼睛，假装睡着了。")


class CmdFan(ChineseCommand):
    __doc__ = "扇风"
    key = "扇风"
    aliases = ["fan", "扇扇子", "扇风", "扇了扇", "挥扇", "扇凉"]

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.name} 扇了扇风。")
        self.caller.msg("你扇了扇风。")


class CmdPray(ChineseCommand):
    __doc__ = "祈祷"
    key = "祈祷"
    aliases = ["pray", "祷告", "祈求", "默祷", "许愿", "祝祷", "拜"]

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.name} 双手合十，默默祈祷。")
        self.caller.msg("你双手合十，默默祈祷。")


# =============================================================================
# 十四、地图指令
# =============================================================================

class CmdMap(ChineseCommand):
    """
    查看地图

    用法:
      地图              - 查看世界地图
      地图 世界         - 查看世界地图
      地图 区域         - 查看区域地图（周边）
      地图 本地         - 查看本地地图（当前房间及出口）
      map              - 同上
    """
    __doc__ = "查看地图"
    key = "地图"
    aliases = ["map", "查看地图", "世界地图", "区域地图", "本地地图"]

    def func(self):
        from world.map import show_map
        zoom = self.args.strip() if self.args else "世界"
        show_map(self.caller, zoom)


# =============================================================================
# 十五、命令集
# =============================================================================

from evennia import CmdSet


class ChineseCmdSet(CmdSet):
    """
    中文指令集，包含所有中文命令。
    在 CharacterCmdSet 中合并此命令集即可启用中文指令。
    """
    key = "ChineseCmdSet"

    def at_cmdset_creation(self):
        # 移动
        self.add(CmdEast())
        self.add(CmdWest())
        self.add(CmdSouth())
        self.add(CmdNorth())
        self.add(CmdNortheast())
        self.add(CmdNorthwest())
        self.add(CmdSoutheast())
        self.add(CmdSouthwest())
        self.add(CmdUp())
        self.add(CmdDown())
        self.add(CmdEnter())
        self.add(CmdExit())

        # 观察
        self.add(CmdLook())

        # 物品交互
        self.add(CmdGet())
        self.add(CmdDrop())
        self.add(CmdGive())
        self.add(CmdPut())
        self.add(CmdInventory())

        # 饮食
        self.add(CmdEat())
        self.add(CmdDrink())

        # 装备
        self.add(CmdWear())
        self.add(CmdRemove())
        self.add(CmdWield())

        # 社交表情
        self.add(CmdSpeak())
        self.add(CmdShout())
        self.add(CmdWhisper())
        self.add(CmdLaugh())
        self.add(CmdCry())
        self.add(CmdSmile())
        self.add(CmdNod())
        self.add(CmdShakeHead())
        self.add(CmdWave())
        self.add(CmdClap())
        self.add(CmdHug())
        self.add(CmdKiss())
        self.add(CmdBow())
        self.add(CmdKneel())
        self.add(CmdKowtow())

        # 体态
        self.add(CmdSit())
        self.add(CmdStand())
        self.add(CmdLie())
        self.add(CmdSquat())
        self.add(CmdCrawl())
        self.add(CmdSleep())
        self.add(CmdHide())
        self.add(CmdJump())
        self.add(CmdRun())
        self.add(CmdWalk())

        # 表情/肢体动作
        self.add(CmdSigh())
        self.add(CmdYawn())
        self.add(CmdSing())
        self.add(CmdDance())
        self.add(CmdWhistle())
        self.add(CmdShrug())
        self.add(CmdPoint())
        self.add(CmdWink())
        self.add(CmdBlink())
        self.add(CmdRubEyes())
        self.add(CmdScratchHead())
        self.add(CmdRubHands())
        self.add(CmdStretch())
        self.add(CmdFacepalm())
        self.add(CmdCoverMouth())
        self.add(CmdArmsCrossed())
        self.add(CmdAkimbo())
        self.add(CmdHandsBehindBack())
        self.add(CmdOpenArms())

        # 生理行为
        self.add(CmdShit())
        self.add(CmdPee())
        self.add(CmdSpit())
        self.add(CmdVomit())
        self.add(CmdSneeze())
        self.add(CmdCough())
        self.add(CmdSweat())
        self.add(CmdShiver())

        # 战斗
        self.add(CmdHit())
        self.add(CmdKick())
        self.add(CmdSlap())
        self.add(CmdPoke())
        self.add(CmdPinch())
        self.add(CmdPushPerson())
        self.add(CmdPullPerson())

        # 经济/社交互动
        self.add(CmdBeg())
        self.add(CmdPay())
        self.add(CmdSteal())

        # 环境交互
        self.add(CmdOpen())
        self.add(CmdClose())
        self.add(CmdPush())
        self.add(CmdPull())
        self.add(CmdDig())
        self.add(CmdBury())
        self.add(CmdBurn())
        self.add(CmdLightFire())
        self.add(CmdExtinguish())
        self.add(CmdFish())
        self.add(CmdRead())
        self.add(CmdWrite())
        self.add(CmdRepair())
        self.add(CmdDestroy())
        self.add(CmdUse())
        self.add(CmdSearch())
        self.add(CmdCut())
        self.add(CmdStick())
        self.add(CmdDaub())
        self.add(CmdWash())
        self.add(CmdSweep())

        # 特殊状态
        self.add(CmdPlayDead())
        self.add(CmdPlaySleep())
        self.add(CmdFan())
        self.add(CmdPray())

        # 地图
        self.add(CmdMap())