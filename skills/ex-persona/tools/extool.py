#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extool.py — 前任人格蒸馏 skill 的统一命令行入口。

为什么需要这个文件：
  1. 自定位。脚本用 __file__ 反推 skill 根目录，因此调用方不需要知道
     绝对路径，也不需要 Claude Code 的 ${CLAUDE_SKILL_DIR} 之类变量。
     无论 skill 装在用户级还是项目级、目录叫什么，调用方式完全一致。
  2. 跨平台。原项目各脚本文档里统一写 python3，在 Windows 上不存在这个
     命令。本入口用 sys.executable，即当前解释器自身，天然对齐。
  3. 单一入口。对外只暴露 extool.py 一个可执行文件，内部按子命令分发到
     wechat_parser / qq_parser / social_parser / photo_analyzer /
     version_manager / skill_writer，保持原脚本零改动，便于溯源比对。

只做本地文件读写，不发起任何网络请求。
"""

import argparse
import os
import subprocess
import sys

# skill 根目录 = 本文件所在 tools/ 的上一级
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(TOOLS_DIR)

# 内部脚本白名单：只允许调用同目录下这几个文件，杜绝任意代码执行
ALLOWED = {
    "wechat": "wechat_parser.py",
    "qq": "qq_parser.py",
    "social": "social_parser.py",
    "photo": "photo_analyzer.py",
    "version": "version_manager.py",
    "writer": "skill_writer.py",
}


def _python() -> str:
    """当前解释器。sys.executable 一定存在，且与运行本文件的解释器一致。"""
    return sys.executable or "python"


def _run(script_key: str, argv) -> int:
    """把参数原样转发给内部脚本。"""
    script = os.path.join(TOOLS_DIR, ALLOWED[script_key])
    if not os.path.isfile(script):
        print(f"[错误] 找不到内部脚本：{script}", file=sys.stderr)
        return 2
    proc = subprocess.run([_python(), script] + argv, check=False)
    return proc.returncode


def cmd_parse_wechat(a) -> int:
    return _run("wechat", [
        "--file", a.file, "--target", a.target,
        "--output", a.output, "--format", a.format,
    ])


def cmd_parse_qq(a) -> int:
    return _run("qq", [
        "--file", a.file, "--target", a.target, "--output", a.output,
    ])


def cmd_parse_social(a) -> int:
    return _run("social", ["--dir", a.dir, "--output", a.output])


def cmd_photos(a) -> int:
    return _run("photo", ["--dir", a.dir, "--output", a.output])


def cmd_backup(a) -> int:
    return _run("version", [
        "--action", "backup", "--slug", a.slug, "--base-dir", a.base_dir,
    ])


def cmd_rollback(a) -> int:
    return _run("version", [
        "--action", "rollback", "--slug", a.slug,
        "--version", a.version, "--base-dir", a.base_dir,
    ])


def cmd_versions(a) -> int:
    return _run("version", [
        "--action", "list", "--slug", a.slug, "--base-dir", a.base_dir,
    ])


def cmd_list(a) -> int:
    return _run("writer", ["--action", "list", "--base-dir", a.base_dir])


def cmd_init(a) -> int:
    argv = ["--action", "init", "--base-dir", a.base_dir]
    if a.slug:
        argv += ["--slug", a.slug]
    return _run("writer", argv)


def cmd_where(a) -> int:
    """打印 skill 根目录。供 AI 在需要绝对路径时先探测一次。"""
    print(SKILL_DIR)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="extool",
        description="前任人格蒸馏 skill 统一入口（本地运行，无网络请求）",
    )
    p.add_argument(
        "--base-dir", default="./exes",
        help="前任 skill 输出根目录，默认为当前目录下的 ./exes",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("where", help="打印 skill 根目录绝对路径")
    s.set_defaults(fn=cmd_where)

    s = sub.add_parser("parse-wechat", help="解析微信/纯文本聊天记录")
    s.add_argument("--file", required=True)
    s.add_argument("--target", required=True, help="对方昵称")
    s.add_argument("--output", required=True)
    s.add_argument("--format", default="auto")
    s.set_defaults(fn=cmd_parse_wechat)

    s = sub.add_parser("parse-qq", help="解析 QQ 聊天记录")
    s.add_argument("--file", required=True)
    s.add_argument("--target", required=True)
    s.add_argument("--output", required=True)
    s.set_defaults(fn=cmd_parse_qq)

    s = sub.add_parser("parse-social", help="分析社交平台截图目录")
    s.add_argument("--dir", required=True)
    s.add_argument("--output", required=True)
    s.set_defaults(fn=cmd_parse_social)

    s = sub.add_parser("photos", help="提取照片 EXIF 时间地点时间线")
    s.add_argument("--dir", required=True)
    s.add_argument("--output", required=True)
    s.set_defaults(fn=cmd_photos)

    s = sub.add_parser("backup", help="归档当前版本")
    s.add_argument("--slug", required=True)
    s.set_defaults(fn=cmd_backup)

    s = sub.add_parser("rollback", help="回滚到指定版本")
    s.add_argument("--slug", required=True)
    s.add_argument("--version", required=True)
    s.set_defaults(fn=cmd_rollback)

    s = sub.add_parser("versions", help="列出某位前任的历史版本")
    s.add_argument("--slug", required=True)
    s.set_defaults(fn=cmd_versions)

    s = sub.add_parser("list", help="列出已生成的所有前任")
    s.set_defaults(fn=cmd_list)

    s = sub.add_parser("init", help="初始化 exes 目录结构")
    s.add_argument("--slug")
    s.set_defaults(fn=cmd_init)

    return p


def main() -> int:
    args = build_parser().parse_args()
    try:
        return args.fn(args)
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
