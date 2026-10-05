# 安装说明

## 方式一：手动复制（最通用）

### macOS / Linux / Git Bash

```bash
git clone https://github.com/wan-fang-peng/Psyche.git
cd Psyche
cp -r skills/ex-persona ~/.workbuddy/skills/
```

### Windows PowerShell

```powershell
git clone https://github.com/wan-fang-peng/Psyche.git
cd Psyche
Copy-Item -Recurse skills\ex-persona $HOME\.workbuddy\skills\
```

复制完成后重启 WorkBuddy。

### 验证安装

```bash
ls ~/.workbuddy/skills/ex-persona
# 应看到 SKILL.md / tools/ / prompts/ / LICENSE 等
```

再跑一次自检，确认统一入口可用：

```bash
python ~/.workbuddy/skills/ex-persona/tools/extool.py where
# 应输出 skill 根目录绝对路径
```

---

## 方式二：项目级安装

只让 skill 在当前项目生效，不污染全局。

```bash
mkdir -p {你的项目}/.workbuddy/skills
cp -r skills/ex-persona {你的项目}/.workbuddy/skills/
```

相对路径写法（脚本用 `__file__` 自定位，装在哪都能跑）：

```bash
cp -r skills/ex-persona .workbuddy/skills/
```

---

## 方式三：对话导入

在 WorkBuddy 对话框输入「导入技能」，或直接把
`skills/ex-persona/SKILL.md` 拖进对话框。

注意：这种方式只导入 SKILL.md 主文件，`tools/` 和 `prompts/` 不会跟着进来，
**脚本功能会失效**。需要完整功能请用方式一或方式二。

---

## 方式四：市场安装

在 WorkBuddy 左侧「技能」面板搜索 `ex-persona`。

---

## 可选依赖

| 依赖 | 用途 | 不装会怎样 |
|------|------|-----------|
| Pillow ≥ 9.0 | 读取照片 EXIF（时间、地点） | 其余功能全部正常；`photos` 命令退化为只列出文件名并提示安装 |

安装：

```bash
pip install Pillow
```

---

## 手动调用脚本（进阶）

一般不需要直接用，skill 会自动调用。排查问题时可用：

```bash
ET=~/.workbuddy/skills/ex-persona/tools/extool.py

python $ET where                      # 打印 skill 根目录
python $ET list                       # 列出所有已生成人格
python $ET init --slug xiaoming       # 初始化目录
python $ET versions --slug xiaoming   # 查历史版本
python $ET rollback --slug xiaoming --version v1

python $ET parse-wechat --file 记录.txt --target 小明 --output 分析.md
python $ET parse-qq --file 记录.txt --target 小明 --output 分析.md
python $ET parse-social --dir 截图目录 --output 分析.md
python $ET photos --dir 照片目录 --output 时间线.md
```

`--base-dir` 指定输出根目录，默认为当前目录下的 `./exes`。

### Windows 提示

脚本文档里如果看到 `python3`，在 Windows 上换成 `python`。
更稳妥的做法是用 WorkBuddy 托管解释器的绝对路径：

```
C:\Users\<用户名>\.workbuddy\binaries\python\envs\default\Scripts\python.exe
```

`extool.py` 内部用 `sys.executable` 转发子命令，所以你用哪个解释器调它，
内部就跟着用哪个，不存在解释器不一致的问题。

---

## 卸载

```bash
rm -rf ~/.workbuddy/skills/ex-persona
```

已生成的人格数据在 `exes/` 目录，不在 skill 目录内，需要的话单独删。
