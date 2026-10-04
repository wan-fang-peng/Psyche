# 开发与分发约定

改造或重写本 skill 时请遵守以下约定。这些不是风格偏好，是踩过坑总结出来的硬约束。

---

## 一、路径与解释器（最容易出问题的地方）

### 禁止硬编码绝对路径

skill 可能装在两处：

- 用户级 `~/.workbuddy/skills/ex-persona/`
- 项目级 `{项目}/.workbuddy/skills/ex-persona/`

目录名也可能被改。所有定位必须自解析：

```python
import os
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(TOOLS_DIR)
```

### 禁止假设 `${CLAUDE_SKILL_DIR}`

这是 Claude Code 提供的变量，**WorkBuddy 不提供**。照抄其他 skill 的写法会在本平台
直接失效——本项目已因此改造（原版 20 处失效）。

### 禁止写死 `python3`

Windows 上通常只有 `python`。统一走 `sys.executable`：

```python
subprocess.run([sys.executable, script_path] + args)
```

`extool.py` 已按此实现，内部子命令自动跟随调用方的解释器。

### 对外只暴露一个入口

SKILL.md 里不要让 AI 分别调六个脚本，统一走 `extool.py <子命令>`。好处：
路径只解析一次、AI 调用不易出错、跨平台透明。内部脚本保持零改动，便于和原版
diff 比对、溯源。

---

## 二、触发方式

### 禁止斜杠命令

`/create-ex`、`/list-exes` 是 Claude Code 语法，WorkBuddy 不支持。
本项目已全部改为自然语言触发（"帮我创建一个前任"）或 `@ex-persona`。

### list 类输出不要打印斜杠命令

脚本输出里也不要把 `/slug` 当作操作指引，那是给用户看的「怎么用」，
必须写成自然语言（如"直接说「跟 ta 聊聊」并指明是哪一位"）。

---

## 三、frontmatter 硬性要求

```yaml
---
name: ex-persona          # 与目录名一致
description: ...           # 写清触发场景，决定 AI 匹配命中率
agent_created: true        # 缺这行 WorkBuddy 不允许修改该 skill
version: 1.0.0
license: MIT
---
```

`description` 不能写"一个处理前任的工具"。要写清：
用户会说什么、输入是什么、输出是什么、除了前任还适用于谁。

---

## 四、隐私与安全

### 生成数据必须被 gitignore

`exes/` 含高度私密的聊天内容摘要。已在本目录 `.gitignore` 中屏蔽，
但**新增输出目录时必须同步补进去**。

### 脚本零网络

不引入 `requests` / `urllib` / `socket`。所有处理本地完成。
这是用户信任这个 skill 的基础，不要为了"打个统计上报"破坏它。

### 唯一允许的外部依赖

Pillow（读照片 EXIF），且必须可选——未安装时降级运行而非报错中断。

### 不编造原材料里没有的事

生成人格时，原材料没提到的细节宁可留白或标注"记忆模糊"。
Layer 0 硬规则（不说 ta 绝不可能说的话）的优先级高于用户期待。

---

## 五、流程完整性

### 命令链要实跑，不要只测单个

本项目踩过的坑：`init` 只建目录不写 meta.json，导致 `backup` 必失败。
两个命令单独测都"通过"，串起来才暴露。

改动任何命令后，用一份样例数据把完整链路跑一遍：

```
where → init → parse-* → list → backup → versions → rollback
```

### 修改脚本时同步改 SKILL.md

SKILL.md 里的参数名必须和脚本 `argparse` 定义一致。AI 照文档调用，
对不上就直接报错。

### 回归验证用真实数据

`parse-wechat` 的分析链路（口头禅、标点、emoji、风格判定）依赖
`parse_plaintext` 正确切分消息。改解析逻辑后必须确认统计数字不是 N/A。

---

## 六、分发前检查

完整清单见仓库根目录 `SHARE-GUIDE.md`。最容易漏的三条：

1. **zip 包必须排除 `.git/`** —— 否则会连完整提交历史一起发出去
2. **不能用 `npx skills add` 分发** —— 实测它装到 `~/.agents/skills/`，
   不写 `~/.workbuddy/skills/`，WorkBuddy 读不到
3. **不能让用户拖拽导入 SKILL.md** —— 只导入主文件，`tools/` 和 `prompts/`
   都不跟着来，带脚本的 skill 会直接失效

---

## 七、衍生作品的许可要求

本项目派生自 `therealXiaomanChu/ex-skill`（MIT）。若你再分发衍生版本：

- 保留 `LICENSE` 中的原始版权声明
- README 中写明原项目名称与链接
- 列出相对原版的改动（做了什么、为什么做）

MIT 允许闭源商用，但不免除署名义务。
