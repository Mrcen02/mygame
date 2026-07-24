"""
地图渲染引擎

从数据库读取所有带有 map_x/map_y 属性的房间，生成 ASCII 地图。
支持三级缩放：世界(0)、区域(1)、本地(2)。

房间分类:
  █ 都城  ▣ 州城  ◇ 县城  ◎ 村镇  ▲ 山岳  ~ 水路
  ★ 当前位置（你在这里）

路线:
  ─ 东西向  │ 南北向  ┼ 交叉  ┌┐└┘ 拐角
"""

import re
from evennia.objects.models import ObjectDB


# 房间分类符号
CATEGORY_SYMBOLS = {
    "都城": "█",
    "州城": "▣",
    "县城": "◇",
    "村镇": "◎",
    "城门": "∩",
    "山岳": "▲",
    "水路": "~",
    "渡口": "≈",
    "寺庙": "△",
    "园林": "♢",
    "酒楼": "♨",
    "驿站": "⌂",
    "市场": "▤",
    "码头": "▽",
    "府衙": "▣",
    "湖泊": "≈",
    "海滨": "▽",
    "野外": "·",
}

# 缩放级别定义
ZOOM_WORLD = 0   # 世界地图：显示所有城池
ZOOM_REGION = 1  # 区域地图：显示当前区域及周边
ZOOM_LOCAL = 2   # 本地地图：显示当前房间及相连房间

# 世界地图显示的最小等级（隐藏城门、市场等小房间）
WORLD_CATEGORIES = {"都城", "州城", "县城", "村镇", "渡口", "山岳", "水路", "海滨"}


def get_all_rooms():
    """获取所有带有 map_x 属性的房间。"""
    try:
        rooms = ObjectDB.objects.filter(db_typeclass_path__icontains='room')
    except Exception:
        rooms = []
    result = []
    for room in rooms:
        try:
            x = room.attributes.get("map_x")
            if x is not None:
                result.append(room)
        except Exception:
            continue
    return result


def get_room_category(room):
    """获取房间的类别。"""
    try:
        cat = room.attributes.get("map_category")
        if cat:
            return cat
    except Exception:
        pass
    # 从 key 推断
    key = room.key
    if "长安" in key or "洛阳" in key:
        return "都城"
    if "金陵" in key or "杭州" in key or "苏州" in key:
        return "州城"
    if "扬州" in key:
        if "门" in key:
            return "城门"
        if "市" in key:
            return "市场"
        if "码头" in key:
            return "码头"
        if "寺" in key:
            return "寺庙"
        if "湖" in key:
            return "湖泊"
        if "园" in key:
            return "园林"
        if "酒楼" in key or "楼" in key:
            return "酒楼"
        if "驿站" in key:
            return "驿站"
        if "府衙" in key:
            return "府衙"
        return "州城"
    if "长江" in key or "运河" in key:
        return "水路"
    if "渡" in key:
        return "渡口"
    if "海" in key:
        return "海滨"
    if len(key) <= 3:
        return "县城"
    return "村镇"


def get_room_symbol(room):
    """获取房间在地图上的显示符号。"""
    cat = get_room_category(room)
    return CATEGORY_SYMBOLS.get(cat, "◇")


def get_direction(from_room, to_room):
    """获取两个房间之间的方向符号。"""
    try:
        fx = from_room.attributes.get("map_x", 0)
        fy = from_room.attributes.get("map_y", 0)
        tx = to_room.attributes.get("map_x", 0)
        ty = to_room.attributes.get("map_y", 0)
    except Exception:
        return None

    dx = tx - fx
    dy = ty - fy

    if dx == 0 and dy == 0:
        return None
    if dx == 0:
        return "│" if dy < 0 else "│"
    if dy == 0:
        return "─" if dx > 0 else "─"
    if dx > 0 and dy < 0:
        return "╱"
    if dx > 0 and dy > 0:
        return "╲"
    if dx < 0 and dy < 0:
        return "╲"
    if dx < 0 and dy > 0:
        return "╱"
    return "─"


def get_connected_rooms(room):
    """获取与当前房间直接相连的所有房间。"""
    connected = []
    try:
        for ex in room.exits:
            if ex.destination:
                connected.append(ex.destination)
    except Exception:
        pass
    return connected


def get_route_char(room, rooms_set):
    """
    判断一个房间是否是路线经过的点（非房间本身），
    返回路线字符或 None。
    """
    try:
        x = room.attributes.get("map_x")
        if x is None:
            return None
    except Exception:
        return None
    return None  # 简化：房间本身就是符号位置


def build_world_map(player_room, all_rooms):
    """
    构建世界地图（缩放级别 0）。
    显示所有主要城池和路线。
    """
    # 收集所有有坐标的房间
    room_coords = {}
    for room in all_rooms:
        try:
            x = room.attributes.get("map_x")
            y = room.attributes.get("map_y")
            if x is not None and y is not None:
                room_coords[(x, y)] = room
        except Exception:
            continue

    if not room_coords:
        return "地图数据尚未加载。请先运行 build_world.build() 构建世界。\n"

    # 计算边界
    xs = [c[0] for c in room_coords]
    ys = [c[1] for c in room_coords]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    # 网格大小
    width = max_x - min_x + 1
    height = max_y - min_y + 1

    # 构建路线集合
    route_points = set()
    for (x, y), room in room_coords.items():
        for neighbor in get_connected_rooms(room):
            try:
                nx = neighbor.attributes.get("map_x")
                ny = neighbor.attributes.get("map_y")
                if nx is not None and ny is not None:
                    # 画两点之间的连线
                    draw_line(route_points, x, y, nx, ny)
            except Exception:
                continue

    # 获取玩家位置
    try:
        player_x = player_room.attributes.get("map_x", 0)
        player_y = player_room.attributes.get("map_y", 0)
    except Exception:
        player_x, player_y = 0, 0

    # 渲染
    lines = []
    lines.append("╔" + "═" * (width * 2 + 1) + "╗")
    lines.append("║  【世界地图 · 大唐天下】" + " " * (width * 2 - 20) + "║")

    for y in range(min_y, max_y + 1):
        row = "║ "
        for x in range(min_x, max_x + 1):
            if (x, y) == (player_x, player_y):
                row += "★"
            elif (x, y) in room_coords:
                room = room_coords[(x, y)]
                cat = get_room_category(room)
                if cat in WORLD_CATEGORIES:
                    row += get_room_symbol(room)
                else:
                    row += " "
            elif (x, y) in route_points:
                row += "·"
            else:
                row += " "
        row += " ║"
        lines.append(row)

    lines.append("║" + " " * (width * 2 + 1) + "║")
    lines.append("║  图例: █都城 ▣州城 ◇县城 ◎村镇 ▲山岳 ~水路 ★你在 ║")
    lines.append("╚" + "═" * (width * 2 + 1) + "╝")
    lines.append("输入 '地图 区域' 查看周边，'地图 本地' 查看附近。")

    return "\n".join(lines)


def build_region_map(player_room, all_rooms, radius=10):
    """
    构建区域地图（缩放级别 1）。
    显示玩家周围一定范围内的所有房间。
    """
    try:
        cx = player_room.attributes.get("map_x", 0)
        cy = player_room.attributes.get("map_y", 0)
    except Exception:
        return "无法获取你的位置信息。\n"

    # 收集范围内的房间
    room_coords = {}
    for room in all_rooms:
        try:
            x = room.attributes.get("map_x")
            y = room.attributes.get("map_y")
            if x is not None and y is not None:
                if abs(x - cx) <= radius and abs(y - cy) <= radius:
                    room_coords[(x, y)] = room
        except Exception:
            continue

    if not room_coords:
        return "附近没有地图数据。\n"

    # 边界
    xs = [c[0] for c in room_coords] + [cx]
    ys = [c[1] for c in room_coords] + [cy]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    width = max_x - min_x + 1
    height = max_y - min_y + 1

    # 路线
    route_points = set()
    for (x, y), room in room_coords.items():
        for neighbor in get_connected_rooms(room):
            try:
                nx = neighbor.attributes.get("map_x")
                ny = neighbor.attributes.get("map_y")
                if nx is not None and ny is not None:
                    if abs(nx - cx) <= radius and abs(ny - cy) <= radius:
                        draw_line(route_points, x, y, nx, ny)
            except Exception:
                continue

    # 渲染
    region_name = _get_region_name(cx, cy)
    lines = []
    lines.append("┌" + "─" * (width * 2 + 1) + "┐")
    lines.append(f"│  【区域地图 · {region_name}】" + " " * (width * 2 - 14 - len(region_name) * 2) + "│")

    for y in range(min_y, max_y + 1):
        row = "│ "
        for x in range(min_x, max_x + 1):
            if (x, y) == (cx, cy):
                row += "★"
            elif (x, y) in room_coords:
                row += get_room_symbol(room_coords[(x, y)])
            elif (x, y) in route_points:
                row += "·"
            else:
                row += " "
        row += " │"
        lines.append(row)

    # 房间列表
    lines.append("│" + " " * (width * 2 + 1) + "│")
    lines.append("│  附近地点：" + " " * (width * 2 - 9) + "│")
    for (x, y), room in sorted(room_coords.items()):
        if (x, y) != (cx, cy):
            label = f"    {get_room_symbol(room)} {room.key}"
            lines.append(f"│{label}" + " " * (width * 2 + 1 - _str_width(label)) + "│")

    lines.append("└" + "─" * (width * 2 + 1) + "┘")
    lines.append("输入 '地图' 查看世界，'地图 本地' 查看附近。")

    return "\n".join(lines)


def build_local_map(player_room, all_rooms):
    """
    构建本地地图（缩放级别 2）。
    显示当前房间及直接相连的房间。
    """
    try:
        cx = player_room.attributes.get("map_x", 0)
        cy = player_room.attributes.get("map_y", 0)
    except Exception:
        return "无法获取你的位置信息。\n"

    connected = get_connected_rooms(player_room)
    room_coords = {(cx, cy): player_room}

    for room in connected:
        try:
            x = room.attributes.get("map_x")
            y = room.attributes.get("map_y")
            if x is not None and y is not None:
                room_coords[(x, y)] = room
        except Exception:
            continue

    if len(room_coords) <= 1:
        return "这里没有通往其他地点的出口。\n"

    xs = [c[0] for c in room_coords]
    ys = [c[1] for c in room_coords]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    width = max_x - min_x + 1
    if width < 3:
        width = 3
    height = max_y - min_y + 1
    if height < 3:
        height = 3

    lines = []
    lines.append(f"\n  【{player_room.key}】")
    lines.append("  " + "─" * (width * 2 + 1))

    for y in range(min_y, max_y + 1):
        row = "  │"
        for x in range(min_x, max_x + 1):
            if (x, y) == (cx, cy):
                row += "★"
            elif (x, y) in room_coords:
                room = room_coords[(x, y)]
                # 方向提示
                direction = get_exit_direction(player_room, room)
                if direction:
                    row += direction
                else:
                    row += get_room_symbol(room)
            else:
                row += " "
        row += "│"
        lines.append(row)

    lines.append("  " + "─" * (width * 2 + 1))
    lines.append("  ★ = 你在这里")

    # 出口列表
    lines.append(f"\n  从【{player_room.key}】可以前往：")
    for ex in player_room.exits:
        if ex.destination:
            dir_cn = get_dir_cn(ex.key)
            lines.append(f"    {dir_cn} → {ex.destination.key}")

    lines.append("\n输入 '地图' 查看世界，'地图 区域' 查看周边。")
    return "\n".join(lines)


def draw_line(points, x1, y1, x2, y2):
    """在点集中画一条从 (x1,y1) 到 (x2,y2) 的直线。"""
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    while True:
        if (x1, y1) not in points:
            points.add((x1, y1))
        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy


def get_exit_direction(from_room, to_room):
    """获取从 from_room 到 to_room 的方向提示。"""
    try:
        fx = from_room.attributes.get("map_x", 0)
        fy = from_room.attributes.get("map_y", 0)
        tx = to_room.attributes.get("map_x", 0)
        ty = to_room.attributes.get("map_y", 0)
    except Exception:
        return "?"

    dx = tx - fx
    dy = ty - fy

    if dx == 0 and dy < 0:
        return "↑"
    if dx == 0 and dy > 0:
        return "↓"
    if dx < 0 and dy == 0:
        return "←"
    if dx > 0 and dy == 0:
        return "→"
    if dx > 0 and dy < 0:
        return "↗"
    if dx > 0 and dy > 0:
        return "↘"
    if dx < 0 and dy < 0:
        return "↖"
    if dx < 0 and dy > 0:
        return "↙"
    return "◎"


def get_dir_cn(direction):
    """将英文方向转为中文。"""
    mapping = {
        "north": "北", "south": "南", "east": "东", "west": "西",
        "northeast": "东北", "northwest": "西北",
        "southeast": "东南", "southwest": "西南",
        "up": "上", "down": "下",
    }
    return mapping.get(direction.lower(), direction)


def _get_region_name(x, y):
    """根据坐标推断区域名称。"""
    if 35 <= x <= 45 and 15 <= y <= 25:
        return "扬州"
    if 38 <= x <= 42 and 10 <= y <= 14:
        return "高邮·淮安"
    if x >= 46 and 15 <= y <= 25:
        return "泰州·海安"
    if x >= 55:
        return "通州·东海"
    if 30 <= x <= 35 and 0 <= y <= 10:
        return "洛阳·开封"
    if x <= 25 and y <= 5:
        return "长安"
    if 40 <= x <= 50 and 30 <= y <= 40:
        return "苏州·杭州"
    if 30 <= x <= 36 and 25 <= y <= 35:
        return "金陵"
    if 25 <= x <= 35 and 15 <= y <= 25:
        return "合肥·滁州"
    if 25 <= x <= 35 and 5 <= y <= 15:
        return "宿州·商丘"
    return "未知区域"


def _str_width(s):
    """估算字符串显示宽度（中文算2，英文算1）。"""
    w = 0
    for ch in s:
        if '\u4e00' <= ch <= '\u9fff' or '\u3000' <= ch <= '\u303f':
            w += 2
        else:
            w += 1
    return w


def show_map(caller, zoom="世界"):
    """地图命令入口。"""
    zoom = zoom.strip()
    all_rooms = get_all_rooms()

    if not all_rooms:
        caller.msg("世界尚未构建，请管理员先运行 build_world.build()。")
        return

    player_room = caller.location
    if not player_room:
        caller.msg("你不在任何地方。")
        return

    if zoom in ("本地", "local", "2"):
        caller.msg(build_local_map(player_room, all_rooms))
    elif zoom in ("区域", "region", "1"):
        caller.msg(build_region_map(player_room, all_rooms))
    else:
        caller.msg(build_world_map(player_room, all_rooms))