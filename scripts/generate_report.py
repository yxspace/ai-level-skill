#!/usr/bin/env python3
"""读取 score_result.json，生成单文件 Neon 风格 HTML 报告"""

import json
import html as html_lib
import random as _random
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
OUTPUT_DIR = Path.cwd() / 'output'

# ─── 每个维度的图标和中文名
DIMENSION_META = {
    'apps':               ('\U0001f5a5', '应用程序'),
    'cli_tools':          ('⚡', '终端工具'),
    'npm_globals':        ('\U0001f4e6', 'npm 全局包'),
    'claude_skills':      ('\U0001f916', 'Skills'),
    'model_configs':      ('\U0001f9e0', '模型配置'),
    'python_ai_packages': ('\U0001f40d', 'Python AI 包'),
    'ide_ai_plugins':     ('\U0001f50c', 'IDE AI 插件'),
    'ai_home_folders':    ('\U0001f4c1', 'AI 文件夹'),
    'hardware':           ('\U0001f4bb', '设备硬件'),
    'network':            ('\U0001f310', '网络能力'),
    'local_models':       ('\U0001f5c4', '本地模型'),
    'api_keys':           ('\U0001f511', 'API Key'),
    'browser_ai_plugins': ('\U0001f30d', '浏览器插件'),
    'docker_ai_images':   ('\U0001f433', 'Docker AI'),
    'jupyter':            ('\U0001f4d3', 'Jupyter'),
}

TOOL_DESCRIPTIONS = {
    # AI 原生 IDE / 编辑器
    'cursor':                   'AI 原生代码编辑器，深度集成 Claude / GPT-4，支持自然语言生成、重构与解释代码',
    'windsurf':                 'Codeium 出品的 AI 原生 IDE，内置 Cascade AI 助手，支持多步骤代码推理',
    'zed':                      '高性能代码编辑器，内置 AI 代码补全与 Copilot 集成，专注极速响应',
    'copilot':                  'GitHub 出品的 AI 代码补全工具，基于 OpenAI Codex，覆盖主流语言与 IDE',
    'github copilot':           'GitHub 出品的 AI 代码补全工具，基于 OpenAI Codex，覆盖主流语言与 IDE',
    # AI 对话 / 助手应用
    'claude':                   'Anthropic 出品的 AI 助手，擅长长文本理解、代码分析与复杂推理',
    'chatgpt':                  'OpenAI 出品的对话式 AI 助手，支持 GPT-4 等多种模型',
    'perplexity':               '以搜索为核心的 AI 问答工具，实时检索网页并给出引用式回答',
    'gemini':                   'Google DeepMind 出品的多模态 AI 助手，与 Google Workspace 深度整合',
    'copilot chat':             'Microsoft Copilot 对话界面，集成 GPT-4 与 Bing 搜索能力',
    'notionai':                 'Notion 内置 AI 写作与总结助手，可在笔记中直接生成、改写内容',
    # 本地大模型运行工具
    'ollama':                   '命令行本地大模型运行工具，支持一键拉取 Llama、Mistral 等主流模型',
    'lm studio':                '本地大模型图形化客户端，支持 GGUF 格式，提供 OpenAI 兼容 API',
    'jan':                      '开源本地 AI 应用，支持多种大模型离线运行，内置简洁聊天界面',
    'gpt4all':                  '跨平台本地 LLM 运行工具，支持多种量化模型，无需 GPU 即可运行',
    'llamafile':                '单文件分发的本地大模型，无需安装直接执行，Mozilla 出品',
    # AI 终端 / CLI 工具
    'claude code':              'Anthropic 官方 AI 编程 CLI，直接在终端驱动代码生成、调试与项目管理',
    'aider':                    'AI 结对编程 CLI 工具，与 git 深度集成，支持多文件代码修改与提交',
    'continue':                 'VSCode/JetBrains 开源 AI 插件，可接入任意 LLM，支持自定义 prompt',
    'cody':                     'Sourcegraph 出品的 AI 代码助手，擅长大型代码库理解与跨文件搜索',
    'tabnine':                  '基于本地模型的 AI 代码补全工具，保护代码隐私，支持离线运行',
    'codeium':                  '免费 AI 代码补全工具，覆盖 40+ 语言，支持本地与云端混合部署',
    'gpt-engineer':             '自然语言生成完整项目的 AI 工具，输入需求描述即可生成可运行代码',
    'openai':                   'OpenAI 官方 Python SDK，用于调用 GPT、DALL-E、Whisper 等 API',
    'anthropic':                'Anthropic 官方 Python SDK，用于调用 Claude 系列模型 API',
    'llm':                      'Simon Willison 出品的命令行 LLM 工具，支持多种模型与插件',
    'fabric':                   '开源 AI 增强 CLI 框架，提供丰富的 prompt 模板处理各类文本任务',
    'gorilla-cli':              '自然语言转 Shell 命令的 AI 工具，基于 Gorilla LLM',
    'sgpt':                     '终端 AI 助手，支持自然语言查询、Shell 命令生成与代码解释',
    'shell-gpt':                '终端 AI 助手，支持自然语言查询、Shell 命令生成与代码解释',
    'ai-shell':                 '自然语言转 Shell 命令的 AI 工具，由 Builder.io 出品',
    'gptcommit':                'AI 自动生成 git commit 信息的 CLI 工具',
    'gitbutler':                'AI 辅助的 git 客户端，支持多分支并行开发与智能合并',
    # Python AI 包
    'langchain':                '大型语言模型应用开发框架，提供链式调用、Agent、RAG 等核心组件',
    'langchain-core':           'LangChain 核心抽象层，定义 Runnable 接口与基础组件',
    'langchain-community':      'LangChain 社区集成包，包含大量第三方工具与模型适配器',
    'langchain-openai':         'LangChain 的 OpenAI 集成，封装 GPT 系列模型调用',
    'langchain-anthropic':      'LangChain 的 Anthropic 集成，封装 Claude 系列模型调用',
    'llama-index':              '专注检索增强生成（RAG）的框架，擅长构建知识库问答系统',
    'llama_index':              '专注检索增强生成（RAG）的框架，擅长构建知识库问答系统',
    'openai':                   'OpenAI 官方 Python SDK，提供 GPT、Embeddings、DALL-E 等 API 调用',
    'anthropic':                'Anthropic 官方 Python SDK，提供 Claude 系列模型的完整 API 接口',
    'transformers':             'Hugging Face 出品的预训练模型库，支持 BERT、GPT、T5 等数百种模型',
    'diffusers':                'Hugging Face 出品的扩散模型库，用于图像生成（Stable Diffusion 等）',
    'sentence-transformers':    '文本向量化（Embedding）库，用于语义搜索、相似度计算',
    'torch':                    'Meta 出品的深度学习框架 PyTorch，AI/ML 研究与生产的核心工具',
    'tensorflow':               'Google 出品的深度学习框架，支持大规模模型训练与部署',
    'keras':                    '高层神经网络 API，运行于 TensorFlow / JAX 之上，简化模型构建',
    'jax':                      'Google 出品的高性能数值计算库，支持自动微分与 XLA 加速',
    'scipy':                    '科学计算基础库，提供统计、优化、信号处理等 ML 常用算法',
    'scikit-learn':             '经典机器学习算法库，涵盖分类、回归、聚类、特征工程等',
    'sklearn':                  '经典机器学习算法库，涵盖分类、回归、聚类、特征工程等',
    'xgboost':                  '高效梯度提升树库，在表格数据竞赛和生产场景中广泛使用',
    'lightgbm':                 'Microsoft 出品的高速梯度提升框架，适合大规模特征训练',
    'catboost':                 'Yandex 出品的梯度提升库，对类别特征有原生支持',
    'numpy':                    'Python 数值计算基础库，提供高性能多维数组与矩阵运算',
    'pandas':                   '数据分析与处理库，提供 DataFrame 接口，AI 数据预处理核心工具',
    'matplotlib':               '经典数据可视化库，用于绘制训练曲线、特征分布等 ML 图表',
    'seaborn':                  '基于 matplotlib 的统计可视化库，快速绘制相关矩阵、分布图等',
    'plotly':                   '交互式可视化库，支持动态图表与仪表板，适合 AI 结果展示',
    'chromadb':                 '开源嵌入式向量数据库，用于 RAG 应用的语义搜索与存储',
    'faiss':                    'Meta 出品的向量相似度搜索库，支持亿级向量的高速检索',
    'pinecone-client':          'Pinecone 向量数据库 Python SDK，用于云端语义搜索服务',
    'weaviate-client':          'Weaviate 向量数据库 Python SDK，支持语义搜索与知识图谱',
    'qdrant-client':            'Qdrant 向量数据库客户端，高性能向量存储与检索服务',
    'tiktoken':                 'OpenAI 出品的 token 计算库，用于统计 GPT 模型的 token 用量',
    'tokenizers':               'Hugging Face 出品的快速分词库，支持 BPE、WordPiece 等算法',
    'accelerate':               'Hugging Face 出品的分布式训练库，简化多 GPU/TPU 模型训练',
    'peft':                     'Hugging Face 出品的参数高效微调库，支持 LoRA、Prefix-Tuning 等',
    'trl':                      'Hugging Face 出品的强化学习微调库，用于 RLHF 训练',
    'bitsandbytes':             'LLM 量化库，支持 INT8/INT4 量化以降低显存占用',
    'auto-gptq':                '基于 GPTQ 算法的 LLM 量化工具，大幅压缩模型体积',
    'autoawq':                  'AWQ 量化工具，4-bit 权重量化以提升 LLM 推理效率',
    'vllm':                     '高吞吐量 LLM 推理引擎，使用 PagedAttention 技术加速服务部署',
    'text-generation-inference':'Hugging Face 出品的高性能 LLM 推理服务框架',
    'guidance':                 '微软出品的 LLM 程序化控制框架，精确控制生成格式与结构',
    'outlines':                 '结构化 LLM 输出库，确保模型生成符合 JSON Schema 等格式',
    'instructor':               '基于 Pydantic 的结构化 LLM 输出库，支持自动重试与验证',
    'litellm':                  '统一 LLM API 调用代理，用一套接口调用 100+ 模型提供商',
    'dspy':                     'Stanford 出品的 LLM 程序化框架，用代码替代手工 prompt 工程',
    'haystack':                 'deepset 出品的 NLP/RAG 应用框架，适合生产级问答系统搭建',
    'spacy':                    '工业级 NLP 库，提供命名实体识别、依存分析等经典 NLP 流水线',
    'nltk':                     '自然语言处理教学与研究工具包，包含丰富语料库和基础算法',
    'gensim':                   '文本相似度与 Topic Model 库，支持 Word2Vec、LDA 等模型',
    'cohere':                   'Cohere 官方 SDK，提供文本生成、Embedding 与 Rerank API',
    'groq':                     'Groq 官方 SDK，调用 Groq 超高速推理平台的 LLama、Mixtral 等模型',
    'mistralai':                'Mistral AI 官方 SDK，调用 Mistral、Mixtral 等欧洲开源模型',
    'together':                 'Together AI SDK，用于调用开源模型的云端推理 API',
    'replicate':                'Replicate SDK，通过 API 调用开源模型，无需本地 GPU',
    'fireworks-ai':             'Fireworks AI SDK，提供高速开源模型推理 API 服务',
    'wandb':                    'Weights & Biases 实验跟踪平台，记录训练指标、可视化模型性能',
    'mlflow':                   'MLOps 平台，管理实验、模型版本与部署流程',
    'optuna':                   '自动超参数优化框架，使用 TPE 等算法高效搜索超参数空间',
    'ray':                      '分布式 AI 计算框架，用于大规模并行训练与强化学习',
    'opencv-python':            'OpenCV Python 接口，计算机视觉基础库，支持图像预处理与模型部署',
    'pillow':                   'Python 图像处理库，用于 AI 模型的图像预处理与后处理',
    'albumentations':           '高性能图像增强库，专为计算机视觉模型训练设计',
    'timm':                     'PyTorch 图像模型库，包含数百种预训练视觉 Transformer 和 CNN',
    'ultralytics':              'YOLO 系列目标检测模型官方库，支持训练、推理与部署',
    'gradio':                   '快速构建 AI 模型演示 Web 界面的库，一键生成可分享的 Demo',
    'streamlit':                '数据科学与 AI 应用快速开发框架，将 Python 脚本转为 Web 应用',
    'chainlit':                 '专为 LLM 应用设计的聊天界面框架，支持流式输出与对话历史',
    'modal':                    '云端无服务器 AI 计算平台 SDK，支持 GPU 推理任务快速部署',
    'celery':                   '分布式任务队列，常用于 AI 推理服务的异步任务调度',
    # npm AI 工具
    '@anthropic-ai/claude-code': 'Claude Code 官方 npm 包，提供 Claude AI 编程助手 CLI 功能',
    '@anthropic-ai/sdk':        'Anthropic 官方 Node.js SDK，用于在 JS/TS 项目中调用 Claude API',
    'openai':                   'OpenAI 官方 Node.js SDK，用于调用 GPT、DALL-E、Whisper 等 API',
    'langchain':                'LangChain JavaScript 版，在 Node.js 中构建 LLM 应用',
    '@langchain/core':          'LangChain JS 核心抽象层，提供 Runnable 接口与基础组件',
    '@langchain/anthropic':     'LangChain 的 Anthropic 集成（JS），封装 Claude 系列模型',
    '@langchain/openai':        'LangChain 的 OpenAI 集成（JS），封装 GPT 系列模型',
    'ai':                       'Vercel AI SDK，简化在 Next.js 中集成多种 LLM 的流式输出',
    '@ai-sdk/openai':           'Vercel AI SDK 的 OpenAI 适配器',
    '@ai-sdk/anthropic':        'Vercel AI SDK 的 Anthropic 适配器',
    'llamaindex':               'LlamaIndex JS 版，在 Node.js 环境中构建 RAG 知识库应用',
    'ollama':                   'Ollama 官方 JS SDK，在 Node.js 中调用本地 Ollama 模型',
    'transformers':             'Hugging Face Transformers JS 版，浏览器与 Node.js 端运行 ML 模型',
    '@huggingface/inference':   'Hugging Face 推理 API 的 JS SDK，调用 Hub 上的模型',
    'groq-sdk':                 'Groq 官方 Node.js SDK，调用 Groq 超高速推理 API',
    'cohere-ai':                'Cohere 官方 Node.js SDK，提供文本生成与 Embedding 能力',
    'mistral':                  'Mistral AI 官方 Node.js SDK',
    'replicate':                'Replicate Node.js SDK，通过 API 调用开源模型',
    'vectordb':                 'LanceDB 向量数据库的 Node.js 客户端',
    'chromadb':                 'Chroma 向量数据库的 Node.js 客户端，用于语义搜索',
    # Docker AI 镜像
    'ollama/ollama':            'Ollama 官方 Docker 镜像，容器化部署本地大模型服务',
    'ghcr.io/ollama/ollama':    'Ollama 官方 Docker 镜像（GitHub Container Registry）',
    'vllm/vllm-openai':         'vLLM 官方 Docker 镜像，提供 OpenAI 兼容的高性能推理服务',
    'localai/localai':          'LocalAI Docker 镜像，OpenAI 兼容的本地推理服务端',
    'huggingface/text-generation-inference': 'Hugging Face TGI 镜像，生产级 LLM 推理服务',
    'nvidia/cuda':              'NVIDIA CUDA 基础镜像，AI 模型 GPU 训练与推理的基础环境',
    'pytorch/pytorch':          'PyTorch 官方 Docker 镜像，预装 CUDA 的深度学习环境',
    'tensorflow/tensorflow':    'TensorFlow 官方 Docker 镜像，含 GPU 支持的训练环境',
    'jupyter/datascience-notebook': 'Jupyter 官方数据科学镜像，预装 Python/R/Julia 数据分析工具',
    # AI 文件夹 / 本地模型
    '.claude':                  'Claude Code 配置目录，存储 Skills、自定义指令与会话状态',
    '.ollama':                  'Ollama 本地模型存储目录，管理下载的 GGUF 格式模型文件',
    '.lmstudio':                'LM Studio 配置与模型存储目录',
    'huggingface':              'Hugging Face 模型缓存目录，存储从 Hub 下载的模型文件',
    '.cache/huggingface':       'Hugging Face 模型缓存目录，存储从 Hub 下载的模型文件',
    'models':                   '本地 AI 模型存储目录',
    # Claude Skills
    'ai-level-skill':           'AI 能力水平侧写 Skill，扫描设备 AI 工具并生成可视化报告',
}

ACHIEVEMENT_COLORS = {
    'SSR': {'border': '#ffd700', 'bg': 'rgba(255,215,0,0.08)', 'glow': '0 0 20px rgba(255,215,0,0.5)'},
    'SR':  {'border': '#bf5fff', 'bg': 'rgba(191,95,255,0.08)', 'glow': '0 0 20px rgba(191,95,255,0.5)'},
    'R':   {'border': '#00fff0', 'bg': 'rgba(0,255,240,0.08)', 'glow': '0 0 15px rgba(0,255,240,0.4)'},
}


def esc(s):
    return html_lib.escape(str(s)) if s else ''


def count_ai_tools(scores):
    """Count total AI tools across all dimensions."""
    total = 0
    for key, dim_data in scores.items():
        if not isinstance(dim_data, dict):
            continue
        items = dim_data.get('items', [])
        if key == 'api_keys':
            total += len(dim_data.get('detected', []))
        elif key == 'model_configs':
            total += len(dim_data.get('models', []))
        elif key in ('hardware', 'network', 'jupyter'):
            if dim_data.get('score', 0) > 0:
                total += 1
        else:
            for item in items:
                if isinstance(item, dict) and item.get('is_ai', True):
                    total += 1
                elif isinstance(item, str):
                    total += 1
    return total


def count_scored_dims(scores):
    """Count dimensions with score > 0."""
    count = 0
    for key, dim_data in scores.items():
        if isinstance(dim_data, dict) and dim_data.get('score', 0) > 0:
            count += 1
    return count


def build_top_dims_pills(scores, top_n=3):
    """Build HTML for top N dimension pills shown in hero."""
    dim_scores = []
    for key, (icon, label) in DIMENSION_META.items():
        s = scores.get(key, {})
        if isinstance(s, dict) and s.get('score', 0) > 0:
            dim_scores.append((key, icon, label, s.get('score', 0)))
    dim_scores.sort(key=lambda x: x[3], reverse=True)
    top = dim_scores[:top_n]
    pills = []
    for key, icon, label, score in top:
        pills.append(
            f'<div class="hero-dim-pill">'
            f'<span class="hero-dim-pill-icon">{icon}</span>'
            f'<span>{esc(label)}</span>'
            f'<span class="hero-dim-pill-score">{score:,} 分</span>'
            f'</div>'
        )
    return ''.join(pills)


def build_ach_chips(achievements):
    """Build compact achievement chips for hero preview."""
    if not achievements:
        return ''
    chips = []
    for ach in achievements[:4]:
        level = ach.get('level', 'R')
        title = esc(ach.get('title', ''))
        css_class = f'hero-ach-chip hero-ach-chip-{level.lower()}'
        chips.append(
            f'<span class="{css_class}">{level}</span>'
            f'<span class="hero-ach-chip-label">{title}</span>'
        )
    return ''.join(chips)


def build_dimension_cards(scores, hide_empty=True):
    parts = []
    dim_order = list(DIMENSION_META.keys())
    for key in dim_order:
        icon, label = DIMENSION_META.get(key, ('\U0001f4ca', key))
        dim_data = scores.get(key, {})
        score = dim_data.get('score', 0)
        items = dim_data.get('items', [])

        if hide_empty and score == 0:
            has_content = False
            if key == 'api_keys':
                has_content = bool(dim_data.get('detected', []))
            elif key == 'model_configs':
                has_content = bool(dim_data.get('models', []))
            elif key in ('hardware', 'network'):
                has_content = bool(dim_data.get('detail'))
            else:
                has_content = bool(items)
            if not has_content:
                continue

        items_html = ''
        for item in items[:15]:
            if isinstance(item, str):
                item = {'name': item}
            name = esc(item.get('name') or item.get('logical_name') or '')
            version = esc(item.get('version', ''))
            _tool_key = (item.get('name') or item.get('logical_name') or '').lower().strip()
            desc_text = (TOOL_DESCRIPTIONS.get(_tool_key)
                         or item.get('description')
                         or item.get('reason') or '')
            desc = esc(desc_text[:100])
            mult = item.get('multiplier', 1.0)
            fscore = item.get('final_score') or item.get('score') or item.get('bonus') or 0

            if mult >= 3.0:
                mult_color = '#ff6b35'
            elif mult >= 2.0:
                mult_color = '#00fff0'
            elif mult >= 1.5:
                mult_color = '#bf5fff'
            else:
                mult_color = '#888'

            score_html = (f'<span class="dim-item-score">+{fscore} 分</span>' if fscore else '')

            items_html += f'''
            <div class="dim-item">
              <span class="dim-item-name">{name}</span>
              {f'<span class="dim-item-version">v{version}</span>' if version else ''}
              <span class="dim-item-mult" style="color:{mult_color}">×{mult}</span>
              {score_html}
              {f'<div class="dim-item-desc">{desc}</div>' if desc else ''}
            </div>'''

        if key == 'api_keys':
            detected = dim_data.get('detected', [])
            items_html = ''
            for k in detected:
                items_html += f'<div class="dim-item"><span class="dim-item-name">{esc(k)}</span><span class="dim-item-mult" style="color:#00ff88">✓ 已配置</span></div>'
            if not detected:
                items_html = '<div class="dim-item dim-item-empty">未检测到 AI API Key</div>'

        if key == 'model_configs':
            models = dim_data.get('models', [])
            items_html = ''
            for m in models:
                model_name = esc(m.get('model', '') if isinstance(m, dict) else str(m))
                tool = esc(m.get('tool', '') if isinstance(m, dict) else '')
                items_html += f'<div class="dim-item"><span class="dim-item-name">{model_name}</span>{f"<span class=\"dim-item-version\">{tool}</span>" if tool else ""}</div>'
            if not models:
                items_html = '<div class="dim-item dim-item-empty">未检测到模型配置</div>'

        if key == 'hardware':
            detail = dim_data.get('detail', dim_data)
            hw_lines = [
                ('型号', detail.get('model', '-')),
                ('芯片', detail.get('chip', '-')),
                ('内存', f"{detail.get('ram_gb', '-')} GB"),
                ('存储', f"{detail.get('storage_gb', '-')} GB"),
            ]
            if detail.get('gpu_discrete'):
                hw_lines.append(('独显', detail.get('gpu_discrete', '')))
            items_html = ''.join(
                f'<div class="dim-item"><span class="dim-item-name">{esc(k)}</span><span class="dim-item-version">{esc(str(v))}</span></div>'
                for k, v in hw_lines
            )

        if key == 'network':
            detail = dim_data.get('detail', dim_data)
            net_lines = [
                ('网速', f"{detail.get('download_mbps', '-')} Mbps" if detail.get('download_mbps') else '测速失败'),
                ('OpenAI 延迟', f"{detail.get('latency_openai_ms', '-')} ms" if detail.get('latency_openai_ms') else '-'),
                ('VPN 工具', ', '.join(detail.get('vpn_tools', [])) or '未检测到'),
            ]
            items_html = ''.join(
                f'<div class="dim-item"><span class="dim-item-name">{esc(k)}</span><span class="dim-item-version">{esc(str(v))}</span></div>'
                for k, v in net_lines
            )

        if not items_html and key not in ('hardware', 'network', 'api_keys', 'model_configs'):
            items_html = '<div class="dim-item dim-item-empty">未检测到 AI 相关项目</div>'

        # Build count label for header
        if key in ('hardware', 'network', 'jupyter'):
            count_label = ''
        elif key == 'api_keys':
            n = len(dim_data.get('detected', []))
            count_label = f'<span class="dim-count">{n} 个</span>' if n else ''
        elif key == 'model_configs':
            n = len(dim_data.get('models', []))
            count_label = f'<span class="dim-count">{n} 个</span>' if n else ''
        else:
            n = len(items)
            count_label = f'<span class="dim-count">{n} 个</span>' if n else ''

        parts.append(f'''
        <div class="dim-card fade-in">
          <div class="dim-card-header">
            <span class="dim-icon">{icon}</span>
            <span class="dim-label">{label}</span>
            <span class="dim-header-right">{count_label}<span class="dim-score">{score:,} 分</span></span>
          </div>
          <div class="dim-card-body">
            {items_html}
          </div>
        </div>''')

    return '\n'.join(parts)


def build_achievements_html(achievements):
    if not achievements:
        return ''
    cards = []
    for ach in achievements:
        level = ach.get('level', 'R')
        title = esc(ach.get('title', ''))
        tool = esc(ach.get('tool', ''))
        copy = esc(ach.get('copy', ''))
        enhance = ACHIEVEMENT_ENHANCEMENTS.get(level, '成就达成！')
        colors = ACHIEVEMENT_COLORS.get(level, ACHIEVEMENT_COLORS['R'])
        cards.append(f'''
        <div class="ach-card" style="border-color:{colors["border"]};background:{colors["bg"]};box-shadow:{colors["glow"]};">
          <div class="ach-badge ach-badge-{level.lower()}">{level}</div>
          <div class="ach-content">
            <div class="ach-enhance">{enhance}</div>
            <div class="ach-title">{title}</div>
            <div class="ach-tool">{tool}</div>
            <div class="ach-copy">"{copy}"</div>
          </div>
        </div>''')
    return '\n'.join(cards)


def build_roadmap_html(roadmap):
    phases = roadmap.get('phases', [])
    if not phases:
        return ''
    items = []
    for phase in phases:
        title = esc(phase.get('title', ''))
        actions = phase.get('actions', [])
        actions_html = ''.join(f'<li>{esc(a)}</li>' for a in actions)
        items.append(f'''
        <div class="roadmap-phase fade-in">
          <div class="roadmap-phase-title">{title}</div>
          <ul class="roadmap-actions">{actions_html}</ul>
        </div>''')
    return '\n'.join(items)


def build_radar_data(scores):
    dim_order = list(DIMENSION_META.keys())
    labels = [DIMENSION_META[k][1] for k in dim_order]
    values = []
    max_score = 1
    for k in dim_order:
        s = scores.get(k, {}).get('score', 0)
        values.append(s)
        if s > max_score:
            max_score = s
    normalized = [round(v / max_score * 100, 1) for v in values]
    return json.dumps(labels), json.dumps(normalized), json.dumps(values)


OVERALL_EVAL = {
    'AI 极客': '你在 AI 领域的投入和探索已远超绝大多数人。从工具链到基础设施，从云端到本地，你构建了一个完整的 AI 能力体系。这不是简单的工具堆砌，而是对 AI 可能性的深度实践。',
    'AI 超级用户': '你的 AI 工具链已经相当完备，从编程到创作，从本地到云端，你正在用 AI 重新定义自己的工作方式。继续深入，极客就在前方。',
    'AI 工程师': '你已经超越了“用 AI”的阶段，正在进入“用 AI 创造”的领域。你的工具选择显示出对效率和专业性的追求。',
    'AI 进阶玩家': '你不再是 AI 的新手，已经开始建立自己的 AI 工作流。你选择的方向很对，持续深入会有质变。',
    'AI 实践者': '你正在从“了解 AI”走向“使用 AI”，已经有了不错的起步。每一次新工具的尝试都在扩展你的能力边界。',
    'AI 尝鲜者': '你已经开始探索 AI 的世界了，这是最宝贵的第一步。保持好奇心，你会发现更多可能。',
    'AI 初探者': '欢迎来到 AI 的世界！每一个高手都是从这里开始的，你的探索之旅才刚刚开始。',
}


def get_overall_eval(title, total_score):
    if title in OVERALL_EVAL:
        return OVERALL_EVAL[title]
    if total_score >= 10000:
        return OVERALL_EVAL['AI 极客']
    elif total_score >= 6000:
        return OVERALL_EVAL['AI 超级用户']
    elif total_score >= 3000:
        return OVERALL_EVAL['AI 工程师']
    elif total_score >= 1500:
        return OVERALL_EVAL['AI 进阶玩家']
    elif total_score >= 800:
        return OVERALL_EVAL['AI 实践者']
    elif total_score >= 300:
        return OVERALL_EVAL['AI 尝鲜者']
    else:
        return OVERALL_EVAL['AI 初探者']


HIGHLIGHT_PREFIXES = [
    '出色的', '令人印象深刻的', '亮眼的', '实力强劲的', '卓越的',
    '超群的', '非凡的', '令人瞩目的', '惊艳的', '出众的',
]

ACHIEVEMENT_ENHANCEMENTS = {
    'SSR': '传说级成就！',
    'SR': '史诗级成就！',
    'R': '稀有成就达成！',
}


def generate(score_result, detail=False, share_card_url=''):
    user_name = score_result.get('user_name', '')
    total_score = score_result.get('total_score', 0)
    title = score_result.get('title', 'AI 初探者')
    scores = score_result.get('dimension_scores', {})
    achievements = score_result.get('rare_achievements', [])
    highlights = score_result.get('highlights', [])
    weaknesses = score_result.get('weaknesses', [])
    roadmap = score_result.get('roadmap', {})
    scan_time = score_result.get('scan_time', '')

    report_title = f'{esc(user_name)} 的 AI 能力侧写报告' if user_name else '我的 AI 能力侧写报告'
    dim_cards_html = build_dimension_cards(scores)
    achievements_html = build_achievements_html(achievements)
    roadmap_html = build_roadmap_html(roadmap)

    # Hero quick stats
    ai_tool_count = count_ai_tools(scores)
    scored_dim_count = count_scored_dims(scores)
    ach_count = len(achievements)
    top_dims_html = build_top_dims_pills(scores)
    ach_chips_html = build_ach_chips(achievements)

    _rng = _random.Random(42)
    highlights_html = ''
    for h in highlights:
        prefix = _rng.choice(HIGHLIGHT_PREFIXES)
        highlights_html += f'<li class="highlight-item"><span class="hl-icon">✦</span>{prefix}{esc(h)}</li>'

    filtered_weaknesses = []
    for w in weaknesses:
        skip = False
        for k, (icon, label) in DIMENSION_META.items():
            dim_score = scores.get(k, {}).get('score', 0)
            if dim_score == 0 and label in w:
                skip = True
                break
        if not skip:
            filtered_weaknesses.append(w)
    weaknesses_html = ''.join(
        f'<li class="weakness-item"><span class="wk-icon">◈</span>{esc(w)}</li>'
        for w in filtered_weaknesses
    )

    if not filtered_weaknesses and weaknesses:
        weaknesses_html = '<li class="weakness-item" style="color:var(--green)"><span class="hl-icon">✦</span>你当前覆盖的维度均表现出色，继续保持！</li>'

    overall_eval = get_overall_eval(title, total_score)

    current_level = esc(roadmap.get('current_level', title))
    next_level = esc(roadmap.get('next_level', ''))

    radar_labels, radar_normalized, radar_values = build_radar_data(scores)

    score_table_rows = ''
    for key in DIMENSION_META:
        icon, label = DIMENSION_META[key]
        dim_data = scores.get(key, {})
        score = dim_data.get('score', 0)
        items = dim_data.get('items', [])
        if key == 'api_keys':
            ai_count = len(dim_data.get('detected', []))
        elif key == 'model_configs':
            ai_count = len(dim_data.get('models', []))
        elif key in ('hardware', 'network', 'jupyter'):
            ai_count = 1 if score > 0 else 0
        else:
            ai_count = len([i for i in items if (i.get('is_ai', True) if isinstance(i, dict) else True)])
        score_table_rows += f'''
        <tr>
          <td>{icon} {esc(label)}</td>
          <td class="td-count">{ai_count}</td>
          <td class="td-score">{score:,}</td>
        </tr>'''

    detail_badge = '''
    <div class="detail-badge">
      <span class="detail-badge-icon">\U0001f512</span>
      <span>详细报告 · 仅供本地查阅，请勿公开分享</span>
    </div>''' if detail else ''

    detail_score_table = f'''
    <section class="section">
      <h2 class="section-title">各维度得分汇总</h2>
      <div class="score-table-wrap">
        <table class="score-table">
          <thead><tr><th>维度</th><th>AI 工具数</th><th>得分</th></tr></thead>
          <tbody>{score_table_rows}</tbody>
          <tfoot><tr><td><strong>合计</strong></td><td></td><td class="td-score"><strong>{total_score:,}</strong></td></tr></tfoot>
        </table>
      </div>
    </section>''' if detail else ''

    dim_cards_section = f'''
    <section class="section">
      <h2 class="section-title">各维度工具明细</h2>
      <div class="dim-grid">{dim_cards_html}</div>
    </section>''' if detail else ''

    local_detail_hint = '' if detail else '''
    <div class="local-hint">
      <span class="local-hint-icon">\U0001f4cb</span>
      本地查看完整工具明细与单项得分：打开 <code>report_detail.html</code>
    </div>'''

    detail_footer_note = '''
    <div class="detail-footer-note">
      <span>← </span><a class="footer-link" href="report.html">返回基础报告</a>
    </div>''' if detail else ''

    ach_section = ''
    if achievements_html:
        ach_section = f'''
    <section class="section">
      <h2 class="section-title">稀有成就</h2>
      <div class="ach-grid">{achievements_html}</div>
    </section>'''

    # Ach chips row in hero
    ach_chips_section = ''
    if ach_chips_html:
        ach_chips_section = f'<div class="hero-ach-preview">{ach_chips_html}</div>'

    # Top dims row in hero
    top_dims_section = ''
    if top_dims_html:
        top_dims_section = f'<div class="hero-top-dims">{top_dims_html}</div>'

    report_title_text = esc(report_title)
    page_title_prefix = '[详细] ' if detail else ''

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{page_title_prefix}{report_title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;600&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --bg:#0a0a0f;--card:#0f0f1a;--border:rgba(0,255,240,0.15);
  --cyan:#00fff0;--purple:#bf5fff;--orange:#ff6b35;--green:#00ff88;
  --text:#e0e0e0;--muted:#888;
  --font-title:'Orbitron',sans-serif;
  --font-body:'Inter','PingFang SC',sans-serif;
  --font-mono:'JetBrains Mono','SF Mono',monospace;
  --safe-bottom:env(safe-area-inset-bottom, 0px);
  --safe-top:env(safe-area-inset-top, 0px);
  --safe-left:env(safe-area-inset-left, 0px);
  --safe-right:env(safe-area-inset-right, 0px);
}}
html{{scroll-behavior:smooth;-webkit-text-size-adjust:100%}}
body{{
  background:var(--bg);color:var(--text);font-family:var(--font-body);overflow-x:hidden;
  padding-top:var(--safe-top);padding-left:var(--safe-left);padding-right:var(--safe-right);
}}

/* ── Scrollbar ── */
::-webkit-scrollbar{{width:6px}}
::-webkit-scrollbar-track{{background:var(--bg)}}
::-webkit-scrollbar-thumb{{background:var(--border);border-radius:3px}}

/* ── Hero ── */
.hero{{
  position:relative;min-height:auto;display:flex;flex-direction:column;
  align-items:center;justify-content:flex-start;text-align:center;
  padding:2.5rem 1.5rem 1.5rem;overflow:hidden;
  padding-top:max(2.5rem, var(--safe-top));
}}
#particles{{position:absolute;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none}}
.hero-content{{position:relative;z-index:1;max-width:800px;width:100%}}
.hero-subtitle{{
  font-family:var(--font-body);font-size:clamp(0.7rem,1.6vw,0.82rem);
  color:var(--muted);margin-bottom:0.4rem;letter-spacing:0.1em;
}}
.hero-name{{
  font-family:var(--font-title);font-size:clamp(0.85rem,3vw,1.4rem);
  color:var(--text);margin-bottom:0.5rem;
}}
.hero-score-row{{
  display:flex;align-items:baseline;justify-content:center;gap:0.8rem;
  margin-bottom:0.2rem;
}}
.hero-score{{
  font-family:var(--font-title);font-size:clamp(2.8rem,10vw,5.5rem);
  font-weight:900;
  background:linear-gradient(135deg,var(--cyan),var(--purple));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  background-clip:text;line-height:1;
}}
.hero-title{{
  font-family:var(--font-title);font-size:clamp(0.75rem,2vw,1.1rem);
  color:var(--cyan);text-shadow:0 0 20px var(--cyan);
  letter-spacing:0.15em;white-space:nowrap;
}}
.hero-overall-eval{{
  max-width:640px;margin:0.6rem auto 0;
  font-size:clamp(0.78rem,1.4vw,0.9rem);line-height:1.55;
  color:var(--text);opacity:0.85;text-align:center;
}}

/* ── Quick Stats Row ── */
.hero-stats{{
  display:flex;justify-content:center;gap:0.6rem;
  margin:0.8rem auto 0;flex-wrap:wrap;max-width:640px;
}}
.hero-stat{{
  background:rgba(0,255,240,0.06);border:1px solid var(--border);
  border-radius:8px;padding:0.4rem 0.8rem;
  display:flex;align-items:center;gap:0.4rem;
  font-size:0.78rem;
}}
.hero-stat-icon{{font-size:0.85rem}}
.hero-stat-val{{font-family:var(--font-mono);font-weight:600;color:var(--cyan)}}
.hero-stat-label{{color:var(--muted);font-size:0.72rem}}

/* ── Top Dims Preview ── */
.hero-top-dims{{
  display:flex;justify-content:center;gap:0.5rem;
  margin:0.6rem auto 0;flex-wrap:wrap;max-width:640px;
}}
.hero-dim-pill{{
  background:var(--card);border:1px solid var(--border);border-radius:20px;
  padding:0.25rem 0.7rem;font-size:0.72rem;
  display:flex;align-items:center;gap:0.3rem;
}}
.hero-dim-pill-icon{{font-size:0.75rem}}
.hero-dim-pill-score{{font-family:var(--font-mono);color:var(--cyan);font-weight:600}}

/* ── Ach Preview in Hero ── */
.hero-ach-preview{{
  display:flex;justify-content:center;gap:0.4rem;align-items:center;
  margin:0.5rem auto 0;flex-wrap:wrap;max-width:640px;
}}
.hero-ach-chip{{
  border-radius:4px;padding:0.15rem 0.5rem;font-size:0.68rem;
  font-family:var(--font-title);font-weight:700;letter-spacing:0.05em;
}}
.hero-ach-chip-ssr{{background:#ffd700;color:#000}}
.hero-ach-chip-sr{{background:#bf5fff;color:#fff}}
.hero-ach-chip-r{{background:#00fff0;color:#000}}
.hero-ach-chip-label{{font-family:var(--font-body);font-weight:400;font-size:0.68rem;color:var(--text);opacity:0.8}}

.hero-arrow{{
  margin-top:1rem;color:var(--muted);font-size:1.1rem;
  animation:bounce 2s infinite;z-index:1;
}}
@keyframes bounce{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(6px)}}}}

/* ── Sections ── */
.section{{max-width:1400px;margin:0 auto;padding:2rem 1.5rem}}
.section-title{{
  font-family:var(--font-title);font-size:clamp(0.85rem,2.5vw,1.2rem);
  color:var(--cyan);letter-spacing:0.1em;
  border-bottom:1px solid var(--border);padding-bottom:0.6rem;margin-bottom:1.2rem;
}}

/* ── Radar + Bars ── */
.radar-wrapper{{
  display:grid;grid-template-columns:auto 1fr;gap:1.5rem;align-items:start;
}}
.radar-box{{display:flex;justify-content:center}}
canvas#radar{{max-width:340px;width:100%;height:auto}}
.dim-bars{{display:flex;flex-direction:column;gap:0.45rem}}
.dim-bar-row{{display:flex;align-items:center;gap:0.6rem;font-size:0.78rem}}
.dim-bar-label{{width:80px;color:var(--muted);flex-shrink:0;font-family:var(--font-body)}}
.dim-bar-track{{flex:1;height:5px;background:#1a1a2e;border-radius:3px;overflow:hidden}}
.dim-bar-fill{{height:100%;border-radius:3px;transition:width 1.5s ease;background:linear-gradient(90deg,var(--cyan),var(--purple))}}
.dim-bar-score{{width:55px;text-align:right;font-family:var(--font-mono);font-size:0.72rem;color:var(--cyan);flex-shrink:0}}

/* ── Achievement Cards ── */
.ach-grid{{display:flex;flex-wrap:wrap;gap:0.8rem;justify-content:center}}
.ach-card{{
  flex:1;min-width:240px;max-width:420px;
  border:1px solid;border-radius:10px;padding:0.9rem;
  display:flex;align-items:flex-start;gap:0.8rem;
  transition:transform 0.2s;
}}
.ach-card:hover{{transform:translateY(-3px)}}
.ach-badge{{
  font-family:var(--font-title);font-size:0.7rem;font-weight:700;
  padding:0.2rem 0.5rem;border-radius:5px;flex-shrink:0;letter-spacing:0.1em;
}}
.ach-badge-ssr{{background:#ffd700;color:#000}}
.ach-badge-sr{{background:#bf5fff;color:#fff}}
.ach-badge-r{{background:#00fff0;color:#000}}
.ach-enhance{{
  font-size:0.72rem;font-weight:700;margin-bottom:0.15rem;
  letter-spacing:0.05em;
}}
.ach-card[style*="ffd700"] .ach-enhance{{color:#ffd700}}
.ach-card[style*="bf5fff"] .ach-enhance{{color:#bf5fff}}
.ach-card[style*="00fff0"] .ach-enhance{{color:#00fff0}}
.ach-title{{font-weight:600;margin-bottom:0.15rem;font-size:0.88rem}}
.ach-tool{{font-family:var(--font-mono);font-size:0.75rem;color:var(--muted);margin-bottom:0.35rem}}
.ach-copy{{font-size:0.82rem;color:var(--text);opacity:0.85;line-height:1.5;font-style:italic}}

/* ── Dimension Cards Grid ── */
.dim-grid{{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(280px,1fr));
  gap:0.8rem;
}}
.dim-card{{
  background:var(--card);border:1px solid var(--border);
  border-radius:10px;overflow:hidden;
  transition:border-color 0.2s,transform 0.2s;
}}
.dim-card:hover{{border-color:rgba(0,255,240,0.4);transform:translateY(-2px)}}
.dim-card-header{{
  display:flex;align-items:center;gap:0.5rem;
  padding:0.6rem 0.8rem;background:rgba(0,255,240,0.04);
  border-bottom:1px solid var(--border);
}}
.dim-icon{{font-size:1rem}}
.dim-label{{flex:1;font-weight:600;font-size:0.82rem}}
.dim-header-right{{display:flex;align-items:center;gap:0.4rem}}
.dim-count{{
  font-family:var(--font-mono);font-size:0.72rem;
  color:var(--muted);background:rgba(255,255,255,0.06);
  padding:0.1rem 0.35rem;border-radius:4px;
}}
.dim-score{{
  font-family:var(--font-mono);font-size:0.82rem;
  color:var(--cyan);font-weight:600;
}}
.dim-card-body{{padding:0.6rem 0.8rem;max-height:200px;overflow-y:auto}}
.dim-item{{
  display:flex;align-items:baseline;flex-wrap:wrap;gap:0.3rem;
  padding:0.25rem 0;border-bottom:1px solid rgba(255,255,255,0.04);font-size:0.78rem;
}}
.dim-item:last-child{{border-bottom:none}}
.dim-item-name{{font-weight:500;color:var(--text)}}
.dim-item-version{{font-family:var(--font-mono);font-size:0.72rem;color:var(--muted)}}
.dim-item-mult{{font-family:var(--font-mono);font-size:0.72rem;font-weight:600;margin-left:auto}}
.dim-item-score{{font-family:var(--font-mono);font-size:0.72rem;color:var(--green)}}
.dim-item-desc{{width:100%;color:var(--muted);font-size:0.75rem;line-height:1.4}}
.dim-item-empty{{color:var(--muted);font-style:italic}}

/* ── Highlights ── */
.hw-card{{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:1rem}}
.hw-card-title{{font-family:var(--font-title);font-size:0.82rem;letter-spacing:0.1em;margin-bottom:0.7rem}}
.hw-card.highlights .hw-card-title{{color:var(--green)}}
.hw-card ul{{list-style:none;display:flex;flex-direction:column;gap:0.5rem}}
.highlight-item{{display:flex;align-items:flex-start;gap:0.5rem;font-size:0.82rem;line-height:1.45}}
.hl-icon{{color:var(--green);font-size:0.75rem;flex-shrink:0;margin-top:0.1rem}}

/* ── Roadmap ── */
.roadmap-progress{{
  display:flex;align-items:center;gap:0.8rem;margin-bottom:1.2rem;
  font-family:var(--font-title);font-size:0.8rem;
  flex-wrap:wrap;
}}
.rp-current{{color:var(--cyan)}}
.rp-arrow{{color:var(--muted)}}
.rp-next{{color:var(--purple)}}
.roadmap-phases{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:0.8rem}}
.roadmap-phase{{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:0.9rem}}
.roadmap-phase-title{{
  font-family:var(--font-title);font-size:0.72rem;color:var(--cyan);
  letter-spacing:0.1em;margin-bottom:0.6rem;
}}
.roadmap-actions{{list-style:none;display:flex;flex-direction:column;gap:0.4rem}}
.roadmap-actions li{{
  font-size:0.8rem;line-height:1.45;padding-left:0.8rem;position:relative;
  color:var(--text);opacity:0.9;
}}
.roadmap-actions li::before{{content:"›";position:absolute;left:0;color:var(--purple)}}

/* ── Footer / Share ── */
.footer{{
  max-width:1400px;margin:0 auto;padding:1.5rem 1.5rem calc(3rem + var(--safe-bottom));
  border-top:1px solid var(--border);
  display:flex;flex-wrap:wrap;gap:1.5rem;align-items:flex-start;justify-content:space-between;
}}
.footer-stats{{font-size:0.82rem;color:var(--muted);line-height:2}}
.footer-disclaimer{{font-size:0.75rem;color:var(--muted);opacity:0.6;max-width:400px;line-height:1.6}}
#share-section{{text-align:center;display:none;flex-direction:column;align-items:center}}
#share-section h3{{font-family:var(--font-title);font-size:0.9rem;color:var(--cyan);margin-bottom:1rem;letter-spacing:0.1em}}
#qr-code{{display:inline-block;padding:0.5rem;background:#fff;border-radius:8px;margin-bottom:0.8rem}}
#share-url{{
  background:var(--card);border:1px solid var(--border);color:var(--cyan);
  padding:0.4rem 0.8rem;border-radius:6px;width:280px;
  font-family:var(--font-mono);font-size:0.8rem;margin-right:0.5rem;
}}
.btn-copy{{
  background:transparent;border:1px solid var(--cyan);color:var(--cyan);
  padding:0.4rem 0.8rem;border-radius:6px;cursor:pointer;font-size:0.82rem;
  transition:background 0.2s;min-height:44px;
}}
.btn-copy:hover{{background:rgba(0,255,240,0.1)}}

/* ── Animations ── */
.fade-in{{opacity:0;transform:translateY(20px);transition:opacity 0.6s,transform 0.6s}}
.fade-in.visible{{opacity:1;transform:translateY(0)}}

/* ── Mobile: Tablet (768px) ── */
@media(max-width:768px){{
  .radar-wrapper{{grid-template-columns:1fr}}
  .hw-grid{{grid-template-columns:1fr}}
  .hero-stats{{gap:0.4rem}}
  .hero-stat{{padding:0.35rem 0.6rem;font-size:0.72rem}}
  .hero-dim-pill{{font-size:0.68rem;padding:0.2rem 0.6rem}}
  .hero-ach-preview{{gap:0.3rem}}
  .hero-ach-chip{{font-size:0.64rem;padding:0.12rem 0.4rem}}
  .hero-ach-chip-label{{font-size:0.64rem}}
}}

/* ── Mobile: Phone (480px) ── */
@media(max-width:480px){{
  .hero{{
    padding:1.8rem 1rem 1rem;
    padding-top:max(1.8rem, var(--safe-top));
  }}
  .section{{padding:1.2rem 0.8rem}}
  .hero-score-row{{
    flex-direction:column;gap:0.2rem;
  }}
  .hero-score{{
    font-size:clamp(3rem,16vw,4.5rem);
  }}
  .hero-title{{
    font-size:clamp(0.85rem,3.5vw,1rem);
  }}
  .hero-overall-eval{{
    font-size:clamp(0.85rem,3.5vw,0.95rem);
    line-height:1.6;
  }}
  .hero-stats{{
    gap:0.35rem;
    margin:0.6rem auto 0;
  }}
  .hero-stat{{
    padding:0.4rem 0.65rem;
    font-size:0.82rem;
    border-radius:10px;
    min-height:44px;
    justify-content:center;
  }}
  .hero-stat-val{{font-size:0.88rem}}
  .hero-stat-label{{font-size:0.72rem}}
  .hero-top-dims{{
    gap:0.4rem;
    margin:0.5rem auto 0;
    overflow-x:auto;
    -webkit-overflow-scrolling:touch;
    flex-wrap:nowrap;
    justify-content:flex-start;
    padding:0 0.5rem;
    scrollbar-width:none;
  }}
  .hero-top-dims::-webkit-scrollbar{{display:none}}
  .hero-dim-pill{{
    flex-shrink:0;
    font-size:0.76rem;
    padding:0.3rem 0.7rem;
    border-radius:20px;
  }}
  .hero-ach-preview{{
    gap:0.25rem;
    margin:0.4rem auto 0;
  }}
  .hero-ach-chip{{font-size:0.62rem;padding:0.12rem 0.4rem}}
  .hero-ach-chip-label{{font-size:0.62rem}}
  .hero-name{{
    font-size:clamp(0.9rem,3.5vw,1.1rem);
  }}
  .hero-subtitle{{
    font-size:0.75rem;
  }}

  /* Section titles larger on mobile for readability */
  .section-title{{
    font-size:clamp(0.9rem,3.5vw,1rem);
    padding-bottom:0.5rem;
    margin-bottom:0.8rem;
  }}

  /* Radar: smaller but still readable */
  canvas#radar{{max-width:280px}}

  /* Dim bars: bigger labels, taller bars for touch */
  .dim-bar-row{{
    font-size:0.85rem;
    gap:0.5rem;
    padding:0.3rem 0;
  }}
  .dim-bar-label{{
    width:70px;
    font-size:0.8rem;
    overflow:hidden;
    text-overflow:ellipsis;
    white-space:nowrap;
  }}
  .dim-bar-track{{
    height:8px;
    border-radius:4px;
  }}
  .dim-bar-score{{
    font-size:0.8rem;
    width:50px;
  }}

  /* Achievement cards: stack vertically, stretch full width */
  .ach-grid{{
    flex-direction:column;
    gap:0.6rem;
    align-items:stretch;
  }}
  .ach-card{{
    max-width:100%;
    width:100%;
    min-width:0;
    padding:0.8rem;
    gap:0.6rem;
    border-radius:12px;
  }}
  .ach-title{{font-size:0.92rem}}
  .ach-copy{{font-size:0.85rem}}
  .ach-badge{{
    font-size:0.68rem;
    padding:0.25rem 0.55rem;
  }}

  /* Dimension cards: single column, more touch-friendly */
  .dim-grid{{
    grid-template-columns:1fr;
    gap:0.6rem;
  }}
  .dim-card{{
    border-radius:12px;
  }}
  .dim-card-header{{
    padding:0.7rem 0.9rem;
    min-height:44px;
  }}
  .dim-label{{font-size:0.9rem}}
  .dim-score{{font-size:0.9rem}}
  .dim-count{{font-size:0.78rem}}
  .dim-card-body{{padding:0.6rem 0.9rem}}
  .dim-item{{
    padding:0.35rem 0;
    font-size:0.85rem;
    min-height:32px;
    align-items:center;
  }}
  .dim-item-name{{font-size:0.88rem}}
  .dim-item-version{{font-size:0.78rem}}
  .dim-item-mult{{font-size:0.78rem}}
  .dim-item-score{{font-size:0.78rem}}

  /* HW cards: stack, bigger text */
  .hw-card{{
    padding:0.8rem;
    border-radius:12px;
  }}
  .hw-card-title{{
    font-size:0.9rem;
    margin-bottom:0.5rem;
  }}
  .highlight-item,.weakness-item{{
    font-size:0.88rem;
    line-height:1.5;
    gap:0.4rem;
  }}

  /* Roadmap: single column */
  .roadmap-phases{{
    grid-template-columns:1fr;
    gap:0.6rem;
  }}
  .roadmap-phase{{
    padding:0.8rem;
    border-radius:12px;
  }}
  .roadmap-phase-title{{
    font-size:0.78rem;
  }}
  .roadmap-actions li{{
    font-size:0.85rem;
    line-height:1.5;
    padding:0.25rem 0 0.25rem 0.8rem;
  }}
  .roadmap-progress{{
    font-size:0.85rem;
    gap:0.5rem;
  }}

  /* Footer: stack, safe area, centered */
  .footer{{
    padding:1rem 0.8rem calc(2rem + var(--safe-bottom));
    flex-direction:column;
    align-items:stretch;
    text-align:center;
  }}
  .footer-stats{{font-size:0.85rem}}
  .footer-disclaimer{{font-size:0.82rem;max-width:100%;text-align:center}}

  /* Local hint: bigger touch target */
  .local-hint{{
    padding:0 0.8rem 1.5rem;
    font-size:0.88rem;
  }}
  .local-hint code{{
    font-size:0.85rem;
    padding:0.15rem 0.5rem;
  }}

  /* Share section: bigger QR */
  #share-section h3{{font-size:1rem}}
  #share-url{{
    width:100%;
    max-width:300px;
    font-size:0.85rem;
    padding:0.5rem 0.8rem;
    margin:0 0 0.5rem 0;
  }}
  .btn-copy{{
    min-height:44px;
    min-width:44px;
    font-size:0.88rem;
    padding:0.5rem 1rem;
  }}
}}

/* ── Detail Report Extras ── */
.detail-badge{{
  position:fixed;top:0;left:0;right:0;z-index:100;
  background:rgba(255,107,53,0.15);border-bottom:1px solid rgba(255,107,53,0.3);
  padding:0.5rem 1.5rem;font-size:0.8rem;color:#ff6b35;
  display:flex;align-items:center;gap:0.5rem;
  padding-top:max(0.5rem, var(--safe-top));
}}
.detail-badge-icon{{font-size:1rem}}
.score-table-wrap{{overflow-x:auto;-webkit-overflow-scrolling:touch}}
.score-table{{
  width:100%;border-collapse:collapse;
  font-size:0.82rem;
}}
.score-table th{{
  text-align:left;padding:0.45rem 0.8rem;
  border-bottom:2px solid var(--border);
  font-family:var(--font-title);font-size:0.7rem;
  color:var(--cyan);letter-spacing:0.08em;
}}
.score-table td{{padding:0.4rem 0.8rem;border-bottom:1px solid rgba(255,255,255,0.04)}}
.score-table tfoot td{{
  border-top:2px solid var(--border);border-bottom:none;
  padding-top:0.8rem;
}}
.td-count{{color:var(--muted);text-align:center}}
.td-score{{font-family:var(--font-mono);color:var(--cyan);text-align:right}}
.score-table tr:hover td{{background:rgba(0,255,240,0.03)}}
.local-hint{{
  max-width:1400px;margin:0 auto 0;padding:0 1.5rem 2rem;
  display:flex;align-items:center;gap:0.6rem;
  font-size:0.82rem;color:var(--muted);
}}
.local-hint-icon{{font-size:1rem}}
.local-hint code{{
  font-family:var(--font-mono);color:var(--cyan);
  background:rgba(0,255,240,0.07);padding:0.1rem 0.4rem;border-radius:4px;
}}
.detail-footer-note{{margin-bottom:0.5rem;font-size:0.82rem}}
.footer-link{{color:var(--cyan);text-decoration:none}}
.footer-link:hover{{text-decoration:underline}}
</style>
</head>
<body>

<!-- ── Detail Badge (detail report only) ── -->
{detail_badge}

<!-- ── Hero ── -->
<section class="hero">
  <canvas id="particles"></canvas>
  <div class="hero-content">
    <div class="hero-subtitle">AI 能力侧写报告 · {scan_time}</div>
    <div class="hero-name">{report_title}</div>
    <div class="hero-score-row">
      <div class="hero-score" id="score-display">0</div>
      <div class="hero-title">{esc(title)}</div>
    </div>
    <div class="hero-overall-eval fade-in">{esc(overall_eval)}</div>
    <div class="hero-stats fade-in">
      <div class="hero-stat">
        <span class="hero-stat-icon">\U0001f916</span>
        <span class="hero-stat-val">{ai_tool_count}</span>
        <span class="hero-stat-label">AI 工具</span>
      </div>
      <div class="hero-stat">
        <span class="hero-stat-icon">\U0001f4ca</span>
        <span class="hero-stat-val">{scored_dim_count}/15</span>
        <span class="hero-stat-label">维度</span>
      </div>
      <div class="hero-stat">
        <span class="hero-stat-icon">\U0001f3c6</span>
        <span class="hero-stat-val">{ach_count}</span>
        <span class="hero-stat-label">成就</span>
      </div>
    </div>
    {top_dims_section}
    {ach_chips_section}
  </div>
  <div class="hero-arrow">↓</div>
</section>

<!-- ── Radar + Dimension Bars ── -->
<section class="section">
  <h2 class="section-title">维度雷达图</h2>
  <div class="radar-wrapper">
    <div class="radar-box"><canvas id="radar" width="340" height="340"></canvas></div>
    <div class="dim-bars" id="dim-bars"></div>
  </div>
</section>

<!-- ── Achievements ── -->
{ach_section}

<!-- ── Detail: Score Table ── -->
{detail_score_table}

<!-- ── Detail: Dimension Cards ── -->
{dim_cards_section}

<!-- ── Local Detail Hint (basic report only) ── -->
{local_detail_hint}

<!-- ── Highlights ── -->
<section class="section">
  <div class="hw-card highlights fade-in">
    <div class="hw-card-title">✦ 得分亮点</div>
    <ul>{highlights_html}</ul>
  </div>
</section>

<!-- ── Roadmap ── -->
<section class="section">
  <h2 class="section-title">AI 学习路线图</h2>
  <div class="roadmap-progress">
    <span class="rp-current">{current_level}</span>
    <span class="rp-arrow">──────→</span>
    <span class="rp-next">{next_level}</span>
  </div>
  <div class="roadmap-phases">{roadmap_html}</div>
</section>

<!-- ── Footer ── -->
<footer class="footer">
  <div>
    {detail_footer_note}
    <div class="footer-stats" id="footer-stats"></div>
    <div class="footer-disclaimer">本报告为非正式趣味评估，评分不代表绝对标准，仅供参考。数据仅写入本地，不上传任何服务器。</div>
  </div>
  <div id="share-section" style="display:none">
    <h3>扫码下载分享卡片</h3>
    <div id="qr-code"></div>
    <p style="font-size:0.82rem;color:#888;margin-bottom:0.5rem">长按保存图片后分享到朋友圈</p>
    <input type="text" id="share-url" readonly>
    <button class="btn-copy" onclick="copyUrl()">复制链接</button>
  </div>
</footer>

<script src="https://cdn.jsdelivr.net/npm/qrcodejs@1.0.0/qrcode.min.js"></script>
<script>
// ── Data ──
const TOTAL_SCORE = {total_score};
const RADAR_LABELS = {radar_labels};
const RADAR_VALUES = {radar_normalized};
const RADAR_RAW = {radar_values};
const DIM_META = {json.dumps({k: list(v) for k, v in DIMENSION_META.items()})};
const SCORES = {json.dumps({k: v.get('score', 0) if isinstance(v, dict) else 0 for k, v in scores.items()})};

// ── Particle Background ──
(function(){{
  const canvas = document.getElementById('particles');
  const ctx = canvas.getContext('2d');
  let W, H, particles;
  function resize(){{
    W = canvas.width = canvas.parentElement.offsetWidth;
    H = canvas.height = canvas.parentElement.offsetHeight;
  }}
  function Particle(){{
    this.x = Math.random()*W; this.y = Math.random()*H;
    this.vx = (Math.random()-0.5)*0.4; this.vy = (Math.random()-0.5)*0.4;
    this.r = Math.random()*1.5+0.5;
    this.alpha = Math.random()*0.5+0.2;
  }}
  Particle.prototype.update = function(){{
    this.x += this.vx; this.y += this.vy;
    if(this.x<0) this.x=W; if(this.x>W) this.x=0;
    if(this.y<0) this.y=H; if(this.y>H) this.y=0;
  }};
  function init(){{
    resize();
    var count = window.innerWidth < 480 ? 40 : 80;
    particles = Array.from({{length:count}}, ()=>new Particle());
  }}
  function draw(){{
    ctx.clearRect(0,0,W,H);
    particles.forEach(p=>{{
      p.update();
      ctx.beginPath(); ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
      ctx.fillStyle='rgba(0,255,240,'+p.alpha+')'; ctx.fill();
    }});
    var maxDist = window.innerWidth < 480 ? 80 : 120;
    for(var i=0;i<particles.length;i++){{
      for(var j=i+1;j<particles.length;j++){{
        var dx=particles[i].x-particles[j].x, dy=particles[i].y-particles[j].y;
        var dist=Math.sqrt(dx*dx+dy*dy);
        if(dist<maxDist){{
          ctx.beginPath();
          ctx.moveTo(particles[i].x,particles[i].y);
          ctx.lineTo(particles[j].x,particles[j].y);
          ctx.strokeStyle='rgba(0,255,240,'+(0.15*(1-dist/maxDist))+')';
          ctx.lineWidth=0.5; ctx.stroke();
        }}
      }}
    }}
    requestAnimationFrame(draw);
  }}
  window.addEventListener('resize',()=>{{resize(); particles.forEach(p=>{{p.x=Math.random()*W;p.y=Math.random()*H;}});}});
  init(); draw();
}})();

// ── Score Counter Animation ──
(function(){{
  var el = document.getElementById('score-display');
  var target = TOTAL_SCORE;
  var duration = 1800;
  var start = performance.now();
  function easeOut(t){{ return 1 - Math.pow(1-t, 3); }}
  function frame(now){{
    var t = Math.min((now-start)/duration,1);
    el.textContent = Math.round(easeOut(t)*target).toLocaleString();
    if(t<1) requestAnimationFrame(frame);
  }}
  requestAnimationFrame(frame);
}})();

// ── Dimension Bars ──
(function(){{
  var container = document.getElementById('dim-bars');
  var maxScore = Math.max(...Object.values(SCORES), 1);
  Object.entries(DIM_META).forEach(function(entry){{
    var key=entry[0], icon=entry[1][0], label=entry[1][1];
    var score = SCORES[key] || 0;
    var pct = (score/maxScore*100).toFixed(1);
    var row = document.createElement('div');
    row.className = 'dim-bar-row';
    row.innerHTML = '<span class="dim-bar-label">'+icon+' '+label+'</span>'
      +'<div class="dim-bar-track"><div class="dim-bar-fill" data-w="'+pct+'" style="width:0%"></div></div>'
      +'<span class="dim-bar-score">'+score.toLocaleString()+'</span>';
    container.appendChild(row);
  }});
  setTimeout(function(){{
    document.querySelectorAll('.dim-bar-fill').forEach(function(el){{
      el.style.width = el.dataset.w + '%';
    }});
  }}, 400);
}})();

// ── Radar Chart ──
(function(){{
  var canvas = document.getElementById('radar');
  var ctx = canvas.getContext('2d');
  var W = canvas.width, H = canvas.height;
  var cx = W/2, cy = H/2;
  var r = Math.min(W,H)*0.38;
  var n = RADAR_LABELS.length;
  var PI2 = Math.PI*2;
  var isMobile = window.innerWidth < 480;
  var fontSize = isMobile ? 8 : 9;

  function angle(i){{ return (i/n)*PI2 - Math.PI/2; }}

  function drawGrid(){{
    ctx.strokeStyle = 'rgba(0,255,240,0.1)';
    ctx.lineWidth = 1;
    [0.2,0.4,0.6,0.8,1.0].forEach(function(scale){{
      ctx.beginPath();
      for(var i=0;i<n;i++){{
        var a=angle(i), x=cx+r*scale*Math.cos(a), y=cy+r*scale*Math.sin(a);
        i===0 ? ctx.moveTo(x,y) : ctx.lineTo(x,y);
      }}
      ctx.closePath(); ctx.stroke();
    }});
    for(var i=0;i<n;i++){{
      ctx.beginPath();
      ctx.moveTo(cx,cy);
      ctx.lineTo(cx+r*Math.cos(angle(i)), cy+r*Math.sin(angle(i)));
      ctx.stroke();
    }}
  }}

  function drawLabels(){{
    ctx.font=fontSize+'px Inter,sans-serif';
    ctx.fillStyle='rgba(224,224,224,0.7)';
    ctx.textAlign='center'; ctx.textBaseline='middle';
    for(var i=0;i<n;i++){{
      var a=angle(i), lx=cx+(r+18)*Math.cos(a), ly=cy+(r+18)*Math.sin(a);
      ctx.fillText(RADAR_LABELS[i], lx, ly);
    }}
  }}

  var progress = 0;
  function drawData(p){{
    ctx.clearRect(0,0,W,H);
    drawGrid(); drawLabels();
    var vals = RADAR_VALUES.map(function(v){{return v/100*p;}});
    ctx.beginPath();
    for(var i=0;i<n;i++){{
      var a=angle(i), rv=vals[i]*r, x=cx+rv*Math.cos(a), y=cy+rv*Math.sin(a);
      i===0 ? ctx.moveTo(x,y) : ctx.lineTo(x,y);
    }}
    ctx.closePath();
    ctx.fillStyle='rgba(0,255,240,0.12)'; ctx.fill();
    ctx.strokeStyle='#00fff0'; ctx.lineWidth=2; ctx.stroke();
    for(var i=0;i<n;i++){{
      var a=angle(i), rv=vals[i]*r, x=cx+rv*Math.cos(a), y=cy+rv*Math.sin(a);
      ctx.beginPath(); ctx.arc(x,y,3,0,PI2);
      ctx.fillStyle='#00fff0'; ctx.fill();
    }}
  }}

  var start = performance.now();
  function animRadar(now){{
    progress = Math.min((now-start)/1200, 1);
    drawData(progress);
    if(progress<1) requestAnimationFrame(animRadar);
  }}
  requestAnimationFrame(animRadar);
}})();

// ── IntersectionObserver for fade-in ──
(function(){{
  var obs = new IntersectionObserver(function(entries){{
    entries.forEach(function(e){{ if(e.isIntersecting) e.target.classList.add('visible'); }});
  }}, {{threshold:0.15}});
  document.querySelectorAll('.fade-in').forEach(function(el){{ obs.observe(el); }});
}})();

// ── Footer Stats ──
document.getElementById('footer-stats').innerHTML =
  '应用程序 · 终端工具 · 模型配置 · 本地模型 · 15 个维度综合评估';

// ── Share (QR code for share card image) ──
(function(){{
  var shareCardUrl = '{share_card_url}';
  if(!shareCardUrl) return;
  var sec = document.getElementById('share-section');
  sec.style.display='flex';
  var urlInput = document.getElementById('share-url');
  urlInput.value = shareCardUrl;
  if(typeof QRCode!=='undefined'){{
    new QRCode(document.getElementById('qr-code'),{{
      text:shareCardUrl, width:160, height:160,
      colorDark:'#00fff0', colorLight:'#0a0a0f'
    }});
  }}
}})();

function copyUrl(){{
  var input = document.getElementById('share-url');
  input.select();
  document.execCommand('copy');
  var btn = document.querySelector('.btn-copy');
  btn.textContent='已复制！'; setTimeout(function(){{btn.textContent='复制链接';}}, 2000);
}}
</script>
</body>
</html>'''


def generate_poster(score_result):
    """Generate a mobile-first poster-style HTML for sharing (report.html)."""
    import html as _html
    def esc(s): return _html.escape(str(s))

    user_name    = score_result.get('user_name', '')
    total_score  = score_result.get('total_score', 0)
    title        = score_result.get('title', 'AI 初探者')
    scores       = score_result.get('dimension_scores', {})
    achievements = score_result.get('rare_achievements', [])
    highlights   = score_result.get('highlights', [])
    scan_time    = score_result.get('scan_time', '')

    dim_labels = {
        'apps':               ('🖥', '应用程序'),
        'cli_tools':          ('⚡', '终端工具'),
        'npm_globals':        ('📦', 'npm 包'),
        'claude_skills':      ('🤖', 'Skills'),
        'model_configs':      ('⚙', '模型配置'),
        'python_ai_packages': ('🐍', 'Python AI'),
        'ide_ai_plugins':     ('🔌', 'IDE 插件'),
        'ai_home_folders':    ('📁', 'AI 文件夹'),
        'hardware':           ('💻', '设备硬件'),
        'network':            ('🌐', '网络能力'),
        'local_models':       ('🏠', '本地模型'),
        'api_keys':           ('🔑', 'API Key'),
        'browser_ai_plugins': ('🧩', '浏览器插件'),
        'docker_ai_images':   ('🐳', 'Docker'),
        'jupyter':            ('📓', 'Jupyter'),
        'env_ai_config':      ('🔧', '环境变量'),
    }

    # Top 3 dims as pills
    dim_items = []
    for k, v in scores.items():
        s = v.get('score', 0) if isinstance(v, dict) else 0
        if s > 0:
            icon, label = dim_labels.get(k, ('·', k))
            dim_items.append((label, s, icon))
    dim_items.sort(key=lambda x: -x[1])

    top3_pills_html = ''
    for label, s, icon in dim_items[:3]:
        top3_pills_html += (
            f'<div class="dim-pill">'
            f'<span class="dim-pill-icon">{icon}</span>'
            f'<span class="dim-pill-label">{esc(label)}</span>'
            f'<span class="dim-pill-score">{s:,}</span>'
            f'</div>'
        )

    # Dim bars (top 6, for details section)
    top_dims = dim_items[:6]
    max_dim_score = max((d[1] for d in top_dims), default=1)
    dim_bars_html = ''
    for label, s, icon in top_dims:
        pct = round(s / max_dim_score * 100)
        dim_bars_html += (
            f'<div class="dim-bar-row">'
            f'<div class="dim-bar-label">{icon} {esc(label)}</div>'
            f'<div class="dim-bar-track"><div class="dim-bar-fill" style="--w:{pct}%"></div></div>'
            f'<div class="dim-bar-score">{s:,}</div>'
            f'</div>'
        )

    # Achievement cards — full detail (level badge + desc + title + tool + copy)
    lvl_bg    = {'SSR': '#fbbf24', 'SR': '#a855f7', 'R': '#00fff0'}
    lvl_tc    = {'SSR': '#000',    'SR': '#fff',    'R': '#000'}
    lvl_border= {'SSR': '#fbbf24', 'SR': '#a855f7', 'R': '#00fff0'}
    lvl_desc  = {'SSR': '传说级成就！', 'SR': '史诗级成就！', 'R': '稀有成就达成！'}
    ach_html = ''
    for ach in achievements:
        lvl   = ach.get('level', 'R')
        at    = ach.get('title', '')
        tool  = ach.get('tool', '')
        copy  = ach.get('copy', '')
        bg    = lvl_bg.get(lvl, '#00fff0')
        tc    = lvl_tc.get(lvl, '#000')
        bd    = lvl_border.get(lvl, '#00fff0')
        desc  = lvl_desc.get(lvl, '')
        tool_html = f'<div class="ach-card-tool">{esc(tool)}</div>' if tool else ''
        copy_html = f'<div class="ach-card-copy">"{esc(copy)}"</div>' if copy else ''
        ach_html += (
            f'<div class="ach-card" style="border-color:{bd}33;background:{bg}08">'
            f'<div class="ach-card-header">'
            f'<span class="ach-level-box" style="background:{bg};color:{tc}">{lvl}</span>'
            f'<span class="ach-level-desc">{esc(desc)}</span>'
            f'</div>'
            f'<div class="ach-card-title">{esc(at)}</div>'
            f'{tool_html}'
            f'{copy_html}'
            f'</div>'
        )

    hl_html = ''
    for h in highlights[:4]:
        hl_html += f'<div class="hl-item"><span class="hl-dot">✦</span><span>{esc(h)}</span></div>'

    # Page title line
    if user_name:
        page_title = f'{esc(user_name)} 的 AI 能力侧写报告'
    else:
        page_title = 'AI 能力侧写报告'

    eval_text = esc(get_overall_eval(title, total_score))

    share_html = (
        '<div class="share-area">'
        '<div class="qr-row">'
        '<div class="qr-item"><div id="p-qr-github"></div>'
        '<div class="qr-label">获取此 Skill</div></div>'
        '<div class="qr-item" id="qr-poster-wrap" style="display:none">'
        '<div id="p-qr"></div>'
        '<div class="qr-label">扫码下载分享海报</div></div>'
        '</div>'
        '</div>'
    )

    ai_tool_count    = count_ai_tools(scores)
    scored_dim_count = count_scored_dims(scores)
    ach_count        = len(achievements)

    return f'''<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<title>AI 能力侧写{' — ' + esc(user_name) if user_name else ''}</title>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html,body{{background:#07081a;min-height:100vh;display:flex;justify-content:center;
  font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Helvetica Neue',sans-serif;
  -webkit-font-smoothing:antialiased}}

/* ── Poster wrapper ── */
.poster{{width:100%;max-width:480px;min-height:100vh;
  background:linear-gradient(155deg,#0e0b20 0%,#08101e 50%,#080e1a 100%);
  color:#e8e8f0;position:relative;overflow:hidden;padding-bottom:2.5rem}}
.poster::before{{content:'';position:absolute;inset:0;pointer-events:none;z-index:0;
  background:
    radial-gradient(ellipse 80% 40% at 90% 5%,rgba(168,85,247,.13) 0%,transparent 65%),
    radial-gradient(ellipse 60% 55% at 10% 90%,rgba(0,255,240,.07) 0%,transparent 65%),
    radial-gradient(ellipse 40% 30% at 50% 50%,rgba(99,102,241,.05) 0%,transparent 60%)}}

/* ── Dot grid texture ── */
.poster::after{{content:'';position:absolute;inset:0;pointer-events:none;z-index:0;
  background-image:radial-gradient(rgba(255,255,255,.025) 1px,transparent 1px);
  background-size:28px 28px}}

/* ── Header ── */
.poster-header{{position:relative;z-index:1;
  display:flex;justify-content:space-between;align-items:center;
  padding:1.1rem .75rem 0}}
.poster-brand{{font-size:.65rem;letter-spacing:.2em;color:rgba(0,255,240,.5);font-weight:700;text-transform:uppercase}}
.poster-date{{font-size:.62rem;color:rgba(255,255,255,.2)}}

/* ── Hero ── */
.poster-hero{{position:relative;z-index:1;text-align:center;padding:1.3rem .75rem 1.2rem}}
.poster-supertitle{{font-size:.72rem;color:rgba(255,255,255,.35);letter-spacing:.08em;margin-bottom:.5rem}}
.poster-title{{font-size:1.25rem;font-weight:700;color:rgba(255,255,255,.88);
  margin-bottom:1.2rem;line-height:1.35}}

/* score row: number + badge inline */
.score-row{{display:flex;align-items:baseline;justify-content:center;
  gap:.7rem;margin-bottom:1rem}}
.poster-score{{font-size:clamp(3.5rem,16vw,5.5rem);font-weight:900;
  font-variant-numeric:tabular-nums;line-height:1;letter-spacing:-.02em;
  background:linear-gradient(130deg,#00fff0 0%,#a855f7 55%,#22d3ee 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  filter:drop-shadow(0 0 20px rgba(0,255,240,.3))}}
.poster-level-tag{{font-size:1rem;font-weight:600;color:#00fff0;
  letter-spacing:.06em;white-space:nowrap;
  text-shadow:0 0 12px rgba(0,255,240,.5)}}

/* eval text */
.poster-eval{{font-size:.82rem;color:rgba(255,255,255,.52);line-height:1.7;
  margin-bottom:1.2rem;padding:0 .5rem;text-align:center}}

/* ── Stat pills row ── */
.stat-pills{{display:flex;flex-wrap:wrap;justify-content:center;gap:.5rem;
  margin-bottom:.8rem}}
.stat-pill{{display:inline-flex;align-items:center;gap:.4rem;
  padding:.38rem .85rem;border-radius:100px;
  background:rgba(255,255,255,.055);
  border:1px solid rgba(255,255,255,.12);
  font-size:.78rem;color:rgba(255,255,255,.75);white-space:nowrap}}
.stat-pill-icon{{font-size:.85rem}}
.stat-pill-val{{font-weight:700;color:#e8e8f0;font-variant-numeric:tabular-nums}}

/* ── Top-3 dim pills ── */
.dim-pills{{display:flex;flex-wrap:wrap;justify-content:center;gap:.5rem;
  margin-bottom:.9rem}}
.dim-pill{{display:inline-flex;align-items:center;gap:.35rem;
  padding:.35rem .8rem;border-radius:100px;
  background:rgba(255,255,255,.042);
  border:1px solid rgba(255,255,255,.1);
  font-size:.75rem;color:rgba(255,255,255,.65)}}
.dim-pill-icon{{font-size:.82rem}}
.dim-pill-label{{color:rgba(255,255,255,.6)}}
.dim-pill-score{{font-weight:700;color:#00fff0;font-variant-numeric:tabular-nums;margin-left:.2rem}}

/* ── Achievement cards ── */
.ach-grid{{display:grid;grid-template-columns:1fr 1fr;gap:.55rem}}
.ach-card{{border-radius:10px;padding:.65rem .75rem;border:1px solid transparent}}
.ach-card-header{{display:flex;align-items:center;gap:.45rem;margin-bottom:.4rem}}
.ach-level-box{{padding:.15rem .45rem;border-radius:4px;
  font-size:.58rem;font-weight:900;letter-spacing:.06em;line-height:1.4;flex-shrink:0}}
.ach-level-desc{{font-size:.6rem;color:rgba(255,255,255,.4);font-style:italic}}
.ach-card-title{{font-size:.73rem;font-weight:700;color:rgba(255,255,255,.85);
  line-height:1.35;margin-bottom:.28rem}}
.ach-card-tool{{font-size:.62rem;font-family:monospace;color:rgba(0,255,240,.5);
  margin-bottom:.22rem}}
.ach-card-copy{{font-size:.62rem;color:rgba(255,255,255,.38);font-style:italic;
  line-height:1.45}}

/* ── Divider ── */
.divider{{position:relative;z-index:1;margin:0 .75rem .9rem;
  border:none;border-top:1px solid rgba(255,255,255,.07)}}

/* ── Section card ── */
.s-card{{position:relative;z-index:1;margin:0 .75rem .9rem;
  background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);
  border-radius:14px;padding:.9rem 1rem}}
.s-title{{font-size:.6rem;letter-spacing:.15em;text-transform:uppercase;
  color:rgba(168,85,247,.7);font-weight:700;margin-bottom:.7rem}}

/* dim bars */
.dim-bar-row{{display:flex;align-items:center;gap:.5rem;margin-bottom:.5rem}}
.dim-bar-row:last-child{{margin-bottom:0}}
.dim-bar-label{{width:7rem;flex-shrink:0;font-size:.68rem;color:rgba(255,255,255,.5);
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.dim-bar-track{{flex:1;height:4px;background:rgba(255,255,255,.06);border-radius:2px;overflow:hidden}}
.dim-bar-fill{{height:100%;border-radius:2px;width:0;
  background:linear-gradient(90deg,#00fff0,#a855f7);
  transition:width 1.1s cubic-bezier(.16,1,.3,1)}}
.dim-bar-score{{width:2.8rem;text-align:right;flex-shrink:0;
  font-size:.62rem;color:rgba(0,255,240,.6);font-variant-numeric:tabular-nums}}

/* highlights */
.hl-item{{display:flex;align-items:flex-start;gap:.4rem;
  font-size:.75rem;color:rgba(255,255,255,.58);line-height:1.5;margin-bottom:.38rem}}
.hl-item:last-child{{margin-bottom:0}}
.hl-dot{{color:#22c55e;flex-shrink:0}}

/* share */
.poster-footer{{position:relative;z-index:1;margin:0 .75rem;text-align:center}}
.share-area{{padding:.85rem;background:rgba(255,255,255,.025);
  border:1px solid rgba(255,255,255,.06);border-radius:14px;
  display:flex;flex-direction:column;align-items:center;gap:.45rem;margin-bottom:.8rem}}
.qr-row{{display:flex;gap:1.5rem;align-items:flex-start;justify-content:center}}
.qr-item{{display:flex;flex-direction:column;align-items:center;gap:.35rem}}
#p-qr canvas,#p-qr img,#p-qr-github canvas,#p-qr-github img{{border-radius:6px}}
.share-label,.qr-label{{font-size:.65rem;color:rgba(255,255,255,.3)}}
.poster-disclaimer{{font-size:.56rem;color:rgba(255,255,255,.16);letter-spacing:.04em}}
</style>
</head>
<body>
<div class="poster">

<div class="poster-header">
  <div class="poster-brand">AI 能力侧写报告 ·</div>
  <div class="poster-date">{esc(scan_time)}</div>
</div>

<div class="poster-hero">
  <div class="poster-title">{page_title}</div>

  <div class="score-row">
    <span class="poster-score" id="p-score">0</span>
    <span class="poster-level-tag">{esc(title)}</span>
  </div>

  <div class="poster-eval">{eval_text}</div>

  <div class="stat-pills">
    <div class="stat-pill"><span class="stat-pill-icon">🤖</span><span class="stat-pill-val">{ai_tool_count}</span>&nbsp;AI 工具</div>
    <div class="stat-pill"><span class="stat-pill-icon">📊</span><span class="stat-pill-val">{scored_dim_count}/16</span>&nbsp;维度</div>
    <div class="stat-pill"><span class="stat-pill-icon">🏆</span><span class="stat-pill-val">{ach_count}</span>&nbsp;成就</div>
  </div>

  <div class="dim-pills">
    {top3_pills_html}
  </div>

  </div>

<hr class="divider">

<div class="s-card">
  <div class="s-title">得分分布</div>
  {dim_bars_html}
</div>

<div class="s-card">
  <div class="s-title">稀有成就</div>
  <div class="ach-grid">{ach_html}</div>
</div>

<div class="poster-footer">
  {share_html}
  <div class="poster-disclaimer">非正式趣味评估 · 仅供参考 · 数据不上传任何服务器</div>
</div>

</div>
<script src="https://cdn.jsdelivr.net/npm/qrcodejs@1.0.0/qrcode.min.js"></script>
<script>
(function(){{
  var el=document.getElementById('p-score'),t={total_score},s=performance.now(),d=1400;
  function tick(n){{
    var p=Math.min((n-s)/d,1),e=1-Math.pow(1-p,3);
    el.textContent=Math.round(e*t).toLocaleString('zh-CN');
    if(p<1) requestAnimationFrame(tick);
  }}
  requestAnimationFrame(tick);
}})();
document.querySelectorAll('.dim-bar-fill').forEach(function(el){{
  var w=el.style.getPropertyValue('--w');
  setTimeout(function(){{el.style.width=w;}},300);
}});
(function(){{
  var github='https://github.com/yxspace/ai-level-skill';
  var isRemote=!window.location.href.startsWith('file://');
  if(typeof QRCode==='undefined') return;
  var sz=isRemote?100:120;
  new QRCode(document.getElementById('p-qr-github'),{{text:github,width:sz,height:sz,
    colorDark:'#00fff0',colorLight:'#07081a'}});
  if(isRemote){{
    var wrap=document.getElementById('qr-poster-wrap');
    if(wrap) wrap.style.display='flex';
    new QRCode(document.getElementById('p-qr'),{{text:window.location.href,width:100,height:100,
      colorDark:'#a855f7',colorLight:'#07081a'}});
  }}
}})();
</script>
<script src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js"></script>
<style>
#ai-save-btn{{position:fixed;bottom:1.4rem;right:1.2rem;z-index:9999;
  background:linear-gradient(135deg,#00fff0,#a855f7);color:#07081a;
  border:none;border-radius:14px;padding:.55rem .85rem;font-size:.68rem;
  font-weight:700;cursor:pointer;letter-spacing:.03em;line-height:1.5;
  box-shadow:0 4px 18px rgba(0,255,240,.35);
  font-family:-apple-system,BlinkMacSystemFont,sans-serif;
  text-align:center;white-space:nowrap}}
#ai-save-btn:active{{opacity:.75;transform:scale(.97)}}
#ai-save-toast{{position:fixed;bottom:5rem;left:50%;transform:translateX(-50%);
  z-index:10000;background:rgba(7,8,26,.92);backdrop-filter:blur(10px);
  border:1px solid rgba(0,255,240,.25);border-radius:100px;
  padding:.5rem 1.3rem;font-size:.72rem;color:rgba(0,255,240,.9);
  font-family:-apple-system,BlinkMacSystemFont,sans-serif;letter-spacing:.03em;
  white-space:nowrap;pointer-events:none;
  opacity:0;transition:opacity .3s ease}}
#ai-save-toast.show{{opacity:1}}
</style>
<button id="ai-save-btn" onclick="aiSavePoster()">保存图片分享到朋友圈</button>
<div id="ai-save-toast">图片已保存，打开相册分享到朋友圈 ↗</div>
<script>
function aiSavePoster(){{
  var btn=document.getElementById('ai-save-btn');
  var toast=document.getElementById('ai-save-toast');
  btn.textContent='生成中...';btn.disabled=true;
  var poster=document.querySelector('.poster')||document.body;
  html2canvas(poster,{{scale:2,useCORS:true,allowTaint:true,
    backgroundColor:'#07081a',logging:false,
    onclone:function(doc){{
      var score=doc.querySelector('.poster-score');
      if(score){{score.style.webkitTextFillColor='#00fff0';
        score.style.background='none';score.style.webkitBackgroundClip='unset';
        score.style.backgroundClip='unset';score.style.filter='none';}}
      var b=doc.getElementById('ai-save-btn');if(b)b.style.display='none';
      var t=doc.getElementById('ai-save-toast');if(t)t.style.display='none';
    }}
  }}).then(function(canvas){{
    btn.textContent='保存图片分享到朋友圈';btn.disabled=false;
    var a=document.createElement('a');a.download='ai-level-poster.png';
    a.href=canvas.toDataURL('image/png');a.click();
    toast.classList.add('show');
    setTimeout(function(){{toast.classList.remove('show');}},6000);
  }}).catch(function(){{btn.textContent='保存图片分享到朋友圈';btn.disabled=false;}});
}}
</script>
</body>
</html>'''


def main():
    result_path = OUTPUT_DIR / 'score_result.json'
    if not result_path.exists():
        print(f'[generate_report] 错误: {result_path} 不存在')
        return

    score_result = json.loads(result_path.read_text(encoding='utf-8'))

    import datetime as _dt
    score_result.setdefault('scan_time', _dt.datetime.now().strftime('%Y-%m-%d'))

    basic_html = generate_poster(score_result)
    basic_path = OUTPUT_DIR / 'report.html'
    basic_path.write_text(basic_html, encoding='utf-8')
    basic_kb = round(basic_path.stat().st_size / 1024)

    detail_html = generate(score_result, detail=True)
    detail_path = OUTPUT_DIR / 'report_detail.html'
    detail_path.write_text(detail_html, encoding='utf-8')
    detail_kb = round(detail_path.stat().st_size / 1024)

    print(f'[generate_report] 基础报告 (可分享):  {basic_path}  ({basic_kb} KB)')
    print(f'[generate_report] 详细报告 (仅本地):  {detail_path}  ({detail_kb} KB)')


if __name__ == '__main__':
    main()
