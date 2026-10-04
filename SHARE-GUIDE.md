# 把自己的 skill 分享给别人

以本仓库（ex-persona）为例，四种方式按适用场景排序。

---

## 方式一：GitHub 仓库（最推荐，适合长期维护）

### 怎么发

把 skill 目录推到一个 GitHub 仓库，对方直接 clone 或下载 zip。

仓库推荐结构：

```
你的仓库/
├── .codebuddy-plugin/          # 市场元数据（让 WorkBuddy 市场能收录）
│   ├── plugin.json
│   └── marketplace.json
├── README.md                   # 介绍、用法、截图
├── LICENSE                     # 许可证
└── skills/
    └── 你的-skill/
        ├── SKILL.md            # 必需：技能主文件
        ├── scripts/ 或 tools/  # 可选：脚本
        ├── references/         # 可选：参考资料
        └── assets/             # 可选：模板等静态资源
```

### 对方怎么装

```bash
git clone https://github.com/你的用户名/你的仓库.git
cp -r skills/你的-skill ~/.workbuddy/skills/
```

Windows PowerShell：

```powershell
git clone https://github.com/你的用户名/你的仓库.git
Copy-Item -Recurse skills\你的-skill $HOME\.workbuddy\skills\
```

项目级安装（只在当前项目生效）：

```bash
cp -r skills/你的-skill {项目}/.workbuddy/skills/
```

### 必备的三个文件

**1. `SKILL.md` frontmatter —— 有两个字段不能漏**

```yaml
---
name: 你的-skill名        # 与目录名一致
description: 写清「什么时候该用它」，决定 AI 匹配概率
agent_created: true      # WorkBuddy 专属：没有这行，后续你无法修改自己的 skill
---
```

`description` 是触发命中的关键。别写"一个处理文本的工具"这种废话，要写
"当用户说 XX、XX 时使用。输入…输出…适用于…"。

**2. `.gitignore` —— 保护用户隐私**

如果 skill 会生成用户数据，务必屏蔽：

```gitignore
exes/
outputs/
*.db
```

**3. `LICENSE` —— 想让别人用就必须有**

MIT 最省事，Apache-2.0 多了专利授权保护。

### ⚠️ 别用 `npx skills add`

社区教程常推荐这个，**在 WorkBuddy 上走不通**。实测结果：

```
skills add → 装到 ~/.agents/skills/ → symlink 到 CodeBuddy 等
```

它**不写** `~/.workbuddy/skills/`，WorkBuddy 读不到。装完等于没装。

### ⚠️ 别用拖拽导入 SKILL.md

WorkBuddy 支持把 SKILL.md 拖进对话框，但**只导入主文件**，
`tools/`、`prompts/`、`references/` 全都不跟着来。带脚本的 skill 会直接失效。

---

## 方式二：zip 直发（适合朋友、少量传播）

不想折腾 GitHub，或者对方不用 Git。

### 打包

在仓库根目录执行（**务必排除 `.git`**，否则会连完整提交历史一起发出去）：

```bash
python -c "
import zipfile
from pathlib import Path
root = Path('.')
out = Path('你的-skill.zip')
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in sorted(root.rglob('*')):
        rel = p.relative_to(root).as_posix()
        if rel.startswith('.git/') or '__pycache__' in rel:
            continue
        if p.is_dir():
            z.writestr(rel + '/', '')
        else:
            z.write(p, rel)
print('打包完成')
"
```

### 对方怎么装

解压后把 `skills/你的-skill` 整个目录复制到 `~/.workbuddy/skills/`。

### 附一句安装说明

zip 里放一个 INSTALL.md，写清依赖、装到哪、怎么验证。对方第一次装最容易卡在
"装完没反应"——大概率是路径错了或缺依赖。

---

## 方式三：SkillHub / WorkBuddy 市场（曝光最大）

进 SkillHub 或应用市场，让别人能搜到。

需要准备 `.codebuddy-plugin/plugin.json`：

```json
{
  "name": "你的-skill名",
  "version": "1.0.0",
  "description": "一句话说明，含中英文",
  "author": { "name": "你的名字", "email": "" },
  "license": "MIT",
  "skills": ["./skills/你的-skill名"]
}
```

`skills` 数组用相对路径指向实际 skill 目录，注意是 `./skills/xxx` 形式，
目录名要和 SKILL.md 里的 `name` 对得上。

---

## 方式四：直接告诉对方路径（最快，适合同事）

如果对方就在你旁边、或者用同一台机器：

```
cp -r ~/.workbuddy/skills/你的-skill ~/.workbuddy/skills/
```

同机复制不涉及任何安装问题，最省事。

---

## 写 skill 时容易踩的坑

### 1. 假设了别的工具提供的变量

Claude Code 有 `${CLAUDE_SKILL_DIR}`，**WorkBuddy 没有**。

解法：脚本用 `__file__` 自定位

```python
import os
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
```

这样 skill 装在用户级还是项目级、目录叫什么，调用方式都一样。

### 2. 写死 `python3`

Windows 上通常只有 `python`。用当前解释器转发：

```python
import sys, subprocess
subprocess.run([sys.executable, script_path] + args)
```

或者更稳的做法：包一个统一入口，SKILL.md 里只让 AI 调这一个文件。

### 3. 用了斜杠命令

`/skill-name` 是 Claude Code 的语法。WorkBuddy 用自然语言或 `@技能名`。

### 4. 忘了 `agent_created: true`

没有这行，WorkBuddy 认为不是你创建的 skill，你后续改不动它。

### 5. 脚本和文档不一致

SKILL.md 里写的参数名和脚本实际 `argparse` 定义对不上，AI 照文档调就报错。
改脚本时同步改文档。

### 6. 链路不完整

`init` 建了目录但没写 meta.json，导致后面的 `backup` 必失败。
设计流程时把命令串起来实跑一遍，别只测单个命令。

---

## 一份最小检查清单

发之前过一遍：

- [ ] `SKILL.md` 有 `name` / `description` / `agent_created: true`
- [ ] `description` 写清了触发场景，不是泛泛而谈
- [ ] 脚本里没有硬编码绝对路径，用 `__file__` 自定位
- [ ] 兼容 Windows（无 `python3` 时也能跑）
- [ ] 没有 Claude Code 专有变量和斜杠命令
- [ ] `.gitignore` 屏蔽了用户数据目录
- [ ] 有 `LICENSE`
- [ ] 有 `README.md`（含安装方式）和 `INSTALL.md`
- [ ] zip 包里**不含** `.git`
- [ ] 在一个干净目录里实跑过全部命令
- [ ] 如果是衍生作品，README 里写明原项目 + 保留原始版权声明
