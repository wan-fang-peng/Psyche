# 前任人格蒸馏 · ex-persona

把一个人从聊天记录里蒸馏出来，变成能对话的 AI 人格。

投喂微信/QQ 聊天记录、朋友圈截图、照片 EXIF，它会提取 ta 的口头禅、标点习惯、
争吵模式、依恋类型，然后用 ta 的语气跟你聊。

**纯本地运行，所有脚本零网络请求，数据不出你的电脑。**

---

## 这个 skill 适合谁

- 想复盘一段关系、想有个能随时说说话的地方
- 想把某个人的沟通方式留下来（比如导师、同事、老板的工作风格）
- 对"AI 能不能记住具体的人"这件事好奇，想自己动手做一个

**不适合**：想拿去骚扰、跟踪或侵犯他人隐私的场合。skill 内置了硬性边界，
详见下方「安全边界」。

---

## 快速开始

### 方式一：直接安装（推荐）

```
git clone https://github.com/wanfa/ex-persona-skill.git
cd ex-persona-skill
cp -r skills/ex-persona ~/.workbuddy/skills/
```

Windows：

```powershell
git clone https://github.com/wanfa/ex-persona-skill.git
cd ex-persona-skill
Copy-Item -Recurse skills\ex-persona $HOME\.workbuddy\skills\
```

重启 WorkBuddy 后直接说「帮我创建一个前任」即可触发。

也支持项目级安装，只在当前项目生效：

```bash
cp -r skills/ex-persona {你的项目}/.workbuddy/skills/
```

### 方式二：市场安装

在 WorkBuddy 左侧「技能」面板中搜索 `ex-persona`。

### 依赖

**无必需依赖。** 照片 EXIF 分析需要 Pillow（可选）：

```bash
pip install Pillow
```

未安装时其余功能全部正常，照片功能会退化为只列出文件名。

---

## 怎么用

跟 WorkBuddy 说人话就行，不用记命令：

| 你说 | 它会做 |
|------|--------|
| 帮我创建一个前任 | 问 3 个基础问题，然后带你走投喂流程 |
| 我想跟 ta 聊聊 | 载入人格，用 ta 的语气对话 |
| 看看 ta 是什么样的人 | 性格画像分析，含恋爱里的小毛病 |
| 帮我回忆一下那件事 | 共同经历时间线梳理 |
| ta 不会这样说 | 触发修正，纠正后归档旧版本 |
| 我找到了更多聊天记录 | 追加材料，合并进现有人格 |
| 列出我所有的前任 | 列出全部已生成的人格 |

也可以 `@ex-persona` 手动指定。

> **想分享你自己做的 skill？** 见 [SHARE-GUIDE.md](SHARE-GUIDE.md)，
> 里面写了 GitHub / zip / 市场三条路怎么走，以及 WorkBuddy 上两个**不能用**的
> 常见做法（`npx skills add`、拖拽导入 SKILL.md）及其原因。

### 投喂什么

按你手上有什么来，可混用、可跳过：

- **聊天记录** —— 微信导出（txt/html/json/csv）、QQ 导出（txt/mht）、直接粘贴的纯文本
- **社交动态** —— 朋友圈、微博、小红书截图
- **照片** —— 自动提取拍摄时间地点，还原关系时间线
- **纯口述** —— 口头禅、吵架模式、常去的地方、专属梗

回忆投得越多，还原度越高。但**不投也行**，只凭几个关键词也能生成基础版。

---

## 输出长什么样

每个前住在 `exes/{代号}/` 下（可自定义位置）：

```
exes/xiaoming/
├── SKILL.md      可独立调用的人格定义
├── memory.md     关系记忆（共同经历、时间线、争吵模式）
├── persona.md    人物性格（5 层结构）
├── meta.json     结构化元信息
└── versions/     历史版本，可回滚
```

每次修正都自动归档，随时可以回退。

---

## 隐私

- 所有解析和生成都在本地文件完成，**脚本不发起任何网络请求**
- 只有依赖 Pillow 用于读取照片 EXIF
- `exes/` 目录已在 `.gitignore` 中，但仍请自觉：不要提交到 git，不要上传网盘或公开分享

底层脚本经过安全审计：无 `requests`/`urllib`/`subprocess` 网络调用，
无 `eval`/`exec`，文件写入全部限定在 `exes/` 目录内。

---

## 安全边界

skill 内置以下不可越过的规则：

1. 仅用于个人回忆与情感疗愈，不用于骚扰、跟踪或侵犯他人隐私
2. 不主动联系真人——生成的人格是对话模拟，不能替代真实沟通
3. 数据不出本机
4. 不鼓励纠缠——若你表现出不健康的执念，它会温和提示
5. **不编造原材料里没有的事**，宁可留白也不填充戏剧化情节
6. **Layer 0 硬规则**：人格不说出现实中的 ta 绝不可能说的话（如突然表白、突然道歉），
   除非原材料有明确证据

设计上刻意保留「棱角」：不完美才像 ta。

---

## 致谢与许可

本项目派生自 **[therealXiaomanChu/ex-skill](https://github.com/therealXiaomanChu/ex-skill)**
（原项目名「前任.skill」），遵循其 MIT 协议，原始版权声明保留在
`skills/ex-persona/LICENSE`。感谢原作者的创意与开源精神。

### 本项目相对原版的改动

| 改动 | 原因 |
|------|------|
| 新增 `tools/extool.py` 统一入口 | 原版文档用 `${CLAUDE_SKILL_DIR}` 定位脚本，WorkBuddy 无此变量；新入口用 `__file__` 自定位，用户级/项目级安装通用 |
| 统一入口用 `sys.executable` | 原版脚本文档统一写 `python3`，Windows 上不存在该命令 |
| 触发方式改为自然语言 + `@技能名` | 原版用 Claude Code 斜杠命令 `/create-ex`，WorkBuddy 不支持 |
| frontmatter 加 `agent_created: true` | WorkBuddy 规范要求，否则后续无法修改该 skill |
| 修复 `parse_plaintext` 统计失效 | 原版纯文本解析不切分消息，输出统计全是 `N/A`；现按「发送者: 内容」切分并复用完整分析链路 |
| 补 `INSTALL.md`、README、plugin.json | 便于分发与市场安装 |

原版分析能力（口头禅/标点/emoji/依恋类型/时间线）全部保留。

## License

MIT
