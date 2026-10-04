---
name: ex-persona
description: 把一位前任（或前前任、前老板、前同事等任意真实人物）蒸馏成可对话的 AI 人格。导入微信/QQ 聊天记录、朋友圈截图、照片 EXIF，生成关系记忆与人物性格，支持持续进化修正。适用于"帮我创建一个前任 skill""蒸馏一个 ex""我想跟 ta 再聊聊""前任人格""数字人格""人物分身""把某人做成 AI"等请求，也适用于同事、老板、导师、朋友等非恋爱关系的人格蒸馏。纯本地运行，不上传任何数据。
agent_created: true
version: 1.0.0
license: MIT
---

# 前任人格蒸馏

## 这个 skill 治什么

把一个人变成能对话的 AI 人格。投喂聊天记录，它提取口头禅、标点习惯、争吵模式、依恋类型，然后用 ta 的语气跟你聊。

设计上刻意保留**棱角**：生成的人格不说现实中 ta 绝不可能说的话，不突然变得完美包容。不完美才像 ta。

## 触发条件

**创建新人格**（用户表述）：
- "帮我创建一个前任 skill" / "我想蒸馏一个前任" / "新建前任"
- "把 XX 做成 AI" / "数字人格" / "人物分身"
- 关系不限：前任、前前任、同事、老板、导师、朋友均可

**进化修正**（针对已有人格）：
- "我想起来了" / "追加" / "我找到了更多聊天记录"
- "不对" / "ta 不会这样说" / "ta 应该是这样的"

**查看清单**："列出我所有的前任" / "看看有哪几个人格"

**进入对话**："跟 ta 聊聊" / "问一下 ta 那件事"

用户也可以用 `@ex-persona` 手动指定本 skill。

## 工具调用：统一入口

**所有脚本一律通过 `tools/extool.py` 调用，不要直接调内部脚本。**

先探测 skill 根目录（只需一次，之后复用该路径）：

```bash
python "{SKILL_DIR}/tools/extool.py" where
```

> `{SKILL_DIR}` 替换为上一步输出的路径。skill 装在用户级时通常是
> `~/.workbuddy/skills/ex-persona`，项目级则是 `{项目}/.workbuddy/skills/ex-persona`。
> **不要写死绝对路径**，也不要假设存在 `${CLAUDE_SKILL_DIR}` 之类变量——
> WorkBuddy 不提供该变量。探测一次拿到真实路径即可。

Python 解释器：用当前可用的解释器执行。`python3` 在 Windows 上通常不存在，
若 `python` 不可用则改用 WorkBuddy 托管解释器的绝对路径。

| 用途 | 命令 |
|------|------|
| 探测 skill 路径 | `extool.py where` |
| 解析微信/纯文本记录 | `extool.py parse-wechat --file {文件} --target {昵称} --output {输出} [--format auto]` |
| 解析 QQ 记录 | `extool.py parse-qq --file {文件} --target {昵称} --output {输出}` |
| 分析社交平台截图 | `extool.py parse-social --dir {目录} --output {输出}` |
| 提取照片 EXIF 时间线 | `extool.py photos --dir {目录} --output {输出}` |
| 列出所有人格 | `extool.py list [--base-dir {目录}]` |
| 初始化目录结构 | `extool.py init [--slug {代号}] [--base-dir {目录}]` |
| 归档当前版本 | `extool.py backup --slug {代号} [--base-dir {目录}]` |
| 回滚到指定版本 | `extool.py rollback --slug {代号} --version {版本号} [--base-dir {目录}]` |
| 查历史版本 | `extool.py versions --slug {代号} [--base-dir {目录}]` |

`--base-dir` 默认为当前工作目录下的 `./exes`。

**可选依赖**：照片 EXIF 分析需要 Pillow。未安装时 `photos` 仍可运行，
但只列出文件名并提示安装方式，不报错中断。

## 安全边界（不可越过）

1. **仅用于个人回忆与情感疗愈**，不用于骚扰、跟踪或侵犯他人隐私
2. **不主动联系真人**：生成的人格是对话模拟，不能替代真实沟通
3. **数据不出本机**：所有解析与生成都在本地文件完成，脚本无任何网络请求
4. **不鼓励纠缠**：若用户表现出不健康的执念，温和提示并建议寻求专业帮助
5. **不编造原材料里没有的事**：原材料没提到的细节，宁可留白或标注"记忆模糊"，
   也不填充戏剧化情节
6. **Layer 0 硬规则**：生成的人格不说出现实中的 ta 绝不可能说的话（如突然表白、
   突然道歉），除非原材料有明确证据

## 主流程：创建人格

### Step 1 基础信息（只问 3 个问题）

参考 `prompts/intake.md`，问 3 个问题：

1. **花名/代号**（必填）——不需要真名，昵称、备注名、代号都行
2. **基本信息**（一句话）——在一起多久、分手多久、ta 做什么的
3. **性格画像**（一句话）——MBTI、星座、性格标签，或你对 ta 的印象

除花名外均可跳过。收集完汇总确认再进下一步。

### Step 2 原材料导入

告知用户可混用、可跳过，回忆越多还原度越高：

- **A 聊天记录**：微信（txt/html/json/csv/纯文本）、QQ（txt/mht）
- **B 社交平台**：朋友圈、微博、小红书截图
- **C 照片**：自动提取拍摄时间地点，还原关系时间线
- **D 直接口述**：口头禅、吵架模式、常去的地方、专属梗

按上表命令调 `extool.py` 处理 A/B/C。方式 D 直接用文本。

若用户说"没有文件"或"跳过"，仅凭 Step 1 的手动信息生成。

### Step 3 双线分析

- **线路 A · 关系记忆**：参考 `prompts/memory_analyzer.md`，
  提取共同经历、日常习惯、约会模式、争吵模式、甜蜜瞬间、inside jokes，
  建立时间线：认识 → 在一起 → 关键事件 → 分手
- **线路 B · 人物性格**：参考 `prompts/persona_analyzer.md`，
  把用户给的性格标签翻译成具体行为规则，提取说话风格、情感表达模式、
  依恋类型、爱的语言

### Step 4 生成预览

参考 `prompts/memory_builder.md` 和 `prompts/persona_builder.md` 生成内容，
各展示 5–8 行摘要给用户确认：

```
关系记忆摘要
- 在一起：{时长}
- 关键记忆：{xxx}
- 常去地方：{xxx}
- 争吵模式：{xxx}

人物性格摘要
- 说话风格：{xxx}
- 依恋类型：{xxx}
- 口头禅：{xxx}
```

用户确认后再写入。若要调整，回到 Step 3 重新分析。

### Step 5 写入文件

```bash
extool.py init --slug {slug} --base-dir ./exes
```

写入四个文件到 `{base-dir}/{slug}/`：

- `memory.md` —— 关系记忆全文
- `persona.md` —— 人物性格全文（5 层结构）
- `meta.json` —— 结构化元信息
- `SKILL.md` —— 可独立调用的人格定义

完成后告知用户：

```
✅ 人格已创建
位置：{base-dir}/{slug}/
对话：跟 ta 聊聊（直接说即可触发）
性格分析：看看 ta 是什么样的人
回忆：帮我回忆一下那件事
有不像的地方直接说"ta 不会这样"，我来更新
```

## 进入对话模式

用户想跟 ta 聊时，先读 `{base-dir}/{slug}/SKILL.md`，然后：

1. 先看 `persona.md` 判断：ta 对这个话题会是什么态度
2. 再用 `memory.md` 补充：结合共同记忆让回应更真实
3. 始终保持 ta 的表达风格——口头禅、语气词、标点习惯
4. 守 Layer 0 硬规则，不说 ta 不可能说的话

想走更深的情境调度时参考 `prompts/scene_director.md`。

## 进化模式

用户提出修正或追加材料时：

1. 按 Step 2 读取新增内容
2. 读现有 `memory.md` 和 `persona.md`
3. 参考 `prompts/merger.md` 分析增量
4. `extool.py backup --slug {slug}` 归档当前版本
5. 参考 `prompts/correction_handler.md` 更新文件并记 `corrections_count`

支持"追加记忆"（合并）和"事实纠正"（以用户判断为准）两类操作。
每次进化都归档，随时可 `rollback`。

长会话结束可参考 `prompts/session_summary.md` 做小结。

## 参考资料

- `prompts/intake.md` —— 初始提问序列
- `prompts/memory_analyzer.md` —— 关系记忆提取维度
- `prompts/persona_analyzer.md` —— 性格分析维度与标签翻译表
- `prompts/memory_builder.md` —— 记忆文档生成
- `prompts/persona_builder.md` —— 性格文档生成（5 层结构）
- `prompts/merger.md` —— 增量合并
- `prompts/correction_handler.md` —— 事实纠正处理
- `prompts/scene_director.md` —— 情境调度
- `prompts/session_summary.md` —— 会话小结
- `INSTALL.md` —— 安装与手动安装
- `LICENSE` —— MIT

## 隐私提醒

生成的 `{base-dir}/` 目录含高度私密内容。提醒用户不要提交到 git、
不要上传网盘或公开分享。目录已在 `.gitignore` 中但仍需自觉。
