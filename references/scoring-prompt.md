# ai-level-skill 评分规则参考

本文档供子代理评分时参考。每个子代理只处理自己负责的那组数据，按以下规则打分后输出 `partial_score_*.json`。

---

## 重要：is_ai 字段优先级

collector.py 已内置白名单，**当 raw_data 中某工具已有 `is_ai` 字段时，直接信任该值，无需重新判断**。
只有当 `is_ai` 字段不存在时，才按下方规则自行推断。

---

## 输出格式（所有子代理统一）

```json
{
  "dimension_group": "ui_tools",
  "items": [
    {
      "name": "工具名称",
      "category": "app | cli | npm | skill | python | ide_plugin | browser_plugin | docker | model | local_model",
      "is_ai": true,
      "base_score": 60,
      "multiplier": 1.5,
      "final_score": 90,
      "description": "一句话工具介绍，说明它的功能定位（15-40字）",
      "reason": "判断理由"
    }
  ],
  "dimension_scores": {
    "维度名": {"score": 0, "items": []}
  },
  "group_total": 90,
  "rare_achievements": [
    {
      "level": "R | SR | SSR",
      "title": "成就标题",
      "tool": "触发工具名",
      "copy": "一句话背书文案，强调稀有性"
    }
  ]
}
```

---

## 核心评分原则

1. **先检查 is_ai 字段，再识别，后打分**：若 raw_data 中工具已有 `is_ai` 字段，直接采用；否则对 apps、cli_tools 等非纯 AI 维度先判断 `is_ai`，只有 `is_ai: true` 的工具才参与计分
2. **得分公式**：`final_score = base_score × multiplier`
3. **模型加成**：从模型配置读取到具体模型时，在 group_total 上额外加上模型加成分
4. **稀有成就**：满足触发条件时添加到 `rare_achievements`，同一工具只保留最高等级

---

## 第 1 组：UI 工具（slice_ui.json）

### 维度：应用程序（apps）

**基础分：80 分/个 AI 应用**

层级乘数（根据工具门槛判断）：

| 工具门槛 | 代表工具 | 乘数 |
|---------|---------|------|
| 消费级 App（国内大厂） | 豆包、文心一言、智能助手、讯飞输入法 | ×0.5 |
| 主流 AI 助手 | ChatGPT（客户端）、Claude.ai、Perplexity | ×1.0 |
| AI 编程 IDE | Cursor、Windsurf、Void、Zed（AI 版） | ×1.5 |
| 本地推理客户端 | Ollama（桌面版）、LM Studio、Jan | ×2.5 |
| 其他 AI 工具 | 根据实际用途判断 | ×0.5-2.5 |

非 AI 工具（浏览器、Office、音乐播放器等）：`is_ai: false`，不计分。

**典型 AI 应用识别列表（partial，遇到不在列表的工具根据名称和描述综合判断）：**
- Cursor, Windsurf, Void → AI 编程 IDE ×1.5
- ChatGPT, Claude, Perplexity, Poe → AI 助手 ×1.0
- LM Studio, Jan → 本地推理客户端 ×2.5
- 豆包, 文心一言, 通义千问（App）, 讯飞星火 → 消费级 ×0.5
- Raycast（含 AI 扩展）→ AI 生产力工具 ×1.0
- Stable Diffusion（客户端）, ComfyUI → AI 创作工具 ×1.5
- Runway, Adobe Firefly → AI 创作工具 ×1.5

### 维度：浏览器 AI 插件（browser_ai_plugins）

**基础分：50 分/个**

乘数一律 ×1.0（浏览器插件门槛相近）。

已知 AI 插件：ChatGPT for Google、Monica、Sider、Merlin、Perplexity、沉浸式翻译、OpenAI Translator、Copilot（浏览器内置除外）、Kimi 助手。

### 维度：IDE AI 插件（ide_ai_plugins）

**基础分：100 分/个**

乘数：
- GitHub Copilot → ×1.5（订阅制，表明愿意付费）
- Continue、Codeium → ×1.0
- Tabnine → ×1.0
- Cursor 相关插件 → ×1.5
- 其他 AI 辅助编码插件 → ×1.0

**稀有成就（UI 工具组）：**
- Cursor 或 Windsurf → R 级：「AI 原生 IDE 用户仍是开发者中的少数派，你比大多数人更早踏上这条路。」
- GitHub Copilot → R 级：「GitHub Copilot 是全球最广泛使用的 AI 编程辅助工具，你已是主动拥抱 AI 编程的开发者。」

---

## 第 2 组：开发者工具（slice_dev.json）

### 维度：终端工具（cli_tools）

**基础分：125 分/个 AI CLI 工具**

#### 识别规则（按优先级）

**规则 1 — 精确名称白名单（直接判定 `is_ai: true`，无需进一步判断）：**

| 工具名称（PATH 可执行文件名） | 乘数 |
|---|---|
| `claude`, `claude-code` | ×2.0 |
| `aider` | ×2.0 |
| `fabric` | ×2.0 |
| `ollama` | ×2.5 |
| `llm` | ×2.0 |
| `rtk` | ×2.0 |
| `sgpt`, `shell-gpt` | ×2.0 |
| `jan` | ×2.0 |
| `comfy`, `comfyui` | ×2.5 |
| `vllm` | ×3.0 |
| `llamafile` | ×3.0 |
| `lms` | ×2.0 |
| `openai` | ×2.0 |
| `gpt-engineer`, `gpt_engineer` | ×2.5 |
| `ai-shell` | ×2.0 |
| `gorilla-cli` | ×2.0 |
| `gptcommit` | ×2.0 |
| `whisper`, `openai-whisper` | ×2.0 |
| `stable-diffusion-webui` | ×2.5 |
| `sd-webui` | ×2.5 |
| `automatic1111` | ×2.5 |
| `invokeai` | ×2.5 |
| `mlc-chat`, `mlc_chat` | ×2.5 |
| `mlc-llm` | ×2.5 |
| `lmstudio` | ×2.0 |
| `litellm` | ×2.5 |
| `dspy` | ×2.5 |
| `promptfoo` | ×2.0 |
| `continue` | ×2.0 |
| `cody` | ×2.0 |
| `codeium` | ×2.0 |
| `copilot` | ×2.0 |
| `tabnine` | ×2.0 |
| `cursor` | ×2.0 |
| `windsurf` | ×2.0 |
| `mods` | ×2.0 |
| `gum` | ×1.5 |
| `groq` | ×2.0 |
| `perplexity` | ×2.0 |
| `huggingface-cli`, `huggingface_hub` | ×2.0 |
| `datasets-cli` | ×1.5 |
| `transformers-cli` | ×2.0 |
| `optimum-cli` | ×2.0 |
| `accelerate` | ×2.5 |
| `peft` | ×2.5 |
| `torchrun` | ×2.5 |
| `deepspeed` | ×3.0 |
| `axolotl` | ×3.0 |
| `lora-scripts` | ×3.0 |
| `mlflow` | ×2.0 |
| `wandb` | ×2.0 |
| `ray`, `ray-train` | ×2.5 |
| `dvc` | ×2.0 |
| `bentoml` | ×2.5 |
| `triton`, `tritonclient` | ×3.0 |
| `onnxruntime`, `onnx` | ×2.5 |
| `ctranslate2` | ×2.5 |
| `exllama`, `exllamav2` | ×2.5 |
| `koboldcpp` | ×2.5 |
| `llama.cpp`, `llama-cpp-python` | ×2.5 |
| `llama-server`, `llama-cli` | ×2.5 |
| `text-generation-inference`, `tgi` | ×3.0 |
| `openvino` | ×2.5 |

**规则 2 — 名称关键词匹配（工具名本身包含以下词时，判定 `is_ai: true`，乘数 ×1.5-2.0）：**

名称含以下子字符串之一（不区分大小写，须是完整词或词首/词尾，避免误匹配 `nginx` 等）：
`llm`, `gpt`, `claude`, `openai`, `anthropic`, `gemini`, `mistral`, `llama`, `falcon`,
`bert`, `diffusion`, `stable-diff`, `whisper`, `copilot`, `codeium`, `tabnine`,
`aider`, `langchain`, `hugging`, `transformers`, `embedding`, `vector-db`,
`rag`, `-ai`, `ai-`, `_ai`, `ai_`

例：`my-ai-tool` 含 `ai-` → `is_ai: true` ×1.5

**规则 3 — 描述内容判断（前两条规则未命中时）：**

如果 raw_data 中该工具有 `description` 字段，且描述提到以下词之一，判定 `is_ai: true`：
`machine learning`, `AI`, `LLM`, `neural`, `inference`, `language model`, `code generation`

**规则 4 — 保守判断（前三条均未命中）：**

对于完全陌生且无描述的工具，**默认 `is_ai: false`**（避免误计分普通系统工具）。

非 AI CLI 工具（git、node、brew、curl、python、pip、ruby、cargo、go、make、cmake 等通用开发工具）：`is_ai: false`，不计分。

乘数汇总：

| 工具类型 | 乘数 |
|---------|------|
| 模型部署/服务端推理工具 | ×3.0 |
| 本地推理运行时 | ×2.5 |
| 主流 AI CLI / AI 编程助手 | ×2.0 |
| 关键词匹配 / 通用 AI 工具 | ×1.5 |

### 维度：npm 全局包（npm_globals）

**基础分：70 分/个 AI npm 包**

乘数：
- `@anthropic-ai/claude-code` → ×2.0
- `openai` → ×1.5
- `langchain` → ×2.0
- `netlify-cli` / `vercel` → ×0.5（非 AI 专属，但关联 AI 部署）
- AI 相关工具包 → ×1.0-2.0

主要 AI npm 包（名称含以下关键词视为 AI 工具）：
`openai`、`anthropic`、`langchain`、`llamaindex`、`@huggingface`、`ollama`、`@google/generative-ai`、`groq-sdk`、`claude-code`

非 AI npm 包：`typescript`、`eslint`、`prettier`、`webpack` 等 → 不计分。

### 维度：Skills（claude_skills）

**基础分：60 分/个 skill（无论内容如何）**

乘数：一律 ×1.0

理由：安装 Skills 本身已是高门槛行为，每个 skill 均视为 AI 工具。

**稀有成就（开发者工具组）：**
- 有 aider 或 fabric → SR 级：「使用 aider/fabric 这类专业 AI CLI 工具，你已进入真正的 AI 工程师工作流，超越约 95% 的普通 AI 用户。」
- 有 ≥ 5 个 Skills → SR 级：「配置了 5 个以上 Skills，你的 AI 工作流高度定制化，这类系统性 AI 运用能力极为罕见。」
- 有 claude（Claude Code）→ R 级：「Claude Code 用户仍是 AI 开发者中的少数，你在使用最前沿的 AI 辅助编程工具之一。」

### 维度：Python AI 包（python_ai_packages）

**基础分：80 分/个 AI Python 包**

乘数：

| 包类型 | 代表包 | 乘数 |
|-------|-------|------|
| 深度学习框架 | torch（PyTorch）、tensorflow、jax | ×3.0 |
| 大模型训练/微调 | transformers、accelerate、peft | ×3.0 |
| AI 应用框架 | langchain、langchain-*、llama-index | ×2.5 |
| AI Agent 框架 | autogen、crewai、langgraph | ×3.0 |
| API 客户端 | openai、anthropic、groq、mistralai | ×1.5 |
| 向量数据库 | chromadb、faiss-cpu、faiss-gpu、pinecone | ×2.0 |
| 嵌入/相似度 | sentence-transformers、tiktoken | ×2.0 |
| 图像生成 | diffusers、controlnet | ×2.5 |
| 其他 AI 包 | huggingface-hub、datasets、evaluate | ×1.5 |

**稀有成就（Python AI 包）：**
- 有 torch 或 tensorflow → SR 级：「安装了深度学习框架，意味着你具备 AI 模型训练能力，超越绝大多数 AI 用户。」
- 有 autogen 或 crewai 或 langgraph → SSR 级：「使用 AI Agent 框架意味着你在构建自主 AI 系统，这是 AI 能力金字塔顶端的技能。」

### 维度：环境变量 AI 配置（env_ai_config）

**基础分：30 分/个 AI 相关环境变量**

乘数：
- API Key 类（变量名含 API_KEY） ×5.0（直接暴露了 API 付费能力）
- 模型配置类（变量名含 MODEL、BASE_URL） ×3.0
- 服务端点类（变量名含 ENDPOINT、URL、HOST） ×2.0
- 其他 AI 相关变量 ×1.0

**稀有成就（环境变量）：**
- 有 ≥ 5 个 AI 环境变量 → SR 级：「在 shell 配置中管理多个 AI 环境变量，说明你已将 AI 深度融入日常开发工作流，这是专业 AI 工程师的标志。」
- 有 ≥ 3 个 AI API Key 环境变量 → SSR 级：「配置了 3 个以上 AI API Key，你的 AI 工具链完备程度已达到专业水平，只有极少数开发者会这样做。」

---

## 第 3 组：模型与 API（slice_model.json）

### 维度：模型配置（model_configs）

不提供基础分，通过"模型加成"计分：

| 档位 | 代表模型 | 加分 |
|------|---------|------|
| 旗舰级 | claude-opus-\*、gpt-4o、o1、o3、gemini-ultra | +500 分/个 |
| 主力级 | claude-sonnet-\*、gpt-4、gemini-pro、llama-3.1-405b | +300 分/个 |
| 经济级 | gpt-3.5-turbo、deepseek-v\*、qwen-plus、claude-haiku-\* | +150 分/个 |
| 本地开源 | llama-\*（本地）、mistral（本地）、qwen（本地）| +200 分/个 |

同一模型在多处配置中出现只计一次。模型名称判断：按字符串模糊匹配（不区分大小写）。

**稀有成就（模型配置）：**
- 配置了 claude-opus 系列 → SSR 级：「你配置了全球最贵的 AI 模型之一，愿意为最强 AI 能力付费的用户不足 1%，你是其中之一。」
- 配置了 gpt-4o 或 o1/o3 → SSR 级：「你在使用 OpenAI 旗舰模型，这意味着你对 AI 能力有极高要求并愿意为此付费。」
- 同时配置了 ≥ 3 种不同厂商的模型 → SSR 级：「同时使用多个顶级 AI 服务，你的 AI 工具链完备程度已达到专业 AI 工程师水平。」

### 维度：AI API Key（api_keys）

注意：此维度只记录了 key 名称，不含 key 值。按 key 名称打分：

| API Key | 加分 |
|---------|------|
| ANTHROPIC_API_KEY | +400 |
| OPENAI_API_KEY | +350 |
| GEMINI_API_KEY | +250 |
| GROQ_API_KEY | +200 |
| MISTRAL_API_KEY | +180 |
| DEEPSEEK_API_KEY | +150 |
| DASHSCOPE_API_KEY（通义） | +150 |
| MOONSHOT_API_KEY（月之暗面） | +150 |
| ZHIPUAI_API_KEY（智谱） | +120 |
| SPARK_API_KEY（讯飞） | +100 |
| AZURE_OPENAI_API_KEY | +300 |
| TOGETHER_API_KEY | +150 |
| PERPLEXITY_API_KEY | +150 |
| 其他 AI API Key | +100 |

同一服务多个 key 只计一次。

**稀有成就（API Key）：**
- 有 ANTHROPIC_API_KEY → SR 级：「配置了 Anthropic API Key，你在直接调用顶级 AI API，超越绝大多数只用聊天界面的用户。」
- 有 ≥ 3 个不同厂商的 API Key → SSR 级：「同时持有 3 个以上 AI API Key，意味着你在构建实际的 AI 应用，这是 1% 用户才有的配置。」
- 有 ≥ 2 个 API Key → R 级：「配置了多个 AI API Key，你已从 AI 用户进化为 AI 开发者。」

### 维度：本地模型文件（local_models）

| 模型参数量 | 加分 |
|-----------|------|
| ≥ 70B | +800 |
| 34B-69B | +500 |
| 13B-33B | +300 |
| 7B-12B | +200 |
| < 7B | +80 |

**稀有成就（本地模型）：**
- 有 ≥ 70B 模型 → SSR 级：「本地运行 70B+ 大模型，你拥有的硬件和技术能力超越了 99% 的 AI 用户，进入了真正的本地 AI 研究者领域。」
- 有 ≥ 34B 模型 → SR 级：「能在本地跑 34B+ 大模型，你已超越绝大多数 AI 用户的技术边界，进入真正的 AI 工程师领域。」
- 有任意本地模型 → R 级：「本地运行 AI 模型的用户仍是少数，你已跨越了从云端到本地的关键门槛。」

### 维度：Docker AI 镜像（docker_ai_images）

**基础分：120 分/个 AI 镜像**

乘数：
- vllm、localai、text-generation-inference → ×3.0（服务端推理，门槛极高）
- ollama（Docker 版）、comfyui → ×2.5
- pytorch（含 cuda）、tensorflow（含 GPU） → ×2.0
- 其他 AI 相关镜像 → ×1.5

**稀有成就（Docker AI 镜像）：**
- 有 vllm 或 localai 或 text-generation-inference → SR 级：「使用 Docker 部署 AI 推理服务，你已在构建真正的 AI 服务端基础设施，这是 AI 工程师级别的技能。」

---

## 第 4 组：工程实践（slice_practice.json）

### 维度：Jupyter Notebook（jupyter）

| 条件 | 加分 |
|------|------|
| 已安装 Jupyter | +100 |
| Notebook 数量 1-5 个 | +100 |
| Notebook 数量 6-20 个 | +200 |
| Notebook 数量 > 20 个 | +350 |
| 检测到 AI 相关 import（torch/transformers/openai 等） | +200 |
| 有 GPU 相关 kernel（pytorch/cuda 等） | +150 |

**稀有成就（Jupyter）：**
- 已安装 Jupyter + 有 AI 相关 import → SR 级：「有 Jupyter Notebook + AI 库使用记录，这是活跃的 AI 开发者最典型的信号之一。」

### 维度：AI 文件夹（ai_home_folders）

**基础分：40 分/个含 AI 关键词的目录**

乘数：一律 ×1.0

无稀有成就（此维度权重较低）。

---

## 第 5 组：基础设施（slice_infra.json）

### 维度：设备硬件（hardware）

此维度完全基于固定规则表，无需 AI 识别，按以下公式计算：

**硬件总分 = 平台基础分 + 芯片档位加成 + 内存加成 + 存储加成 + 独立 GPU 加成**

#### 平台基础分

| 情况 | 分数 |
|------|------|
| Apple Silicon Mac（chip_family = "apple_silicon"） | 300 |
| Intel Mac（chip_family = "x86_64"，platform = "macOS"） | 150 |
| Windows + 独立 GPU（gpu_discrete 非空） | 200 |
| Windows 无独显 | 80 |
| 其他/无法识别 | 50 |

#### 芯片档位加成

| 芯片档位（chip_tier） | 加分 |
|---------------------|------|
| "ultra"（M4 Ultra、M5 Ultra） | +600 |
| "max"（M4 Max、M5 Max） | +500 |
| "pro"（M4 Pro、M5 Pro、M3 Pro） | +350 |
| "base"（M1/M2/M3/M4 基础款） | +200 |
| "high"（Intel i9、AMD Ryzen 9） | +200 |
| "mid_high"（Intel i7、AMD Ryzen 7） | +150 |
| "mid"（Intel i5、AMD Ryzen 5） | +100 |
| "low"（Celeron、Pentium 等） | +20 |

#### 内存加成（字段 ram_gb）

| 内存容量 | 加分 |
|---------|------|
| ≥ 128 GB | +600 |
| 64 GB | +400 |
| 32 GB | +250 |
| 24 GB | +180 |
| 16 GB | +100 |
| 8 GB | +40 |
| < 8 GB | +0 |

#### 存储加成（字段 storage_gb）

| 存储容量 | 加分 |
|---------|------|
| ≥ 4096 GB（4 TB） | +200 |
| ≥ 2048 GB（2 TB） | +120 |
| ≥ 1024 GB（1 TB） | +70 |
| ≥ 512 GB | +30 |
| < 512 GB | +0 |

#### 独立 GPU 加成（字段 gpu_discrete、gpu_vram_gb）

| GPU 档位 | 代表型号（名称模糊匹配） | 加分 |
|---------|----------------------|------|
| RTX 4090/5090/A100/H100 | 名称含 "4090"/"5090"/"A100"/"H100" | +800 |
| RTX 4080/5080/RX 7900 XTX | 名称含 "4080"/"5080"/"7900" | +500 |
| RTX 4070/3090/RX 7800 | 名称含 "4070"/"3090"/"7800" | +300 |
| RTX 4060/3070/RX 6800 | 名称含 "4060"/"3070"/"6800" | +150 |
| 其他独立显卡 | gpu_discrete 非空但不匹配上述型号 | +50 |

**稀有成就（硬件）：**
- chip_tier = "max" 或 "ultra"（M4/M5 Max/Ultra）→ SSR 级：「这台机器的统一内存架构让它比同价位 x86 设备更适合本地 AI 推理，全球拥有者不足 0.5%。」
- ram_gb ≥ 128 → SSR 级：「128GB 内存意味着你可以在本地完整加载 70B 参数的大模型，这是绝大多数 AI 研究者都不具备的硬件条件。」
- gpu_vram_gb ≥ 24（RTX 4090 及以上）→ SSR 级：「24GB+ 显存是本地微调大模型的最低门槛，你的 GPU 配置已达到入门级 AI 训练工作站标准。」
- ram_gb ≥ 64 → SR 级：「64GB 内存让你可以在本地流畅运行 34B 级别的开源模型，超过 95% 的普通用户。」
- chip_tier = "pro"（M3/M4 Pro）→ SR 级：「Apple M Pro 系列的高带宽内存架构在 AI 推理场景下效率远超同级 x86 设备。」

### 维度：网络能力（network）

**网络总分 = 网速加成 + 可达性加成 + VPN 加成 + 延迟加成**

#### 网速加成（字段 download_mbps）

| 下行速度 | 加分 |
|---------|------|
| ≥ 500 Mbps | +300 |
| 200-500 Mbps | +200 |
| 50-200 Mbps | +100 |
| 10-50 Mbps | +40 |
| < 10 Mbps 或 null | +0 |

#### 国际 AI 服务可达性（字段 reachability）

| 条件 | 加分 |
|------|------|
| api.openai.com = "reachable" | +200 |
| api.anthropic.com = "reachable" | +200 |
| generativelanguage.googleapis.com = "reachable" | +150 |

#### VPN/代理工具（字段 vpn_tools）

| 条件 | 加分 |
|------|------|
| vpn_tools 非空（有任意 VPN 工具） | +250 |

#### 延迟加成（取 latency_openai_ms 和 latency_anthropic_ms 的平均值）

| 平均延迟 | 加分 |
|---------|------|
| < 100ms | +100 |
| 100-300ms | +50 |
| > 300ms 或 null | +0 |

**稀有成就（网络）：**
- vpn_tools 非空 + 至少 2 个 AI 服务可达 + download_mbps ≥ 500 → SSR 级：「同时具备 VPN 工具、国际 AI 服务直连能力和 500Mbps+ 网速，你的网络环境已为高强度 AI 工作做好准备。」

---

## 评分质量指南

1. **对未知工具保持合理推断**：如遇 raw_data 中未在本文档列出的工具，根据其名称、描述和发布者综合判断 `is_ai` 和乘数
2. **宁可多判断为 AI**：在模糊情况下，倾向于将专业工具判定为 AI 相关（因为非 AI 工具基础分也是 0，最差情况是 false positive 不计分）
3. **理由必须简洁**：`reason` 字段一句话说明判断依据
4. **背书文案要有感染力**：稀有成就的 `copy` 要让用户有成就感，强调稀有性和能力认可
