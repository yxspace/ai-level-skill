# AI 能力水平侧写 (ai-level-skill)

> 一款通用 AI Skill，扫描你的设备，生成科技风 HTML 报告，告诉你自己在全球 AI 用户中处于什么水平。

支持：Claude Code · Gemini CLI · GitHub Copilot CLI · Cursor · Windsurf · OpenCode · Codex CLI

---

## 它能做什么

扫描本机 **15 个维度**的 AI 装备情况，生成包含以下内容的互动 HTML 报告：

- **总分 + 称号**（AI 初探者 → AI 极客，共 7 档）
- **维度雷达图**（应用 / CLI / Python 包 / 模型配置 / 硬件 / 网络等）
- **稀有成就系统**（R / SR / SSR 三级，触发条件基于真实工具配置）
- **亮点 & 短板分析**
- **三阶段学习路线图**（近期 / 中期 / 长期）
- **详细工具明细**（每个工具的得分、乘数、一句话介绍）

扫描的 15 个维度：

| # | 维度 | 举例 |
|---|------|------|
| 1 | 应用程序 | Cursor, LM Studio, 豆包 |
| 2 | 终端 CLI 工具 | claude, aider, ollama, vllm |
| 3 | npm 全局包 | openai, langchain, @anthropic-ai/claude-code |
| 4 | AI Skills | 安装的 Skill 数量与内容 |
| 5 | 模型配置 | Cursor / Aider / Claude Code 当前使用的模型 |
| 6 | Python AI 包 | torch, transformers, langchain, autogen |
| 7 | IDE AI 插件 | GitHub Copilot, Codeium, Continue |
| 8 | AI 文件夹 | ~/ai, ~/llm, ~/projects/ai 等 |
| 9 | 设备硬件 | Apple Silicon 型号 / 内存 / GPU |
| 10 | 网络能力 | 国际 AI 服务可达性 / VPN / 网速 |
| 11 | 本地模型文件 | .gguf / .bin / .safetensors 文件 |
| 12 | AI API Key | 检测到的 Key 名称（不含 Key 值） |
| 13 | 浏览器 AI 插件 | Monica, Sider, 沉浸式翻译 |
| 14 | Docker AI 镜像 | vllm, ollama, text-generation-inference |
| 15 | Jupyter Notebook | 数量 + AI 相关 import 检测 |

---

## 快速开始

### 要求

- Python 3.8+（标准库，无需额外安装第三方包）
- macOS 或 Windows

### 安装

将此仓库克隆到对应 AI 工具的 Skills 目录：

**Claude Code**
```bash
git clone https://github.com/yxspace/ai-level-skill \
  ~/.claude/skills/ai-level-skill
```

**Gemini CLI**
```bash
git clone https://github.com/yxspace/ai-level-skill \
  ~/.gemini/skills/ai-level-skill
```

**GitHub Copilot CLI**
```bash
git clone https://github.com/yxspace/ai-level-skill \
  ~/.copilot/skills/ai-level-skill
```

**Cursor**
```bash
git clone https://github.com/yxspace/ai-level-skill \
  ~/.cursor/skills/ai-level-skill
```

**Codex CLI**
```bash
git clone https://github.com/yxspace/ai-level-skill \
  ~/.codex/skills/ai-level-skill
```

**Windsurf / OpenCode**：将仓库克隆到该工具的 skills 目录，并将 `SKILL.md` 添加到工具的 context 中。

### 运行

在任意工作目录下，向 AI 助手发送：

```
/ai-level-skill
```

或直接说：**"帮我评估一下我的 AI 能力水平"**。

AI 将自动执行扫描 → 评分 → 生成报告的完整流程，耗时约 3-5 分钟。

---

## 报告预览

生成两份 HTML 文件：

| 文件 | 适合 | 内容 |
|------|------|------|
| `output/report.html` | 分享给朋友 | 总分 + 称号 + 雷达图 + 成就 + 路线图 |
| `output/report_detail.html` | 本地自查 | 以上全部 + 每个工具的得分明细 |

两份文件均为**单文件 HTML**，无需网络，可直接用浏览器打开。

### 在线分享

运行完成后，Skill 会询问是否部署到 Netlify（需要提前安装并登录 `netlify-cli`）。

也可以在本地 `report.html` 页面内点击**「保存图片分享到朋友圈」**按钮，直接下载 PNG 海报，无需任何部署。

---

## 评分说明

### 称号体系

| 总分 | 称号 | 大致画像 |
|------|------|--------|
| 0-299 | AI 初探者 | 刚开始了解 AI 工具 |
| 300-799 | AI 尝鲜者 | 在用主流 AI 产品 |
| 800-1499 | AI 实践者 | 已在工作流中使用 AI |
| 1500-2999 | AI 进阶玩家 | 掌握多种 AI 工具链 |
| 3000-5999 | AI 工程师 | 能构建 AI 应用 |
| 6000-9999 | AI 超级用户 | 深度 AI 工作流，具备训练/部署能力 |
| 10000+ | AI 极客 | 前沿 AI 能力，顶级配置 |

### 稀有成就（部分示例）

| 等级 | 触发条件 | 标题 |
|------|---------|------|
| R | 安装 Cursor / Windsurf | AI 原生 IDE 用户 |
| R | 有 Claude Code CLI | 前沿 AI 编程工具用户 |
| SR | 有 aider 或 fabric | AI 工程师工作流 |
| SR | 有 torch 或 tensorflow | 深度学习框架用户 |
| SR | 配置了 Anthropic API Key | AI API 调用者 |
| SSR | 有 autogen / crewai / langgraph | AI Agent 构建者 |
| SSR | 本地运行 70B+ 模型 | 本地 AI 研究者 |
| SSR | 同时持有 3 个以上 AI API Key | 专业 AI 开发者 |
| SSR | M4/M5 Max/Ultra 芯片 | 顶级 AI 推理硬件 |

### 评分一致性

collector.py 内置了 300+ 条 AI 工具白名单，`is_ai` 字段由 Python 确定性规则预标注，**不依赖 AI 模型的知识储备**，保证不同模型评分结果一致。

---

## 隐私说明

- **所有数据只写入本地** `output/` 目录，不上传到任何服务器
- **API Key 安全**：只记录 Key 的变量名（如 `ANTHROPIC_API_KEY`），**绝不读取或传递 Key 的实际值**
- **分享需主动确认**：Netlify 部署需用户明确输入 `y` 才会执行
- 如不需要分享，输入 `n`，报告仅在本地生成

---

## 依赖的外部工具（可选）

以下工具非必须，缺失时对应维度自动跳过：

| 工具 | 用途 | 安装方式 |
|------|------|--------|
| `brew` | 扫描 Homebrew 安装的 CLI 工具 | [brew.sh](https://brew.sh) |
| `npm` | 扫描 npm 全局包 | 随 Node.js 安装 |
| `docker` | 扫描 AI Docker 镜像 | [docker.com](https://docker.com) |
| `conda` | 扫描 conda 环境中的 Python 包 | [conda.io](https://docs.conda.io) |
| `mas` | 扫描 Mac App Store 应用 | `brew install mas` |
| `netlify-cli` | 部署分享海报（可选） | `npm install -g netlify-cli` |
| `qrcode[pil]` | 生成分享二维码（可选） | 脚本自动安装 |
| `requests` | sm.ms 图片上传（可选） | 脚本自动安装 |

---

## 文件结构

```
ai-level-skill/
├── SKILL.md                  # Skill 入口（AI 工具加载此文件）
├── references/
│   └── scoring-prompt.md     # 5 个评分子代理的完整规则
└── scripts/
    ├── collector.py          # 设备扫描（15 维度，含 AI 工具白名单）
    ├── split_data.py         # 将 raw_data.json 切分为 5 个子文件
    ├── generate_report.py    # 生成 report.html + report_detail.html
    ├── generate_share_card.py# 生成脱敏分享卡片 PNG（可选）
    └── share_to_friends.py   # 部署到 Netlify + 生成二维码（可选）
```

---

## License

Apache 2.0 — see [LICENSE](LICENSE) for details.
