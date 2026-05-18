---
name: ai-level-skill
description: |
  扫描用户设备上已安装的 AI 工具、应用、配置等，综合评估 AI 能力水平，
  生成科技风 HTML 报告。包含稀有成就系统、维度雷达图、学习路线图。
  当用户想了解自己的 AI 能力水平、AI 工具装备情况时使用。
compatibility: 需要 Python 3.8+，支持 macOS 和 Windows
supported_harnesses:
  - claude-code
  - gemini-cli
  - copilot-cli
  - cursor
  - windsurf
  - opencode
  - codex-cli
---

# ai-level-skill — AI 能力水平侧写

本 Skill 通过扫描设备上已安装的 AI 工具和配置，评估用户的 AI 能力水平，生成科技风 HTML 可视化报告。

预计耗时：3-5 分钟（含 15 个维度扫描 + 5 个子代理并行评分）。

---

## 路径说明

本文件所在目录记为 `<SKILL_DIR>`。不同工具安装后的路径如下：

| AI 工具 | SKILL_DIR |
|---------|-----------|
| Claude Code | `~/.claude/skills/ai-level-skill` |
| Gemini CLI | `~/.gemini/skills/ai-level-skill` |
| GitHub Copilot CLI | `~/.copilot/skills/ai-level-skill` |
| Cursor | `~/.cursor/skills/ai-level-skill` |
| Codex CLI | `~/.codex/skills/ai-level-skill` |
| Windsurf / OpenCode | 见工具文档或执行 `pwd` 查看当前路径 |

所有脚本和引用文件均位于 `<SKILL_DIR>/scripts/` 和 `<SKILL_DIR>/references/`，报告输出到当前工作目录的 `output/` 子目录。

---

## 前置检查

确认 Python 版本满足要求，在终端运行：

```
python3 --version
```

若输出 `Python 3.8` 或更高版本，继续执行。否则提示用户先安装 Python 3.8+。

---

## Step 1：检测平台

在终端运行：

```
python3 -c "import platform; print(platform.system())"
```

- 输出 `Darwin` → macOS
- 输出 `Windows` → Windows

---

## Step 2：执行数据收集脚本

> 预计耗时 60-180 秒，含网络测速。脚本会实时输出每个维度的扫描进度，请耐心等待。

在终端运行：

```
python3 <SKILL_DIR>/scripts/collector.py
```

脚本完成后，产出 `<CWD>/output/raw_data.json`，包含 15 个维度的原始设备数据。

---

## Step 3：切分原始数据

运行数据切分脚本，将 `raw_data.json` 拆分为 5 个子文件（每文件 1-10 KB），便于并行评分：

```
python3 <SKILL_DIR>/scripts/split_data.py
```

产出文件：
- `output/slice_ui.json` — 应用程序 + 浏览器插件 + IDE 插件
- `output/slice_dev.json` — CLI 工具 + npm + Skills + Python 包
- `output/slice_model.json` — 模型配置 + API Key + 本地模型 + Docker 镜像
- `output/slice_practice.json` — Jupyter Notebook + AI 文件夹
- `output/slice_infra.json` — 设备硬件 + 网络能力

---

## Step 4：并行启动 5 个子代理评分

同时对以下 5 个文件进行 AI 分析评分（可并行进行，互相独立）。

评分规则完整参考：读取 `<SKILL_DIR>/references/scoring-prompt.md`。

> **重要：写文件必须用 Python `json.dumps()`**
> 评分结果中的描述文字可能含有引号、换行等特殊字符，直接拼写 JSON 文本极易产生语法错误。
> 所有子代理必须通过以下方式写入结果文件：
> ```python
> import json
> from pathlib import Path
> result = { ...你的评分数据... }
> Path('<CWD>/output/partial_score_X.json').write_text(
>     json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8'
> )
> ```
> 禁止直接手写 JSON 文本到文件（会因特殊字符转义问题导致文件损坏）。

---

**子代理 1 — UI 工具评分**

读取 `<CWD>/output/slice_ui.json`，按照 `references/scoring-prompt.md` 中"第 1 组：UI 工具"规则执行：
1. 若 item 已含 `is_ai` 字段，直接采用；否则识别每个工具是否属于 AI 范畴
2. 为 AI 工具赋予基础分和层级乘数
3. 判断是否触发稀有成就（R/SR/SSR）

结果结构示例（用 `json.dumps()` 写入 `<CWD>/output/partial_score_ui.json`）：

```json
{
  "dimension_group": "ui_tools",
  "dimension_scores": {
    "apps": {"score": 120, "items": [
      {
        "name": "Cursor",
        "category": "app",
        "is_ai": true,
        "base_score": 80,
        "multiplier": 1.5,
        "final_score": 120,
        "description": "AI 原生代码编辑器，深度集成多模型辅助编程",
        "reason": "AI 原生 IDE，R 级成就"
      }
    ]},
    "browser_ai_plugins": {"score": 0, "items": []},
    "ide_ai_plugins": {"score": 0, "items": []}
  },
  "group_total": 120,
  "rare_achievements": [
    {
      "level": "R",
      "title": "AI 原生 IDE 用户",
      "tool": "Cursor",
      "copy": "AI 原生 IDE 用户仍是开发者中的少数派，你比大多数人更早踏上这条路。"
    }
  ]
}
```

---

**子代理 2 — 开发者工具评分**

读取 `<CWD>/output/slice_dev.json`，按照 `references/scoring-prompt.md` 中"第 2 组：开发者工具"规则执行。

用 `json.dumps()` 将结果写入 `<CWD>/output/partial_score_dev.json`，结构同上（`dimension_group` 为 `"dev_tools"`）。

---

**子代理 3 — 模型与 API 评分**

读取 `<CWD>/output/slice_model.json`，按照 `references/scoring-prompt.md` 中"第 3 组：模型与 API"规则执行。

用 `json.dumps()` 将结果写入 `<CWD>/output/partial_score_model.json`（`dimension_group` 为 `"model_api"`）。

---

**子代理 4 — 工程实践评分**

读取 `<CWD>/output/slice_practice.json`，按照 `references/scoring-prompt.md` 中"第 4 组：工程实践"规则执行。

用 `json.dumps()` 将结果写入 `<CWD>/output/partial_score_practice.json`（`dimension_group` 为 `"practice"`）。

---

**子代理 5 — 基础设施评分**

读取 `<CWD>/output/slice_infra.json`，按照 `references/scoring-prompt.md` 中"第 5 组：基础设施"规则执行。此组评分完全基于固定规则表，无需 AI 识别。

输出写入 `<CWD>/output/partial_score_infra.json`（`dimension_group` 为 `"infra"`）。

---

## Step 5：合并评分结果

运行合并脚本，将 5 个 `partial_score_*.json` 自动合并为 `score_result.json`：

```
python3 <SKILL_DIR>/scripts/merge_scores.py
```

脚本会自动完成所有机械合并工作：
- 汇总 `group_total` 得到 `total_score`
- 合并所有 `dimension_scores` 和 `items`（兼容模型输出格式差异）
- 归一化并去重 `rare_achievements`（SSR > SR > R）
- 根据 `total_score` 确定 `title`（称号规则见下方）
- 按维度得分自动生成 `highlights` 和 `weaknesses`
- 根据当前称号填入默认 `roadmap`

**脚本完成后**，你（模型）仅需根据用户的实际工具配置情况，对以下三个语义字段做个性化优化（可选，若认为默认内容已准确则无需修改）：

- `highlights`：结合得分最高的具体工具，用 1-2 句话说明亮点
- `weaknesses`：结合具体缺失维度，给出更有针对性的建议
- `roadmap.phases[*].actions`：结合用户已有工具，给出更具体的行动建议

优化后将修改写回 `<CWD>/output/score_result.json`。

**称号规则（供参考）：**

| 总分范围 | 称号 |
|---------|------|
| 0-299 | AI 初探者 |
| 300-799 | AI 尝鲜者 |
| 800-1499 | AI 实践者 |
| 1500-2999 | AI 进阶玩家 |
| 3000-5999 | AI 工程师 |
| 6000-9999 | AI 超级用户 |
| 10000+ | AI 极客 |

---

## Step 5.5：询问用户称呼

在终端向用户询问：

> 请问怎么称呼你？（将显示在报告标题中，直接回车跳过）

运行以下命令完成此操作：

```
python3 -c "
import json, sys
from pathlib import Path
p = Path('output/score_result.json')
name = input('请问怎么称呼你？（将显示在报告标题中，直接回车跳过）: ').strip()
data = json.loads(p.read_text(encoding='utf-8'))
data['user_name'] = name
p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
print('已设置：' + (name if name else '（未设置，将显示默认标题）'))
"
```

---

## Step 6：生成 HTML 报告

在终端运行：

```
python3 <SKILL_DIR>/scripts/generate_report.py
```

脚本会同时产出**两份报告**：

| 文件 | 用途 | 内容 |
|------|------|------|
| `output/report.html` | 基础报告，适合分享 | 总分、称号、维度雷达图、稀有成就、亮点/短板、学习路线图 |
| `output/report_detail.html` | 详细报告，仅本地查阅 | 基础报告全部内容 + 各维度所有工具明细、单项得分、层级乘数 |

两份文件均为单文件 HTML，内联所有 CSS/JS，无需网络即可打开。

---

## Step 7：打开报告

**macOS — 同时打开两份报告（先开详细报告，再开分享报告，分享报告最终显示在前）：**
```
open output/report_detail.html
open output/report.html
```

**Windows — 同时打开两份报告：**
```
start output/report_detail.html
start output/report.html
```

- `report.html`：可分享给朋友的简洁版，顶部有"查看详细报告"提示
- `report_detail.html`：顶部显示橙色"仅供本地查阅"警示条，包含每个工具的得分明细

---

## Step 8：询问是否分享

在终端询问用户：

> 是否将脱敏海报部署到 Netlify 生成分享链接？（不含 API Key、工具名等敏感信息）(y/n)
> 提示：也可以直接在本地的 report.html 中点击「保存图片分享到朋友圈」按钮下载图片分享，无需部署。

**如果选择 n：** 结束，告知用户两份报告的本地路径。

**如果选择 y：** 执行分享流程：

1. 运行分享脚本：
   ```
   python3 <SKILL_DIR>/scripts/share_to_friends.py
   ```
   该脚本会依次执行：

   a. **将 report.html 部署到 Netlify**：直接部署海报页面，注入"保存图片分享到朋友圈"按钮

   b. **生成二维码**：将 Netlify 链接生成二维码，保存为 `output/qrcode.png`，同时在终端显示 ASCII 二维码

   c. **保存链接**：将链接写入 `output/share_image_url.txt`

   d. **自动重新生成 report.html**：将二维码嵌入本地 report.html 页面底部

2. 完成后在终端输出：
   ```
   ✓ 分享海报链接：https://xxx.netlify.app
   ✓ 二维码已保存：output/qrcode.png
   ✓ 已将二维码嵌入 report.html 底部
   ✓ report.html 和 report_detail.html 仍在本地
   ```

3. 重新打开 report.html 查看嵌入的二维码：
   - macOS：`open output/report.html`
   - Windows：`start output/report.html`

---

## 注意事项

- **隐私**：所有数据仅写入本地 `output/` 目录，分享需用户主动确认
- **API Key 安全**：collector.py 只记录 key 名称，绝不读取或传递 key 的实际值
- **容错**：某个维度扫描失败（如 docker 未安装、无 conda）时自动跳过，不影响其他维度
- **耗时**：网络测速约 15 秒，如超时则跳过网速测试，网络评分部分为 0
- **评分一致性**：collector.py 已内置 AI 工具白名单，评分结果不受所用 AI 模型影响
