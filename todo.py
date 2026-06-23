import json
import os
from datetime import datetime

DATA_FILE = "todos.json"
DATE_FMT = "%Y-%m-%d"


# ── 持久化 ──────────────────────────────────────────────────────────────────

def load_todos():
    """从 JSON 文件加载数据，文件不存在则返回空列表"""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_todos(todos):
    """将待办列表写回 JSON 文件"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(todos, f, ensure_ascii=False, indent=2)


# ── 工具函数 ─────────────────────────────────────────────────────────────────

def next_id(todos):
    """返回当前最大 ID + 1，保证 ID 单调递增"""
    return max((t["id"] for t in todos), default=0) + 1


def parse_date(s):
    """将字符串解析为 date 对象，格式不对则抛出 ValueError"""
    return datetime.strptime(s.strip(), DATE_FMT).date()


def input_date(prompt):
    """循环提示直到输入合法日期，返回日期字符串"""
    while True:
        raw = input(prompt).strip()
        try:
            parse_date(raw)          # 仅做格式校验
            return raw
        except ValueError:
            print("  日期格式错误，请输入 YYYY-MM-DD（例如 2026-07-01）")


def require(value, name="内容"):
    """非空校验，为空则抛出 ValueError"""
    if not value:
        raise ValueError(f"{name}不能为空")
    return value


def sorted_by_date(todos):
    """按截止日期升序排列，返回新列表"""
    return sorted(todos, key=lambda t: parse_date(t["due_date"]))


def print_table(todos):
    """表格式打印待办列表"""
    if not todos:
        print("  （暂无待办事项）")
        return
    header = f"{'ID':<5} {'状态':<6} {'标题':<20} {'截止日期':<12} 描述"
    print("\n" + header)
    print("-" * 65)
    for t in todos:
        status = "✓完成" if t["done"] else "✗待办"
        print(f"{t['id']:<5} {status:<6} {t['title']:<20} {t['due_date']:<12} {t['description']}")


def print_brief(todos):
    """简洁打印 ID + 标题，用于编辑/删除前参考"""
    for t in sorted_by_date(todos):
        flag = "✓" if t["done"] else "✗"
        print(f"  [{t['id']}] {flag} {t['title']}  ({t['due_date']})")


def find_by_id(todos, tid):
    """按 ID 查找待办，找不到抛出 ValueError"""
    todo = next((t for t in todos if t["id"] == tid), None)
    if todo is None:
        raise ValueError(f"ID {tid} 不存在")
    return todo


# ── 核心功能 ─────────────────────────────────────────────────────────────────

def add_todo(todos):
    """新增待办：收集字段后追加到列表并保存"""
    print("\n── 新增待办 ──")
    title = require(input("标题: ").strip(), "标题")
    desc  = input("描述（可留空）: ").strip()
    due   = input_date("截止日期 (YYYY-MM-DD): ")

    todo = {
        "id":          next_id(todos),
        "title":       title,
        "description": desc,
        "due_date":    due,
        "done":        False,
    }
    todos.append(todo)
    save_todos(todos)
    print(f"  已添加：{title}")


def list_todos(todos):
    """查看待办，支持全部 / 未完成 / 已完成三种筛选"""
    print("\n── 查看待办 ──")
    print("  1. 全部  2. 只看未完成  3. 只看已完成")
    choice = input("筛选方式（默认1）: ").strip() or "1"

    pool = sorted_by_date(todos)          # 先按截止日期排序
    if choice == "2":
        pool = [t for t in pool if not t["done"]]
    elif choice == "3":
        pool = [t for t in pool if t["done"]]
    elif choice != "1":
        print("  无效选项，显示全部")

    print_table(pool)


def edit_todo(todos):
    """修改待办：标题、描述、截止日期、完成状态均可单独更新"""
    print("\n── 修改待办 ──")
    if not todos:
        print("  暂无待办可修改")
        return

    print_brief(todos)
    try:
        tid = int(require(input("输入要修改的 ID: ").strip(), "ID"))
    except (ValueError, TypeError):
        raise ValueError("ID 必须是整数")

    todo = find_by_id(todos, tid)

    # 每项直接回车则保留原值
    new_title = input(f"标题 [{todo['title']}]（回车保留）: ").strip()
    if new_title:
        todo["title"] = new_title

    new_desc = input(f"描述 [{todo['description']}]（回车保留）: ").strip()
    if new_desc:
        todo["description"] = new_desc

    new_date = input(f"截止日期 [{todo['due_date']}]（回车保留）: ").strip()
    if new_date:
        parse_date(new_date)             # 格式校验，不合法直接抛出
        todo["due_date"] = new_date

    cur_status = "已完成" if todo["done"] else "未完成"
    toggle = input(f"当前状态：{cur_status}，是否切换？(y/n): ").strip().lower()
    if toggle == "y":
        todo["done"] = not todo["done"]

    save_todos(todos)
    print("  修改已保存")


def delete_todo(todos):
    """删除指定 ID 的待办，二次确认后执行"""
    print("\n── 删除待办 ──")
    if not todos:
        print("  暂无待办可删除")
        return

    print_brief(todos)
    try:
        tid = int(require(input("输入要删除的 ID: ").strip(), "ID"))
    except (ValueError, TypeError):
        raise ValueError("ID 必须是整数")

    todo = find_by_id(todos, tid)        # 不存在则抛出 ValueError
    confirm = input(f"  确认删除「{todo['title']}」？(y/n): ").strip().lower()
    if confirm == "y":
        todos.remove(todo)
        save_todos(todos)
        print("  已删除")
    else:
        print("  已取消")


# ── 主菜单 ───────────────────────────────────────────────────────────────────

MENU = """
╔══════════════════════════════╗
║      个人待办事项管理器       ║
╠══════════════════════════════╣
║  1. 新增待办                 ║
║  2. 查看待办                 ║
║  3. 修改待办                 ║
║  4. 删除待办                 ║
║  0. 退出                     ║
╚══════════════════════════════╝"""

ACTIONS = {
    "1": add_todo,
    "2": list_todos,
    "3": edit_todo,
    "4": delete_todo,
}


def main():
    todos = load_todos()                 # 程序启动时一次性加载
    while True:
        print(MENU)
        choice = input("请选择操作: ").strip()
        if choice == "0":
            print("再见！")
            break
        action = ACTIONS.get(choice)
        if action is None:
            print("  无效选项，请输入 0-4")
            continue
        try:
            action(todos)                # 所有函数共享同一份列表引用
        except ValueError as e:
            print(f"  输入错误：{e}")
        except KeyboardInterrupt:
            print("\n  操作已取消")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n再见！")
