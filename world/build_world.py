"""
古代扬州世界构建脚本

以唐代扬州为中心，模拟真实中国古代地理，
覆盖扬州城及周边数十座城池，包含官道、水路、山野等场景。

地图范围：
  北至长安、洛阳，南至杭州，东至东海，西至开封。
  以大运河和长江为水路枢纽。

运行方式:
    在 Evennia 中执行: @py from world.build_world import build; build()
"""

from evennia import create_object, search_object
from evennia.utils import create


# =============================================================================
# 房间描述模板
# =============================================================================

ROOMS = {
    # ── 扬州城 ──────────────────────────────────────
    "yangzhou_center": {
        "key": "扬州城中心",
        "desc": (
            "你站在扬州城的十字街口，青石板路四通八达。\n"
            "南北大街两旁店铺林立，酒旗招展，商贩叫卖声不绝于耳。\n"
            "这里是天下第一繁华之地，腰缠十万贯，骑鹤下扬州。\n"
            "东边是东市，西边是西市，南边通往码头，北边通向府衙。"
        ),
    },
    "yangzhou_east_market": {
        "key": "扬州东市",
        "desc": (
            "东市是扬州最热闹的集市，南北货物在此汇聚。\n"
            "波斯商人兜售着香料和珠宝，日本遣唐使好奇地打量着中原风物。\n"
            "空气中弥漫着丝绸、茶叶和药材的气息。\n"
            "东门外是通往泰州的官道，西边可回城中心。"
        ),
    },
    "yangzhou_west_market": {
        "key": "扬州西市",
        "desc": (
            "西市比东市略显清静，但同样商贾云集。\n"
            "这里以手工作坊为主，铁匠铺叮当作响，\n"
            "织坊里机杼声声，瓷器铺陈列着精美的越窑青瓷。\n"
            "西门外是前往仪征、合肥的官道，东边可回城中心。"
        ),
    },
    "yangzhou_wharf": {
        "key": "扬州码头",
        "desc": (
            "大运河畔的扬州码头，千帆竞渡，百舸争流。\n"
            "漕运船只满载着江南的稻米、丝绸和瓷器，\n"
            "准备北上运往东都洛阳。码头上力夫们喊着号子搬运货物。\n"
            "南边是瓜洲渡口，可渡江前往金陵；北边回城中心。"
        ),
    },
    "yangzhou_temple": {
        "key": "大明寺",
        "desc": (
            "大明寺坐落于扬州城西北的蜀冈之上，始建于南朝宋大明年间。\n"
            "寺内古木参天，钟声悠远，香烟缭绕。\n"
            "鉴真大师曾在此修行，后东渡日本传法。\n"
            "寺前可俯瞰扬州城全景，东南方向可回城中心。"
        ),
    },
    "yangzhou_lake": {
        "key": "瘦西湖",
        "desc": (
            "瘦西湖水波潋滟，两岸杨柳依依，亭台楼阁掩映在绿树丛中。\n"
            "湖面如一条碧绿的绸带蜿蜒曲折，比起杭州西湖更显清瘦秀丽。\n"
            "文人墨客常在此吟诗作对，画舫轻荡，丝竹声声。\n"
            "东南方向可回城中心。"
        ),
    },
    "yangzhou_garden": {
        "key": "个园",
        "desc": (
            "个园以竹石闻名，园中遍植翠竹，假山叠石巧夺天工。\n"
            "园名取自'竹'字的一半，清雅别致，是扬州盐商的私家园林。\n"
            "四季假山各具特色，春山如笑，夏山如滴，秋山如妆，冬山如睡。\n"
            "西边可回城中心。"
        ),
    },
    "yangzhou_inn": {
        "key": "扬州驿站",
        "desc": (
            "扬州驿站是官办驿馆，供来往官员和商旅歇息。\n"
            "驿卒们忙前忙后，马厩里拴着各色驿马。\n"
            "这里可以打听到各地的消息，也可以雇用马车出行。\n"
            "大堂里烧着炭火，供旅人取暖歇脚。"
        ),
    },
    "yangzhou_office": {
        "key": "扬州府衙",
        "desc": (
            "扬州府衙气象森严，朱漆大门两侧立着石狮。\n"
            "这里是扬州大都督府所在，管辖一方军政要务。\n"
            "门前衙役持刀而立，百姓不敢轻易靠近。\n"
            "南边是城中心十字街口。"
        ),
    },
    "yangzhou_tavern": {
        "key": "扬州酒楼",
        "desc": (
            "醉仙楼是扬州最有名的酒楼，三层楼阁临街而立。\n"
            "楼上觥筹交错，楼下说书人正讲着隋唐英雄传。\n"
            "这里的扬州炒饭和蟹粉狮子头远近闻名，\n"
            '店小二热情地招呼着："客官里面请！"'
        ),
    },

    # ── 扬州城门 ──────────────────────────────────
    "yangzhou_north_gate": {
        "key": "扬州北门",
        "desc": (
            "扬州北门高大雄伟，城墙上旌旗招展。\n"
            "守城士兵盘查着来往行人。\n"
            "北去官道直通高邮、淮安。\n"
            "南边通往扬州城中心。"
        ),
    },
    "yangzhou_east_gate": {
        "key": "扬州东门",
        "desc": (
            "扬州东门车水马龙，商旅络绎不绝。\n"
            "东去官道可达泰州、海安。\n"
            "城墙上可远眺运河帆影。\n"
            "西边通往扬州城中心。"
        ),
    },
    "yangzhou_south_gate": {
        "key": "扬州南门",
        "desc": (
            "扬州南门外便是浩荡的长江。\n"
            "城门上刻着'江淮重镇'四个大字。\n"
            "南下可至瓜洲渡口，渡江即达金陵。\n"
            "北边通往扬州城中心。"
        ),
    },
    "yangzhou_west_gate": {
        "key": "扬州西门",
        "desc": (
            "扬州西门略显冷清，多为行脚商人和赶考书生。\n"
            "西去官道可通仪征，再远可达合肥、开封。\n"
            "门外是一片青青的麦田，远处山峦起伏。\n"
            "东边通往扬州城中心。"
        ),
    },

    # ── 北方路线 ──────────────────────────────────
    "gaoyou": {
        "key": "高邮",
        "desc": (
            "高邮是一座古老的运河城市，以高邮湖和咸鸭蛋闻名。\n"
            "大运河穿城而过，河面上舟楫如梭。\n"
            "城北有一座秦代古驿——盂城驿，至今仍在沿用。\n"
            "南去扬州，北去淮安，运河两岸杨柳依依。"
        ),
    },
    "huaian": {
        "key": "淮安",
        "desc": (
            "淮安是漕运总督驻地，扼守运河和淮河交汇之处。\n"
            "这里是南北漕运的咽喉，城中粮仓连绵数里。\n"
            "韩信曾在此受胯下之辱，如今却成了繁华都会。\n"
            "南去高邮，北去徐州。"
        ),
    },
    "xuzhou": {
        "key": "徐州",
        "desc": (
            "徐州自古是兵家必争之地，城高池深，气势雄浑。\n"
            "楚汉相争时，项羽曾定都于此，号令天下。\n"
            "城头铁甲士兵往来巡逻，城中武风盛行。\n"
            "南去淮安，西去商丘，北望齐鲁大地。"
        ),
    },
    "luoyang": {
        "key": "洛阳",
        "desc": (
            "东都洛阳！大唐神都，天下之中！\n"
            "洛水穿城而过，天津桥上车水马龙。\n"
            "龙门石窟的佛像慈悲地俯瞰着这座千年帝都，\n"
            "白马寺的钟声每日清晨唤醒全城。\n"
            "这里汇聚了天下英才，是文人墨客向往的圣地。\n"
            "东去开封，西去长安，南望嵩山少林。"
        ),
    },
    "changan": {
        "key": "长安",
        "desc": (
            "长安——大唐帝国的首都，世界最宏伟的城市！\n"
            "朱雀大街宽达百步，直通皇城。\n"
            "东市西市汇聚天下奇珍，胡商蕃客摩肩接踵。\n"
            "大雁塔巍然矗立，玄奘法师从天竺取回的经卷珍藏于此。\n"
            "大明宫金碧辉煌，万国来朝，盛唐气象尽在此城。\n"
            "东去洛阳，一路潼关古道，山河壮丽。"
        ),
    },

    # ── 东北路线 ──────────────────────────────────
    "taizhou": {
        "key": "泰州",
        "desc": (
            "泰州是一座安静的江淮小城，以盐业和纺织闻名。\n"
            "城中河道纵横，小桥流水，颇有江南韵味。\n"
            "这里出产的盐洁白如雪，远销四方。\n"
            "西南去扬州，东北去海安。"
        ),
    },
    "haian": {
        "key": "海安",
        "desc": (
            "海安东临黄海，是重要的海盐产地。\n"
            "盐田一望无际，盐工们在烈日下辛勤劳作。\n"
            "海风吹来，带着咸腥的气息。\n"
            "西南去泰州，北去盐城，东可望海。"
        ),
    },
    "yancheng": {
        "key": "盐城",
        "desc": (
            "盐城顾名思义，以产盐著称，是江淮盐业的中心之一。\n"
            "城外盐田如棋盘般整齐排列，白花花的盐堆如小山。\n"
            "海风阵阵，吹得盐田边的芦苇沙沙作响。\n"
            "南去海安，此地已是东海之滨。"
        ),
    },

    # ── 东方路线 ──────────────────────────────────
    "tongzhou": {
        "key": "通州",
        "desc": (
            "通州是长江入海口的重要港口，海船云集。\n"
            "从这里可以乘船出海，前往日本、新罗。\n"
            "码头上外商云集，说着各种听不懂的语言。\n"
            "西去扬州，东去海门。"
        ),
    },
    "haimen": {
        "key": "海门",
        "desc": (
            "海门是长江入海的门户，江海交汇之处波滔汹涌。\n"
            "这里是渔民的家园，渔船星罗棋布。\n"
            "极目远眺，海天一色，望不到尽头。\n"
            "西去通州，东面是茫茫大海。"
        ),
    },
    "east_sea": {
        "key": "东海之滨",
        "desc": (
            "你站在东海之滨，脚下是金色的沙滩，眼前是浩瀚的汪洋。\n"
            "海浪拍打着礁石，溅起白色的浪花。\n"
            "海鸥在天空盘旋鸣叫，远处隐约可见几艘渔船。\n"
            "据说，海的那边是日本国和新罗国。\n"
            "西去海门，回到大陆。"
        ),
    },

    # ── 东南路线 ──────────────────────────────────
    "guazhou": {
        "key": "瓜洲渡",
        "desc": (
            "瓜洲渡是长江上最重要的渡口之一。\n"
            '王安石曾在此写下："京口瓜洲一水间，钟山只隔数重山。"\n'
            "渡口大小船只往来穿梭，渡江之人络绎不绝。\n"
            "北去扬州，南渡长江可达镇江，远眺对岸青山如黛。"
        ),
    },
    "zhenjiang": {
        "key": "镇江",
        "desc": (
            "镇江古称京口，是长江南岸的重镇。\n"
            "金山寺屹立江中，白蛇传中水漫金山的传说就发生于此。\n"
            "北固山险峻雄奇，甘露寺刘备招亲的故事流传千古。\n"
            "北渡瓜洲可达扬州，东南去苏州，西南去金陵。"
        ),
    },
    "suzhou": {
        "key": "苏州",
        "desc": (
            "上有天堂，下有苏杭！苏州之美，冠绝江南。\n"
            "小桥流水，粉墙黛瓦，吴侬软语，处处是画。\n"
            "丝绸华美无双，刺绣巧夺天工。\n"
            "寒山寺的钟声传到客船，枫桥夜泊的诗意千年不散。\n"
            "西北去镇江，南去杭州。"
        ),
    },
    "hangzhou": {
        "key": "杭州",
        "desc": (
            "杭州！江南第一名城，人间天堂！\n"
            "西湖十景美不胜收，断桥残雪，苏堤春晓，三潭印月……\n"
            "钱塘江潮汹涌澎湃，每年八月十八引来无数观潮人。\n"
            "灵隐寺钟声悠远，龙井茶香飘四方。\n"
            "北去苏州，这里已是江南的尽头。"
        ),
    },

    # ── 南方路线 ──────────────────────────────────
    "jinling": {
        "key": "金陵城",
        "desc": (
            "金陵，六朝古都，龙盘虎踞之地！\n"
            "石头城雄踞长江之畔，钟山风雨起苍黄。\n"
            "秦淮河上画舫如织，桨声灯影里尽是风流韵事。\n"
            "乌衣巷口夕阳斜，王谢堂前燕已飞入寻常百姓家。\n"
            "北渡长江可达扬州，这里是大唐的江南重镇。"
        ),
    },

    # ── 西南路线 ──────────────────────────────────
    "yizheng": {
        "key": "仪征",
        "desc": (
            "仪征是扬州西面的门户小城，依山傍水。\n"
            "这里的铜矿开采已有数百年历史，矿工们日夜劳作。\n"
            "城虽不大，却是扬州通往西部的必经之路。\n"
            "东去扬州，西去合肥。"
        ),
    },
    "hefei": {
        "key": "合肥",
        "desc": (
            "合肥是江淮之间的重镇，三国时张辽曾在此大破吴军。\n"
            "逍遥津古战场遗址犹存，令人感慨万千。\n"
            "城四周沃野千里，是江淮粮仓。\n"
            "东去仪征，西去信阳，是南北交通要冲。"
        ),
    },

    # ── 西方路线 ──────────────────────────────────
    "chuzhou": {
        "key": "滁州",
        "desc": (
            "滁州是一座山清水秀的小城，琅琊山风景如画。\n"
            '欧阳修在《醉翁亭记》中写道："醉翁之意不在酒，在乎山水之间也。"\n'
            "醉翁亭就坐落在琅琊山下，文人墨客常来此饮酒赋诗。\n"
            "东去扬州，西去开封。"
        ),
    },
    "kaifeng": {
        "key": "开封",
        "desc": (
            "开封古称汴州，是中原重镇，水陆交通枢纽。\n"
            "汴河穿城而过，两岸商铺鳞次栉比。\n"
            "大相国寺香火鼎盛，每月五次万姓交易，热闹非凡。\n"
            "西去洛阳，东去商丘，南去滁州。"
        ),
    },

    # ── 西北路线 ──────────────────────────────────
    "xuyi": {
        "key": "盱眙",
        "desc": (
            "盱眙是淮河边的一座小城，以小龙虾闻名后世。\n"
            "淮河在此拐了一个大弯，河水浑浊却滋养了两岸土地。\n"
            "这里是北方通往扬州的必经之路。\n"
            "东南去扬州，北去宿州。"
        ),
    },
    "suzhou_anhui": {
        "key": "宿州",
        "desc": (
            "宿州是淮北平原上的重镇，周围一马平川。\n"
            "这里民风淳朴，是小麦和棉花的主产区。\n"
            "隋唐大运河经过此地，是南北漕运的重要节点。\n"
            "南去盱眙，北去商丘，西去开封。"
        ),
    },
    "shangqiu": {
        "key": "商丘",
        "desc": (
            "商丘是殷商故地，历史悠久，文化底蕴深厚。\n"
            "这里是火神阏伯的封地，阏伯台是华夏最古老的天文台。\n"
            "古城虽历经沧桑，但依然气势不凡。\n"
            "南去宿州，东去徐州，西去开封。"
        ),
    },

    # ── 特殊场景 ──────────────────────────────────
    "yangtze_river": {
        "key": "长江之上",
        "desc": (
            "你正乘船航行在浩瀚的长江之上。\n"
            "江水滔滔，两岸青山如黛，猿声啼不住。\n"
            "江风拂面，令人心旷神怡。\n"
            "南岸是金陵，北岸是瓜洲渡。"
        ),
    },
    "canal": {
        "key": "大运河",
        "desc": (
            "大运河是世界上最长的人工运河，连接南北，贯通五水。\n"
            "河面上漕船、商船、客船往来如织，\n"
            "纤夫们弓着腰在岸边喊着号子拉纤。\n"
            "沿着运河，你可以一路北上直到洛阳。"
        ),
    },
}


# =============================================================================
# 出口定义 (源房间key, 出口key, 目标房间key, 方向)
# =============================================================================

EXITS = [
    # ── 扬州城内部 ────────────────────────────────
    ("yangzhou_center", "east", "yangzhou_east_market", "东"),
    ("yangzhou_center", "west", "yangzhou_west_market", "西"),
    ("yangzhou_center", "south", "yangzhou_wharf", "南"),
    ("yangzhou_center", "north", "yangzhou_office", "北"),

    ("yangzhou_east_market", "west", "yangzhou_center", "西"),
    ("yangzhou_east_market", "east", "yangzhou_east_gate", "东"),

    ("yangzhou_west_market", "east", "yangzhou_center", "东"),
    ("yangzhou_west_market", "west", "yangzhou_west_gate", "西"),

    ("yangzhou_wharf", "north", "yangzhou_center", "北"),
    ("yangzhou_wharf", "south", "guazhou", "南"),

    ("yangzhou_office", "south", "yangzhou_center", "南"),

    ("yangzhou_center", "northeast", "yangzhou_tavern", "东北"),
    ("yangzhou_tavern", "southwest", "yangzhou_center", "西南"),

    ("yangzhou_center", "northwest", "yangzhou_temple", "西北"),
    ("yangzhou_temple", "southeast", "yangzhou_center", "东南"),

    ("yangzhou_center", "southwest", "yangzhou_garden", "西南"),
    ("yangzhou_garden", "northeast", "yangzhou_center", "东北"),

    ("yangzhou_center", "southeast", "yangzhou_inn", "东南"),
    ("yangzhou_inn", "northwest", "yangzhou_center", "西北"),

    # ── 扬州城门 → 城外 ───────────────────────────
    ("yangzhou_north_gate", "south", "yangzhou_center", "南"),
    ("yangzhou_north_gate", "north", "gaoyou", "北"),

    ("yangzhou_east_gate", "west", "yangzhou_east_market", "西"),
    ("yangzhou_east_gate", "east", "taizhou", "东"),

    ("yangzhou_south_gate", "north", "yangzhou_center", "北"),
    ("yangzhou_south_gate", "south", "guazhou", "南"),

    ("yangzhou_west_gate", "east", "yangzhou_west_market", "东"),
    ("yangzhou_west_gate", "west", "yizheng", "西"),

    # ── 北方路线 ──────────────────────────────────
    ("gaoyou", "south", "yangzhou_north_gate", "南"),
    ("gaoyou", "north", "huaian", "北"),

    ("huaian", "south", "gaoyou", "南"),
    ("huaian", "north", "xuzhou", "北"),

    ("xuzhou", "south", "huaian", "南"),
    ("xuzhou", "west", "shangqiu", "西"),
    ("xuzhou", "northwest", "luoyang", "西北"),

    ("luoyang", "southeast", "xuzhou", "东南"),
    ("luoyang", "west", "changan", "西"),
    ("luoyang", "east", "kaifeng", "东"),

    ("changan", "east", "luoyang", "东"),

    # ── 东北路线 ──────────────────────────────────
    ("taizhou", "west", "yangzhou_east_gate", "西"),
    ("taizhou", "northeast", "haian", "东北"),

    ("haian", "southwest", "taizhou", "西南"),
    ("haian", "north", "yancheng", "北"),
    ("haian", "east", "tongzhou", "东"),

    ("yancheng", "south", "haian", "南"),

    # ── 东方路线 ──────────────────────────────────
    ("tongzhou", "west", "haian", "西"),
    ("tongzhou", "east", "haimen", "东"),

    ("haimen", "west", "tongzhou", "西"),
    ("haimen", "east", "east_sea", "东"),

    ("east_sea", "west", "haimen", "西"),

    # ── 东南路线 ──────────────────────────────────
    ("guazhou", "north", "yangzhou_wharf", "北"),
    ("guazhou", "south", "zhenjiang", "南"),

    ("zhenjiang", "north", "guazhou", "北"),
    ("zhenjiang", "southeast", "suzhou", "东南"),
    ("zhenjiang", "southwest", "jinling", "西南"),

    ("suzhou", "northwest", "zhenjiang", "西北"),
    ("suzhou", "south", "hangzhou", "南"),

    ("hangzhou", "north", "suzhou", "北"),

    # ── 南方路线 ──────────────────────────────────
    ("jinling", "northeast", "zhenjiang", "东北"),

    # ── 西南路线 ──────────────────────────────────
    ("yizheng", "east", "yangzhou_west_gate", "东"),
    ("yizheng", "west", "hefei", "西"),

    ("hefei", "east", "yizheng", "东"),

    # ── 西方路线 ──────────────────────────────────
    ("chuzhou", "east", "yizheng", "东"),
    ("chuzhou", "west", "kaifeng", "西"),

    ("kaifeng", "east", "shangqiu", "东"),
    ("kaifeng", "west", "luoyang", "西"),
    ("kaifeng", "south", "chuzhou", "南"),

    # ── 西北路线 ──────────────────────────────────
    ("xuyi", "southeast", "gaoyou", "东南"),
    ("xuyi", "north", "suzhou_anhui", "北"),

    ("suzhou_anhui", "south", "xuyi", "南"),
    ("suzhou_anhui", "north", "shangqiu", "北"),
    ("suzhou_anhui", "west", "kaifeng", "西"),

    ("shangqiu", "east", "xuzhou", "东"),
    ("shangqiu", "west", "kaifeng", "西"),
    ("shangqiu", "south", "suzhou_anhui", "南"),

    # ── 长江水路 ──────────────────────────────────
    ("guazhou", "southwest", "yangtze_river", "西南"),
    ("yangtze_river", "northeast", "guazhou", "东北"),
    ("yangtze_river", "south", "jinling", "南"),
    ("jinling", "north", "yangtze_river", "北"),
]


def build():
    """
    构建世界地图。
    先创建所有房间，再创建所有出口。
    """
    # 创建所有房间
    rooms = {}
    for room_key, room_data in ROOMS.items():
        obj = create_object(
            typeclass="typeclasses.rooms.Room",
            key=room_data["key"],
            attributes=[("desc", room_data["desc"])],
        )
        if obj:
            rooms[room_key] = obj
            print(f"[创建房间] {room_data['key']} (key={room_key})")
        else:
            print(f"[失败] 无法创建房间: {room_data['key']}")

    # 创建所有出口
    for src_key, exit_dir, dest_key, exit_name in EXITS:
        src_room = rooms.get(src_key)
        dest_room = rooms.get(dest_key)
        if src_room and dest_room:
            exit_obj = create_object(
                typeclass="typeclasses.exits.Exit",
                key=exit_dir,
                location=src_room,
                destination=dest_room,
                attributes=[
                    ("desc", f"一条通往{exit_name}方的道路。"),
                ],
            )
            if exit_obj:
                print(f"  [出口] {src_key} --{exit_dir}--> {dest_key}")
            else:
                print(f"  [失败] 出口: {src_key} -> {dest_key}")
        else:
            print(f"  [跳过] 缺少房间: {src_key}->{dest_key}")

    # 设置起始房间
    start_room = rooms.get("yangzhou_center")
    if start_room:
        from evennia import settings
        settings.START_LOCATION = start_room.dbref
        print(f"\n起始地点已设为: 扬州城中心 (#{start_room.dbref})")

    print(f"\n世界构建完成！共创建 {len(rooms)} 个房间，{len(EXITS)} 条出口。")
    return rooms


if __name__ == "__main__":
    build()