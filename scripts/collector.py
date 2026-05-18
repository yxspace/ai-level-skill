#!/usr/bin/env python3
"""ai-level-skill: 设备 AI 能力扫描器 — 纯 Python 标准库实现，支持 macOS 和 Windows"""

import os
import re
import sys
import json
import time
import socket
import struct
import datetime
import subprocess
import platform
import concurrent.futures
import urllib.request
import urllib.error
from pathlib import Path

PLATFORM = platform.system()   # 'Darwin' | 'Windows'
SKILL_DIR = Path(__file__).parent.parent
OUTPUT_DIR = Path.cwd() / 'output'
OUTPUT_DIR.mkdir(exist_ok=True)

# ─────────────────────────────────────────────
#  AI 工具白名单（用于在收集阶段预标注 is_ai，消除对模型判断的依赖）
# ─────────────────────────────────────────────

AI_APPS = {
    # AI 编程 IDE
    'cursor', 'windsurf', 'void', 'zed',
    # AI 助手客户端
    'claude', 'chatgpt', 'perplexity', 'poe', 'character.ai', 'pi',
    'copilot', 'microsoft copilot', 'github copilot',
    # 本地模型运行器
    'lm studio', 'jan', 'gpt4all', 'ollama', 'koboldai', 'gpt4all-ui',
    'openwebui', 'open webui', 'lobechat', 'nextchat', 'anything llm', 'anythingllm',
    'msty', 'enchanted', 'diffuse',
    # 图像生成
    'diffusionbee', 'draw things', 'comfyui', 'invokeai', 'automatic1111',
    'fooocus', 'stable diffusion', 'leonardo', 'midjourney', 'adobe firefly',
    'canva', 'ideogram', 'playground ai', 'stabledifffusion',
    # 视频/音频 AI
    'runway', 'descript', 'eleven labs', 'elevenlabs', 'murf', 'suno', 'udio',
    'heygen', 'synthesia', 'captions', 'capcut', 'opus clip', 'opusclip',
    # 录音/转写
    'macwhisper', 'otter', 'rewind', 'recall', 'whisper transcription',
    'superwhisper', 'cleft', 'krisp', 'cleanmymac',
    # AI 生产力
    'raycast', 'mem', 'reflect', 'notion', 'readwise reader',
    'elicit', 'consensus', 'research rabbit', 'typingmind',
    # 中文 AI 应用
    '豆包', '文心一言', '通义千问', '讯飞星火', 'kimi', '智谱清言',
    '秘塔搜索', '海螺ai', '天工ai', '腾讯元宝', '商量', 'minimax',
    'stepfun', '阶跃星辰', 'chatglm', '讯飞输入法', 'hailuo',
    # AI 代码辅助
    'tabnine', 'codeium', 'amazon codewhisperer', 'codewhisperer', 'pieces',
    # 图像编辑 AI
    'topaz photo ai', 'topaz gigapixel ai', 'topaz video ai',
    'luminar neo', 'luminar ai', 'photoroom', 'remove.bg',
    # 其他专业 AI
    'replit', 'sourcegraph', 'jasper', 'copy.ai', 'writesonic',
    'grammarly', 'otter.ai',
}

AI_CLI_TOOLS = {
    # Claude / Anthropic
    'claude': 2.0, 'claude-code': 2.0,
    # AI 编程助手
    'aider': 2.0, 'fabric': 2.0, 'continue': 2.0, 'cody': 2.0,
    'cursor': 2.0, 'windsurf': 2.0, 'copilot': 2.0, 'codeium': 2.0,
    'tabnine': 2.0, 'codex': 2.0, 'gh-copilot': 2.0,
    'goose': 2.0, 'amp': 2.0, 'agentic': 2.0, 'repomix': 2.0,
    # 通用 LLM CLI
    'llm': 2.0, 'openai': 2.0, 'groq': 2.0, 'perplexity': 2.0,
    'mods': 2.0, 'aichat': 2.0, 'ai-chat': 2.0, 'chatblade': 2.0,
    'oterm': 2.0, 'tenere': 2.0, 'gollama': 2.0,
    'ttok': 2.0, 'files-to-prompt': 2.0, 'shot-scraper': 2.0,
    'datasette': 2.0, 'strip-tags': 1.5, 'symbex': 1.5,
    # AI Shell 工具
    'sgpt': 2.0, 'shell-gpt': 2.0, 'ai-shell': 2.0,
    'gorilla-cli': 2.0, 'gptcommit': 2.0, 'rtk': 2.0,
    # 本地模型运行时
    'ollama': 2.5, 'jan': 2.0, 'lms': 2.0, 'lmstudio': 2.0,
    'llamafile': 3.0, 'llama-server': 2.5, 'llama-cli': 2.5,
    'llama-cpp': 2.5, 'koboldcpp': 2.5, 'gpt4all': 2.0,
    'tgwui': 2.5, 'mlc-chat': 2.5, 'mlc_chat': 2.5, 'mlc-llm': 2.5,
    'privategpt': 2.5, 'localai': 3.0, 'localai-server': 3.0,
    'exllama': 2.5, 'exllamav2': 2.5,
    # 图像生成
    'comfy': 2.5, 'comfyui': 2.5, 'invokeai': 2.5, 'fooocus': 2.5,
    'stable-diffusion-webui': 2.5, 'sd-webui': 2.5, 'automatic1111': 2.5,
    'sd': 2.5, 'sdxl': 2.5, 'imagen': 2.5, 'imagen3': 2.5,
    # 语音/TTS
    'whisper': 2.0, 'openai-whisper': 2.0, 'faster-whisper': 2.0,
    'tts': 2.0, 'bark': 2.0, 'voicevox': 2.0, 'tortoise-tts': 2.5,
    # 推理加速 / 服务端部署
    'vllm': 3.0, 'text-generation-inference': 3.0, 'tgi': 3.0,
    'triton': 3.0, 'tensorrt': 3.0, 'litellm': 2.5,
    'bentoml': 2.5, 'bento': 2.5, 'truss': 2.5,
    'openvino': 2.5, 'onnxruntime': 2.5, 'ctranslate2': 2.5,
    # 训练 / 微调
    'accelerate': 2.5, 'peft': 2.5, 'torchrun': 2.5,
    'deepspeed': 3.0, 'axolotl': 3.0, 'unsloth': 3.0,
    'megatron': 3.0, 'nemo': 3.0, 'skypilot': 2.5, 'sky': 2.5,
    # 实验管理
    'mlflow': 2.0, 'wandb': 2.0, 'dvc': 2.0, 'clearml': 2.0,
    'neptune': 2.0, 'ray': 2.5,
    # HuggingFace 生态
    'huggingface-cli': 2.0, 'huggingface_hub': 2.0,
    'transformers-cli': 2.0, 'optimum-cli': 2.0,
    'datasets-cli': 1.5,
    # AI 应用框架
    'dspy': 2.5, 'promptfoo': 2.0, 'lmql': 2.5,
    'outlines': 2.5, 'instructor': 2.5, 'guidance': 2.5,
    'semantic-kernel': 2.5, 'haystack': 2.5,
    'langflow': 2.5, 'flowise': 2.5, 'dify': 2.5, 'chainlit': 2.0,
    'gradio': 2.0, 'streamlit': 2.0, 'txtai': 2.5,
    # 评估
    'ragas': 2.5, 'deepeval': 2.5, 'trulens': 2.5,
    # 其他
    'gpt-engineer': 2.5, 'gpt_engineer': 2.5,
    'prompttools': 2.0, 'promptbase': 2.0,
    'llmware': 2.5, 'phidata': 2.5,
}

AI_CLI_KEYWORDS = {
    'llm', 'gpt', 'claude', 'openai', 'anthropic', 'gemini', 'mistral',
    'llama', 'falcon', 'diffusion', 'whisper', 'copilot', 'codeium',
    'tabnine', 'langchain', 'hugging', 'transformer', 'embedding',
    'vectordb', 'cohere', 'groq', 'replicate', 'perplexity', 'ollama',
    'stablelm', 'deepseek', 'qwen', 'baichuan', 'chatglm', 'internlm',
    'moonshot', 'ernie', 'wenxin', 'tongyi',
}

NON_AI_CLI = {
    'git', 'git-lfs', 'node', 'npm', 'npx', 'yarn', 'pnpm', 'bun',
    'brew', 'mas', 'curl', 'wget', 'httpie', 'xh',
    'python', 'python3', 'python3.9', 'python3.10', 'python3.11',
    'python3.12', 'python3.13', 'pyenv', 'pyenv-virtualenv',
    'pip', 'pip3', 'pipx', 'uv', 'poetry', 'pdm', 'hatch', 'rye', 'conda',
    'ruby', 'gem', 'bundle', 'bundler', 'rbenv', 'rvm',
    'cargo', 'rustc', 'rustup', 'rust-analyzer', 'clippy',
    'go', 'gopls', 'golangci-lint', 'gofmt',
    'java', 'javac', 'mvn', 'gradle', 'kotlin', 'kotlinc',
    'make', 'cmake', 'ninja', 'meson', 'bazel', 'buck', 'pants',
    'gcc', 'g++', 'clang', 'clang++', 'cc', 'c++', 'ld', 'lld', 'ar',
    'vim', 'nvim', 'neovim', 'emacs', 'nano', 'micro', 'helix',
    'tmux', 'screen', 'zellij', 'byobu',
    'zsh', 'bash', 'fish', 'sh', 'dash', 'tcsh', 'nushell',
    'ssh', 'scp', 'sftp', 'rsync', 'rclone', 'restic', 'borg',
    'tar', 'zip', 'unzip', 'gzip', 'gunzip', 'xz', 'bzip2', '7z', 'p7zip',
    'grep', 'rg', 'ripgrep', 'ag', 'ack', 'fzf', 'fd', 'find',
    'locate', 'mdfind', 'xargs', 'parallel',
    'sed', 'awk', 'perl', 'lua', 'ruby',
    'jq', 'yq', 'fx', 'jo', 'xsv', 'miller',
    'htop', 'btop', 'top', 'ps', 'kill', 'pkill', 'killall',
    'lsof', 'pgrep', 'netstat', 'ss',
    'ping', 'traceroute', 'nmap', 'nc', 'ncat', 'socat',
    'openssl', 'gpg', 'gnupg', 'age', 'pass', '1password-cli', 'op',
    'ffmpeg', 'ffprobe', 'imagemagick', 'convert', 'exiftool', 'gifsicle',
    'sqlite3', 'mysql', 'psql', 'pg_dump', 'pgcli',
    'redis-cli', 'mongo', 'mongodump', 'mongorestore',
    'docker', 'docker-compose', 'podman', 'lima', 'colima', 'containerd',
    'kubectl', 'helm', 'k9s', 'kubectx', 'kubens', 'kustomize', 'flux',
    'terraform', 'tofu', 'ansible', 'ansible-playbook',
    'vagrant', 'packer', 'pulumi', 'cdktf',
    'aws', 'gcloud', 'az', 'doctl', 'heroku', 'flyctl', 'railway',
    'netlify', 'vercel', 'wrangler', 'cf',
    'gh', 'hub', 'lab', 'glab', 'tea',
    'lazygit', 'tig', 'delta', 'difftastic',
    'bat', 'cat', 'less', 'more', 'head', 'tail',
    'ls', 'lsd', 'eza', 'exa', 'tree', 'broot',
    'rm', 'cp', 'mv', 'ln', 'chmod', 'chown', 'mkdir', 'rmdir',
    'eslint', 'prettier', 'tsc', 'tsx', 'ts-node', 'deno',
    'jest', 'vitest', 'mocha', 'playwright', 'cypress', 'puppeteer',
    'black', 'isort', 'ruff', 'flake8', 'mypy', 'pylint', 'pytest', 'tox',
    'nginx', 'apache2', 'caddy', 'traefik', 'envoy',
    'code', 'code-insiders', 'codium', 'subl', 'atom',
    'xcode-select', 'xcrun', 'xcodebuild', 'simctl',
    'swift', 'swiftc', 'swiftpm', 'swift-package',
    'dart', 'flutter', 'pub',
    'dotnet', 'nuget', 'paket',
    'php', 'composer', 'artisan',
    'r', 'rscript', 'julia',
    'nix', 'nix-env', 'nix-shell', 'home-manager',
    'guile', 'racket', 'sbcl', 'lein', 'clj', 'clojure',
    'hexdump', 'xxd', 'od',
    'strace', 'dtrace', 'perf', 'valgrind', 'lldb', 'gdb',
    'watch', 'cron', 'at', 'launchctl', 'systemctl', 'service',
    'osascript', 'automator', 'shortcuts',
    'pbcopy', 'pbpaste', 'xclip', 'xsel', 'wl-copy',
    'date', 'cal', 'bc', 'dc',
    'wc', 'sort', 'uniq', 'cut', 'tr', 'nl', 'fmt', 'fold',
    'diff', 'patch', 'comm', 'cmp',
    'md5sum', 'sha256sum', 'sha1sum', 'shasum', 'md5', 'sha256',
    'mount', 'umount', 'diskutil', 'df', 'du', 'lsblk',
    'ifconfig', 'ip', 'route', 'arp', 'dig', 'nslookup', 'host',
    'tcpdump', 'tshark',
    'caffeinate', 'pmset', 'sysctl', 'launchctl',
    'security', 'codesign', 'spctl', 'mdutil', 'mdls',
    'defaults', 'scutil', 'networksetup', 'systemsetup',
    'asdf', 'mise', 'rtx',
    'direnv', 'dotenv',
    'tldr', 'man', 'info',
    'test', 'true', 'false', 'echo', 'printf', 'read',
    'env', 'export', 'source', 'eval', 'exec',
}

AI_NPM_PACKAGES = {
    'openai', '@anthropic-ai/sdk', '@anthropic-ai/claude-code',
    'langchain', '@langchain/core', '@langchain/anthropic', '@langchain/openai',
    '@langchain/community', '@langchain/google-genai', '@langchain/groq',
    '@langchain/mistralai', '@langchain/cohere', '@langchain/ollama',
    'llamaindex', 'llamaindexts', '@llamaindex/core',
    'ollama', 'groq-sdk', 'cohere-ai',
    '@mistralai/mistralai', 'replicate', '@huggingface/inference',
    '@huggingface/hub', '@huggingface/transformers',
    'transformers', '@xenova/transformers',
    'ai', '@ai-sdk/openai', '@ai-sdk/anthropic', '@ai-sdk/google',
    '@ai-sdk/groq', '@ai-sdk/mistral', '@ai-sdk/cohere',
    '@ai-sdk/amazon-bedrock', '@ai-sdk/azure', '@ai-sdk/ollama',
    '@vercel/ai',
    '@google/generative-ai', '@google-ai/generativelanguage',
    'together-ai', 'fireworks-ai', '@fireworks-ai/sdk',
    'vectordb', 'chromadb', '@pinecone-database/pinecone', 'pinecone',
    '@qdrant/js-client-rest', 'weaviate-client',
    '@weaviate/weaviate-ts-client', '@lancedb/lancedb', 'lancedb',
    'tiktoken', 'gpt-tokenizer', '@dqbd/tiktoken', 'js-tiktoken',
    'gpt4all', 'node-llama-cpp', '@node-llama-cpp/node-llama-cpp',
    'promptfoo', '@promptfoo/promptfoo',
    '@azure/openai', '@azure/ai-inference',
    '@aws-sdk/client-bedrock-runtime',
    'elevenlabs', '@elevenlabs/api',
    'assemblyai', '@deepgram/sdk', 'whisper-node',
    '@tensorflow/tfjs', '@tensorflow/tfjs-node',
    'brain.js', 'ml5', 'ml-matrix',
    'langfuse', 'helicone', 'braintrust',
    'zod-gpt', 'instructor',
    'natural', 'compromise', 'wink-nlp',
    'mods', 'llm',
    'agents', 'crewai-js',
}

AI_NPM_PREFIXES = (
    '@anthropic-ai/', '@langchain/', '@ai-sdk/', '@huggingface/',
    '@google-ai/', '@google/generative', '@mistralai/', '@cohere-ai/',
    '@aws-sdk/client-bedrock', '@azure/openai', '@azure/ai-',
    '@pinecone-database/', '@qdrant/', '@weaviate/', '@lancedb/',
    '@llamaindex/', '@fireworks-ai/', '@deepgram/',
)

PYTHON_AI_KEYWORDS = {
    'torch', 'tensorflow', 'transformers', 'langchain', 'llama',
    'openai', 'anthropic', 'autogen', 'crewai', 'llamaindex',
    'llama-index', 'huggingface', 'diffusers', 'sentence-transformers',
    'chromadb', 'faiss', 'tiktoken', 'groq', 'mistralai', 'cohere',
    'litellm', 'guidance', 'dspy', 'langgraph', 'langraph',
    'peft', 'accelerate', 'datasets', 'evaluate', 'trl',
    'vllm', 'ctransformers', 'llmlingua', 'semantic-kernel',
    # 深度学习框架
    'keras', 'pytorch', 'jax', 'flax', 'paddle', 'paddlepaddle',
    'mindspore', 'oneflow', 'mxnet',
    # 经典 ML
    'sklearn', 'scikit', 'xgboost', 'lightgbm', 'catboost',
    'optuna', 'hyperopt',
    # NLP
    'spacy', 'nltk', 'gensim', 'stanza', 'textblob',
    # 计算机视觉
    'opencv', 'albumentations', 'torchvision', 'timm', 'ultralytics',
    'detectron', 'mmdet', 'mmcls', 'clip', 'blip',
    # AI 应用 UI
    'gradio', 'streamlit', 'chainlit', 'fastchat', 'lmflow',
    # 量化 / 推理加速
    'bitsandbytes', 'auto-gptq', 'autoawq', 'auto-awq',
    'ctranslate', 'llama-cpp', 'llama_cpp', 'exllamav2',
    'onnx', 'onnxruntime', 'openvino', 'tensorrt',
    # 云 AI SDK
    'together', 'fireworks', 'replicate', 'vertexai',
    'google-cloud-aiplatform', 'boto3',
    # 部署
    'modal', 'bentoml', 'truss', 'sky', 'skypilot',
    # 实验管理
    'mlflow', 'wandb', 'neptune', 'dvclive', 'clearml',
    # 分布式训练
    'deepspeed', 'apex', 'fairscale', 'megatron', 'nemo',
    'axolotl', 'unsloth',
    # AI 框架 / 控制
    'lmql', 'promptflow', 'outlines', 'instructor', 'marvin',
    'haystack', 'txtai', 'phidata',
    # 评估
    'trulens', 'ragas', 'deepeval', 'prompttools',
    # Agent 框架
    'taskweaver', 'agentscope', 'camel',
    'openinterpreter', 'open-interpreter',
    # 语音
    'whisper', 'pywhisper', 'faster-whisper', 'bark', 'coqui', 'tts',
    # 向量数据库
    'pinecone', 'weaviate', 'qdrant', 'milvus', 'lancedb',
    'pgvector', 'vespa',
    # 可观测性
    'langfuse', 'helicone', 'braintrust',
    # 其他
    'ray', 'dask',
}


def run(cmd, timeout=30, shell=True):
    """执行 shell 命令，返回 stdout 字符串，失败返回空字符串。"""
    try:
        r = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
            shell=shell, encoding='utf-8', errors='ignore'
        )
        return r.stdout.strip()
    except Exception:
        return ''


# ─────────────────────────────────────────────
#  维度 1：应用程序
# ─────────────────────────────────────────────

def scan_apps():
    if PLATFORM == 'Windows':
        return _scan_apps_windows()
    return _scan_apps_macos()


def _scan_apps_macos():
    items = []
    seen = set()

    def parse_mdls(app_path):
        out = run(
            f'mdls -name kMDItemDisplayName -name kMDItemVersion '
            f'-name kMDItemDescription -name kMDItemDateAdded '
            f'-name kMDItemLastUsedDate "{app_path}"',
            timeout=5
        )
        info = {}
        for line in out.splitlines():
            if '=' not in line:
                continue
            k, _, v = line.partition('=')
            k = k.strip()
            v = v.strip().strip('"')
            if v == '(null)':
                v = ''
            if 'Version' in k:
                info['version'] = v
            elif 'Description' in k:
                info['description'] = v
            elif 'DateAdded' in k:
                info['install_date'] = v
            elif 'LastUsedDate' in k:
                info['last_used'] = v
        return info

    for apps_dir in [Path('/Applications'), Path.home() / 'Applications']:
        if not apps_dir.exists():
            continue
        for app in apps_dir.glob('*.app'):
            name = app.stem
            if name in seen:
                continue
            seen.add(name)
            info = parse_mdls(app)
            item = {
                'name': name,
                'version': info.get('version', ''),
                'description': info.get('description', ''),
                'install_date': info.get('install_date', ''),
                'last_used': info.get('last_used', ''),
                'source': str(apps_dir.name),
                'accuracy': 'high',
            }
            if name.lower() in AI_APPS:
                item['is_ai'] = True
            items.append(item)

    # Mac App Store
    mas_out = run('mas list', timeout=10)
    for line in mas_out.splitlines():
        parts = line.split(None, 2)
        if len(parts) >= 2:
            name = parts[1].strip()
            if name not in seen:
                seen.add(name)
                item = {'name': name, 'source': 'MAS', 'accuracy': 'high'}
                if name.lower() in AI_APPS:
                    item['is_ai'] = True
                items.append(item)

    return items


def _scan_apps_windows():
    ps = (
        'Get-ItemProperty '
        '"HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*",'
        '"HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*" '
        '| Select-Object DisplayName,DisplayVersion,Publisher,InstallDate '
        '| Where-Object { $_.DisplayName -ne $null } | ConvertTo-Json'
    )
    out = run(f'powershell -Command "{ps}"', timeout=30)
    try:
        apps = json.loads(out) if out else []
        if isinstance(apps, dict):
            apps = [apps]
        return [
            {
                'name': a.get('DisplayName', ''),
                'version': a.get('DisplayVersion', ''),
                'source': 'Registry',
                'accuracy': 'low',
                **({'is_ai': True} if a.get('DisplayName', '').lower() in AI_APPS else {}),
            }
            for a in apps if a.get('DisplayName')
        ]
    except Exception:
        return []


# ─────────────────────────────────────────────
#  维度 2：终端工具
# ─────────────────────────────────────────────

def _annotate_cli_is_ai(items):
    """根据白名单常量预标注 CLI 工具的 is_ai 字段。"""
    for item in items:
        if 'is_ai' in item:
            continue
        name = item.get('name', '').lower().strip()
        if name in AI_CLI_TOOLS:
            item['is_ai'] = True
            item['ai_multiplier_hint'] = AI_CLI_TOOLS[name]
        elif name in NON_AI_CLI:
            item['is_ai'] = False
        else:
            tokens = set(re.split(r'[-_.]', name))
            if tokens & AI_CLI_KEYWORDS:
                item['is_ai'] = True
                item['ai_multiplier_hint'] = 1.5
    return items


def scan_cli_tools():
    items = []
    seen = set()

    if PLATFORM == 'Darwin':
        # brew formula
        brew_json = run('brew info --json=v2 --installed', timeout=60)
        try:
            data = json.loads(brew_json) if brew_json else {'formulae': []}
            for f in data.get('formulae', []):
                name = f.get('name', '')
                if name and name not in seen:
                    seen.add(name)
                    items.append({
                        'name': name,
                        'version': f.get('versions', {}).get('stable', ''),
                        'description': f.get('desc', ''),
                        'source': 'brew',
                        'accuracy': 'high',
                    })
            for f in data.get('casks', []):
                name = f.get('token', '')
                if name and name not in seen:
                    seen.add(name)
                    items.append({
                        'name': name,
                        'description': f.get('desc', ''),
                        'source': 'brew-cask',
                        'accuracy': 'high',
                    })
        except Exception:
            for line in run('brew list --formula').splitlines():
                name = line.strip()
                if name and name not in seen:
                    seen.add(name)
                    items.append({'name': name, 'source': 'brew', 'accuracy': 'medium'})
    else:
        for cmd, src in [
            ('winget list', 'winget'),
            ('scoop list', 'scoop'),
            ('choco list --local-only', 'choco'),
        ]:
            out = run(cmd, timeout=20)
            for line in out.splitlines()[2:]:
                parts = line.split()
                if parts and parts[0] not in seen:
                    seen.add(parts[0])
                    items.append({'name': parts[0], 'source': src, 'accuracy': 'medium'})

    # PATH executables
    sep = ':' if PLATFORM == 'Darwin' else ';'
    system_paths = {'/usr/bin', '/bin', '/usr/sbin', '/sbin',
                    'C:\\Windows\\System32', 'C:\\Windows'}
    for d in os.environ.get('PATH', '').split(sep):
        if not d or d in system_paths:
            continue
        try:
            for f in Path(d).iterdir():
                if f.is_file() and os.access(f, os.X_OK) and f.name not in seen:
                    seen.add(f.name)
                    items.append({'name': f.name, 'source': 'PATH', 'accuracy': 'medium'})
        except Exception:
            pass

    return _annotate_cli_is_ai(items)


# ─────────────────────────────────────────────
#  维度 3：npm 全局包
# ─────────────────────────────────────────────

def _annotate_npm_is_ai(items):
    """根据白名单预标注 npm 包的 is_ai 字段。"""
    for item in items:
        if 'is_ai' in item:
            continue
        name = item.get('name', '')
        name_lower = name.lower()
        if name in AI_NPM_PACKAGES or name_lower in AI_NPM_PACKAGES:
            item['is_ai'] = True
        elif any(name_lower.startswith(p) for p in AI_NPM_PREFIXES):
            item['is_ai'] = True
        else:
            # 名称中包含 AI 关键词（完整词）
            tokens = set(re.split(r'[-_/.]', name_lower))
            if tokens & {'openai', 'anthropic', 'langchain', 'llama', 'gpt', 'llm',
                         'claude', 'gemini', 'mistral', 'groq', 'ollama', 'cohere',
                         'huggingface', 'transformers', 'embedding', 'vectordb'}:
                item['is_ai'] = True
    return items


def scan_npm_globals():
    out = run('npm list -g --depth=0 --json', timeout=30)
    items = []
    try:
        data = json.loads(out) if out else {}
        npm_root = run('npm root -g', timeout=10)
        for name, info in data.get('dependencies', {}).items():
            version = info.get('version', '')
            description = ''
            if npm_root:
                pkg_path = Path(npm_root) / name / 'package.json'
                if pkg_path.exists():
                    try:
                        pkg = json.loads(pkg_path.read_text(encoding='utf-8', errors='ignore'))
                        description = pkg.get('description', '')
                    except Exception:
                        pass
            items.append({
                'name': name,
                'version': version,
                'description': description,
                'source': 'npm-global',
                'accuracy': 'high',
            })
    except Exception:
        pass
    return _annotate_npm_is_ai(items)


# ─────────────────────────────────────────────
#  维度 4：Skills
# ─────────────────────────────────────────────

def scan_claude_skills():
    skills_dir = Path.home() / '.claude' / 'skills'
    items = []
    if not skills_dir.exists():
        return items

    for skill_dir in skills_dir.iterdir():
        if not skill_dir.is_dir():
            continue
        name = skill_dir.name
        description = ''
        skill_md = skill_dir / 'SKILL.md'
        if skill_md.exists():
            try:
                content = skill_md.read_text(encoding='utf-8', errors='ignore')
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 2:
                        for line in parts[1].splitlines():
                            if line.startswith('name:'):
                                name = line.split(':', 1)[1].strip().strip('"\'')
                            elif line.startswith('description:'):
                                description = line.split(':', 1)[1].strip().strip('"\'')
            except Exception:
                pass
        stat = skill_dir.stat()
        items.append({
            'name': name,
            'description': description,
            'install_date': datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'source': 'claude-skills',
            'accuracy': 'high',
        })
    return items


# ─────────────────────────────────────────────
#  维度 5：模型配置文件
# ─────────────────────────────────────────────

def scan_model_configs():
    home = Path.home()
    configs = []
    seen_models = set()

    SENSITIVE_KEYS = {'key', 'token', 'secret', 'password', 'apikey', 'api_key'}

    def safe_load_json(path):
        """加载 JSON，过滤所有含 key/token/secret/password 的字段。"""
        try:
            raw = json.loads(path.read_text(encoding='utf-8', errors='ignore'))
            if not isinstance(raw, dict):
                return {}
            return {
                k: v for k, v in raw.items()
                if not any(s in k.lower() for s in SENSITIVE_KEYS)
            }
        except Exception:
            return {}

    def add_model(source_name, tool_name, model_value):
        if model_value and isinstance(model_value, str) and model_value not in seen_models:
            seen_models.add(model_value)
            configs.append({'source': source_name, 'tool': tool_name, 'model': model_value})

    if PLATFORM == 'Darwin':
        targets = [
            (home / '.cursor' / 'settings.json', 'Cursor',
             ['cursor.models.chat', 'cursor.general.aiModel', 'cursor.openAIModel']),
            (home / 'Library' / 'Application Support' / 'Code' / 'User' / 'settings.json',
             'VS Code', ['github.copilot.selectedModel', 'continue.defaultModel']),
            (home / '.config' / 'windsurf' / 'settings.json', 'Windsurf', ['model']),
            (home / '.claude' / 'settings.json', 'Claude Code', ['model']),
        ]
    else:
        appdata = Path(os.environ.get('APPDATA', ''))
        targets = [
            (appdata / 'Cursor' / 'User' / 'settings.json', 'Cursor',
             ['cursor.models.chat', 'cursor.general.aiModel']),
            (appdata / 'Code' / 'User' / 'settings.json', 'VS Code',
             ['github.copilot.selectedModel']),
        ]

    for cfg_path, tool, keys in targets:
        if not cfg_path.exists():
            continue
        data = safe_load_json(cfg_path)
        for key in keys:
            # Support nested dot-notation keys
            val = data
            for part in key.split('.'):
                if isinstance(val, dict):
                    val = val.get(part, '')
                else:
                    val = ''
                    break
            add_model(cfg_path.name, tool, val if isinstance(val, str) else '')

    # aider YAML
    aider_conf = home / '.aider.conf.yml'
    if aider_conf.exists():
        try:
            content = aider_conf.read_text(encoding='utf-8', errors='ignore')
            m = re.search(r'^model:\s*(.+)$', content, re.MULTILINE)
            if m:
                add_model('.aider.conf.yml', 'aider', m.group(1).strip())
        except Exception:
            pass

    # fabric config
    fabric_conf = home / '.config' / 'fabric' / 'config.yaml'
    if fabric_conf.exists():
        try:
            content = fabric_conf.read_text(encoding='utf-8', errors='ignore')
            m = re.search(r'^default_model:\s*(.+)$', content, re.MULTILINE)
            if m:
                add_model('config.yaml', 'fabric', m.group(1).strip())
        except Exception:
            pass

    # Continue config.json — models array
    continue_conf = home / '.continue' / 'config.json'
    if continue_conf.exists():
        data = safe_load_json(continue_conf)
        for m in data.get('models', []):
            if isinstance(m, dict):
                add_model('config.json', 'Continue', m.get('model', ''))

    return configs


# ─────────────────────────────────────────────
#  维度 6：Python AI 包
# ─────────────────────────────────────────────

def scan_python_ai_packages():
    items = []
    seen = set()

    def process_pkg_list(pkgs, source):
        for pkg in pkgs:
            raw_name = pkg.get('name', pkg.get('Name', ''))
            name_lower = raw_name.lower().replace('_', '-')
            if any(kw in name_lower for kw in PYTHON_AI_KEYWORDS) and name_lower not in seen:
                seen.add(name_lower)
                description = ''
                show = run(f'pip show "{raw_name}"', timeout=8)
                for line in show.splitlines():
                    if line.startswith('Summary:'):
                        description = line.split(':', 1)[1].strip()
                        break
                items.append({
                    'name': raw_name,
                    'version': pkg.get('version', pkg.get('Version', '')),
                    'description': description,
                    'source': source,
                    'accuracy': 'high',
                    'is_ai': True,
                })

    for cmd in ['pip list --format=json', 'pip3 list --format=json']:
        out = run(cmd, timeout=30)
        if out:
            try:
                process_pkg_list(json.loads(out), 'pip')
                break
            except Exception:
                pass

    # conda
    conda_out = run('conda list --json', timeout=30)
    if conda_out:
        try:
            process_pkg_list(json.loads(conda_out), 'conda')
        except Exception:
            pass

    return items


# ─────────────────────────────────────────────
#  维度 7：IDE AI 插件
# ─────────────────────────────────────────────

def scan_ide_ai_plugins():
    AI_KEYWORDS = {
        'copilot', 'codeium', 'continue', 'tabnine', 'cursor',
        'ai', 'llm', 'gpt', 'claude', 'windsurf', 'sourcegraph',
        'cody', 'supermaven', 'blackbox', 'bito', 'mintlify',
    }
    items = []
    seen = set()

    # VS Code extensions
    if PLATFORM == 'Darwin':
        ext_dir = Path.home() / '.vscode' / 'extensions'
    else:
        ext_dir = Path(os.environ.get('USERPROFILE', '')) / '.vscode' / 'extensions'

    if ext_dir.exists():
        for ext in ext_dir.iterdir():
            if not ext.is_dir():
                continue
            pkg = ext / 'package.json'
            if pkg.exists():
                try:
                    data = json.loads(pkg.read_text(encoding='utf-8', errors='ignore'))
                    name = data.get('displayName', data.get('name', ''))
                    desc = data.get('description', '').lower()
                    publisher = data.get('publisher', '').lower()
                    name_l = name.lower()
                    if any(kw in name_l or kw in desc or kw in publisher
                           for kw in AI_KEYWORDS):
                        uid = f"vscode-{name}"
                        if uid not in seen:
                            seen.add(uid)
                            items.append({
                                'name': name,
                                'version': data.get('version', ''),
                                'description': data.get('description', ''),
                                'publisher': data.get('publisher', ''),
                                'source': 'vscode',
                                'accuracy': 'high',
                            })
                except Exception:
                    pass

    # JetBrains plugins (macOS)
    if PLATFORM == 'Darwin':
        jb_base = Path.home() / 'Library' / 'Application Support' / 'JetBrains'
        if jb_base.exists():
            for ide_dir in jb_base.iterdir():
                plugins_dir = ide_dir / 'plugins'
                if not plugins_dir.exists():
                    continue
                for plugin_dir in plugins_dir.iterdir():
                    xml = plugin_dir / 'META-INF' / 'plugin.xml'
                    if xml.exists():
                        try:
                            content = xml.read_text(encoding='utf-8', errors='ignore')
                            nm = re.search(r'<name>(.*?)</name>', content)
                            dm = re.search(r'<description>(.*?)</description>',
                                           content, re.DOTALL)
                            name = nm.group(1) if nm else plugin_dir.name
                            desc = dm.group(1) if dm else ''
                            if any(kw in name.lower() or kw in desc.lower()
                                   for kw in AI_KEYWORDS):
                                uid = f"jb-{name}"
                                if uid not in seen:
                                    seen.add(uid)
                                    items.append({
                                        'name': name,
                                        'description': re.sub(r'<[^>]+>', '', desc)[:200],
                                        'source': 'jetbrains',
                                        'accuracy': 'high',
                                    })
                        except Exception:
                            pass

    return items


# ─────────────────────────────────────────────
#  维度 8：用户目录 AI 文件夹
# ─────────────────────────────────────────────

def scan_ai_home_folders():
    AI_KEYWORDS = {
        'ai', 'gpt', 'llm', 'claude', 'agent', 'model', 'prompt',
        'rag', 'embedding', 'langchain', 'openai', 'ml', 'diffusion',
        'transformer', 'copilot', 'chatbot',
    }
    home = Path.home()
    items = []
    try:
        for item in home.iterdir():
            if item.is_dir():
                name_l = item.name.lower()
                if any(kw in name_l for kw in AI_KEYWORDS):
                    stat = item.stat()
                    items.append({
                        'name': item.name,
                        'path': str(item),
                        'install_date': datetime.datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        'last_used': datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'source': 'home_folder',
                        'accuracy': 'high',
                    })
    except Exception:
        pass
    return items


# ─────────────────────────────────────────────
#  维度 9：设备硬件
# ─────────────────────────────────────────────

def scan_hardware():
    if PLATFORM == 'Darwin':
        return _scan_hardware_macos()
    return _scan_hardware_windows()


def _scan_hardware_macos():
    hw = {
        'platform': 'macOS',
        'model': '',
        'chip': '',
        'chip_family': 'unknown',
        'chip_tier': 'unknown',
        'cpu_cores': None,
        'gpu_cores': None,
        'ram_gb': None,
        'storage_gb': None,
        'storage_type': 'SSD',
        'gpu_discrete': None,
        'gpu_vram_gb': None,
    }

    sp_hw = run('system_profiler SPHardwareDataType', timeout=15)
    for line in sp_hw.splitlines():
        line = line.strip()
        if line.startswith('Model Name:'):
            hw['model'] = line.split(':', 1)[1].strip()
        elif line.startswith('Chip:'):
            hw['chip'] = line.split(':', 1)[1].strip()
        elif line.startswith('Processor Name:') and not hw['chip']:
            hw['chip'] = line.split(':', 1)[1].strip()
        elif 'Total Number of Cores:' in line and hw['cpu_cores'] is None:
            m = re.search(r'(\d+)', line.split(':', 1)[1])
            if m:
                hw['cpu_cores'] = int(m.group(1))
        elif line.startswith('Memory:'):
            m = re.search(r'(\d+)\s*(GB|TB|MB)', line, re.IGNORECASE)
            if m:
                val, unit = int(m.group(1)), m.group(2).upper()
                hw['ram_gb'] = val * 1024 if unit == 'TB' else (val if unit == 'GB' else val // 1024)

    sp_disp = run('system_profiler SPDisplaysDataType', timeout=10)
    for line in sp_disp.splitlines():
        if 'Total Number of Cores:' in line:
            m = re.search(r'(\d+)', line.split(':', 1)[1])
            if m:
                hw['gpu_cores'] = int(m.group(1))
                break

    df = run('df -H /', timeout=10)
    for line in df.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 2:
            m = re.search(r'(\d+\.?\d*)\s*([GTMK])', parts[1])
            if m:
                val, unit = float(m.group(1)), m.group(2)
                mult = {'T': 1024, 'G': 1, 'M': 0.001, 'K': 0.000001}
                hw['storage_gb'] = int(val * mult.get(unit, 1))
            break

    chip = hw.get('chip', '').lower()
    if 'apple' in chip or any(f' m{i} ' in f' {chip} ' or chip.endswith(f' m{i}')
                              for i in range(1, 7)):
        hw['chip_family'] = 'apple_silicon'
        if 'ultra' in chip:
            hw['chip_tier'] = 'ultra'
        elif 'max' in chip:
            hw['chip_tier'] = 'max'
        elif 'pro' in chip:
            hw['chip_tier'] = 'pro'
        else:
            hw['chip_tier'] = 'base'
    elif 'intel' in chip:
        hw['chip_family'] = 'x86_64'
        if any(x in chip for x in ['i9', 'xeon']):
            hw['chip_tier'] = 'high'
        elif 'i7' in chip:
            hw['chip_tier'] = 'mid_high'
        elif 'i5' in chip:
            hw['chip_tier'] = 'mid'
        else:
            hw['chip_tier'] = 'low'

    return hw


def _scan_hardware_windows():
    hw = {
        'platform': 'Windows',
        'model': 'Custom Build',
        'chip': '',
        'chip_family': 'x86_64',
        'chip_tier': 'unknown',
        'cpu_cores': None,
        'gpu_cores': None,
        'ram_gb': None,
        'storage_gb': None,
        'storage_type': 'SSD',
        'gpu_discrete': None,
        'gpu_vram_gb': None,
    }

    cpu_out = run(
        'powershell -Command "Get-CimInstance Win32_Processor | '
        'Select-Object Name,NumberOfCores | ConvertTo-Json"',
        timeout=15
    )
    try:
        cpu = json.loads(cpu_out) if cpu_out else {}
        if isinstance(cpu, list):
            cpu = cpu[0]
        hw['chip'] = cpu.get('Name', '')
        hw['cpu_cores'] = cpu.get('NumberOfCores', None)
    except Exception:
        pass

    ram_out = run(
        'powershell -Command "[math]::Round((Get-CimInstance Win32_ComputerSystem)'
        '.TotalPhysicalMemory / 1GB, 1)"',
        timeout=10
    )
    try:
        hw['ram_gb'] = int(float(ram_out.strip()))
    except Exception:
        pass

    disk_out = run(
        'powershell -Command "Get-CimInstance Win32_LogicalDisk '
        '-Filter \\"DeviceID=\'C:\'\\" | Select-Object Size | ConvertTo-Json"',
        timeout=10
    )
    try:
        disk = json.loads(disk_out) if disk_out else {}
        if isinstance(disk, list):
            disk = disk[0]
        hw['storage_gb'] = int(disk.get('Size', 0) / 1e9)
    except Exception:
        pass

    gpu_out = run(
        'powershell -Command "Get-CimInstance Win32_VideoController | '
        'Select-Object Name,AdapterRAM | ConvertTo-Json"',
        timeout=10
    )
    try:
        gpus = json.loads(gpu_out) if gpu_out else []
        if isinstance(gpus, dict):
            gpus = [gpus]
        for gpu in gpus:
            name = gpu.get('Name', '')
            if any(x in name.upper() for x in ['NVIDIA', 'AMD', 'RTX', 'GTX', 'RX ']):
                hw['gpu_discrete'] = name
                vram = gpu.get('AdapterRAM', 0)
                hw['gpu_vram_gb'] = round(vram / 1e9, 1) if vram else None
                break
    except Exception:
        pass

    chip = hw.get('chip', '').lower()
    if 'i9' in chip or 'ryzen 9' in chip or 'xeon' in chip:
        hw['chip_tier'] = 'high'
    elif 'i7' in chip or 'ryzen 7' in chip:
        hw['chip_tier'] = 'mid_high'
    elif 'i5' in chip or 'ryzen 5' in chip:
        hw['chip_tier'] = 'mid'
    elif 'i3' in chip or 'ryzen 3' in chip:
        hw['chip_tier'] = 'low'
    else:
        hw['chip_tier'] = 'low'

    # Refine chip_tier based on discrete GPU
    if hw['gpu_discrete']:
        gpu_name = hw['gpu_discrete'].upper()
        if any(x in gpu_name for x in ['4090', '5090', 'A100', 'H100', 'A6000']):
            hw['chip_tier'] = 'flagship_gpu'
        elif any(x in gpu_name for x in ['4080', '5080', '3090']):
            hw['chip_tier'] = 'high_gpu'

    return hw


# ─────────────────────────────────────────────
#  维度 10：网络能力
# ─────────────────────────────────────────────

def scan_network():
    result = {
        'download_mbps': None,
        'latency_openai_ms': None,
        'latency_anthropic_ms': None,
        'reachability': {},
        'vpn_tools': [],
    }

    # 网速测试：依次尝试国内直连节点，取第一个有效结果
    null_path = '/dev/null' if PLATFORM == 'Darwin' else 'NUL'
    speed_urls = [
        # 清华大学镜像站（国内直连，文件约 20MB，限速 10s）
        'https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ls-lR.gz',
        # 中科大镜像站备用
        'https://mirrors.ustc.edu.cn/ubuntu/ls-lR.gz',
        # Cloudflare（代理环境备用）
        'https://speed.cloudflare.com/__down?bytes=5000000',
    ]
    for url in speed_urls:
        try:
            out = run(
                f'curl -o {null_path} -s -w "%{{speed_download}}" '
                '--max-time 10 '
                f'"{url}"',
                timeout=15
            )
            if out:
                bytes_per_sec = float(out.strip())
                if bytes_per_sec > 10000:  # 至少 10KB/s 才算有效结果
                    result['download_mbps'] = round(bytes_per_sec * 8 / 1_000_000, 1)
                    break
        except Exception:
            continue

    # 延迟测试
    for host, key in [
        ('api.openai.com', 'latency_openai_ms'),
        ('api.anthropic.com', 'latency_anthropic_ms'),
    ]:
        try:
            start = time.time()
            s = socket.create_connection((host, 443), timeout=5)
            s.close()
            result[key] = round((time.time() - start) * 1000)
        except Exception:
            result[key] = None

    # 可达性检测
    for host in ['api.openai.com', 'api.anthropic.com', 'generativelanguage.googleapis.com']:
        try:
            socket.setdefaulttimeout(5)
            socket.getaddrinfo(host, 443)
            s = socket.create_connection((host, 443), timeout=5)
            s.close()
            result['reachability'][host] = 'reachable'
        except socket.timeout:
            result['reachability'][host] = 'timeout'
        except Exception:
            result['reachability'][host] = 'blocked'

    # VPN/代理工具检测
    vpn_names = [
        'Clash', 'ClashX', 'Surge', 'Shadowsocks', 'ShadowsocksX-NG',
        'V2RayX', 'QuantumultX', 'Quantumult X', 'sing-box', 'Mullvad VPN',
        'ExpressVPN', 'NordVPN', 'Tunnelbear', 'ProtonVPN', 'WireGuard',
    ]
    found_vpns = []

    if PLATFORM == 'Darwin':
        for vpn in vpn_names:
            for apps_dir in [Path('/Applications'), Path.home() / 'Applications']:
                if (apps_dir / f'{vpn}.app').exists():
                    if vpn not in found_vpns:
                        found_vpns.append(vpn)
        brew_casks = run('brew list --cask', timeout=15).lower()
        for vpn in ['clash', 'clashx', 'surge', 'shadowsocks', 'v2rayx',
                    'mullvad-vpn', 'nordvpn', 'expressvpn', 'protonvpn']:
            if vpn in brew_casks and vpn not in found_vpns:
                found_vpns.append(vpn)
    else:
        for base in ['C:\\Program Files', 'C:\\Program Files (x86)']:
            bp = Path(base)
            if bp.exists():
                try:
                    installed = {d.name.lower() for d in bp.iterdir() if d.is_dir()}
                    for vpn in vpn_names:
                        if vpn.lower() in installed and vpn not in found_vpns:
                            found_vpns.append(vpn)
                except Exception:
                    pass

    result['vpn_tools'] = found_vpns
    return result


# ─────────────────────────────────────────────
#  维度 11：本地模型文件
# ─────────────────────────────────────────────

def scan_local_models():
    MODEL_EXTS = {'.gguf', '.safetensors'}
    LARGE_EXTS = {'.bin', '.pt', '.pth'}
    MIN_LARGE_BYTES = 500 * 1024 * 1024  # 500 MB

    if PLATFORM == 'Darwin':
        home = Path.home()
        search_dirs = [
            (home / '.ollama' / 'models' / 'blobs', 'ollama'),
            (home / '.ollama' / 'models' / 'manifests', 'ollama'),
            (home / '.lmstudio' / 'models', 'lmstudio'),
            (home / '.cache' / 'huggingface' / 'hub', 'huggingface'),
            (home / 'models', 'manual'),
            (home / 'llm', 'manual'),
            (home / 'AI' / 'models', 'manual'),
        ]
    else:
        up = Path(os.environ.get('USERPROFILE', Path.home()))
        search_dirs = [
            (up / '.ollama', 'ollama'),
            (up / 'lm-studio' / 'models', 'lmstudio'),
            (up / '.cache' / 'huggingface' / 'hub', 'huggingface'),
            (up / 'models', 'manual'),
        ]

    items = []
    seen = set()

    for model_dir, source in search_dirs:
        if not model_dir.exists():
            continue
        try:
            for f in model_dir.rglob('*'):
                if not f.is_file():
                    continue
                ext = f.suffix.lower()
                try:
                    size_bytes = f.stat().st_size
                except Exception:
                    continue
                if ext not in MODEL_EXTS and not (ext in LARGE_EXTS and size_bytes >= MIN_LARGE_BYTES):
                    continue
                if f.name in seen:
                    continue
                seen.add(f.name)

                size_gb = size_bytes / 1e9
                # Estimate params from filename
                m = re.search(r'(\d+\.?\d*)b', f.name.lower())
                if m:
                    val = float(m.group(1))
                    params = f'{int(val)}B' if val == int(val) else f'{val}B'
                else:
                    estimated = size_gb / 0.7
                    params = f'~{int(estimated)}B'

                items.append({
                    'name': f.name,
                    'source': source,
                    'size_gb': round(size_gb, 2),
                    'estimated_params': params,
                    'accuracy': 'high',
                })
        except PermissionError:
            pass
        except Exception:
            pass

    return items


# ─────────────────────────────────────────────
#  维度 12：AI API Key 配置
# ─────────────────────────────────────────────

def scan_api_keys():
    """SECURITY: 只检测 key 名称存在性，绝不读取或存储 key 值。"""
    AI_KEY_NAMES = [
        'OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GEMINI_API_KEY',
        'COHERE_API_KEY', 'GROQ_API_KEY', 'DEEPSEEK_API_KEY',
        'MISTRAL_API_KEY', 'MOONSHOT_API_KEY', 'ZHIPUAI_API_KEY',
        'DASHSCOPE_API_KEY', 'SPARK_API_KEY', 'GOOGLE_API_KEY',
        'AZURE_OPENAI_API_KEY', 'TOGETHER_API_KEY', 'PERPLEXITY_API_KEY',
        'REPLICATE_API_TOKEN', 'STABILITY_API_KEY', 'HUGGING_FACE_HUB_TOKEN',
        'VOYAGE_API_KEY', 'COHERE_API_KEY',
    ]

    detected = []
    sources = []

    # 环境变量 — 只检测存在性
    env_found = [k for k in AI_KEY_NAMES if k in os.environ]
    if env_found:
        detected.extend(env_found)
        sources.append('env')

    # 配置文件 — 只匹配 key 名称，不读取 key 值
    # 模式：行首有 UPPER_CASE_KEY = 或 UPPER_CASE_KEY:，后跟任意值
    KEY_NAME_PATTERN = re.compile(
        r'^([A-Z][A-Z0-9_]{3,}(?:API_KEY|_KEY|TOKEN|SECRET))\s*[=:]\s*.+',
        re.MULTILINE
    )

    config_files = [
        Path.home() / '.env',
        Path.home() / '.env.local',
        Path(os.environ.get('APPDATA', '')) / '.env' if PLATFORM == 'Windows' else Path('/dev/null'),
    ]

    for cfg in config_files:
        if not cfg.exists() or not cfg.is_file():
            continue
        try:
            content = cfg.read_text(encoding='utf-8', errors='ignore')
            for m in KEY_NAME_PATTERN.finditer(content):
                key_name = m.group(1)
                if key_name in AI_KEY_NAMES and key_name not in detected:
                    detected.append(key_name)
                    src = str(cfg.name)
                    if src not in sources:
                        sources.append(src)
        except Exception:
            pass

    return {'detected': detected, 'sources': sources}


# ─────────────────────────────────────────────
#  维度 13（新增）：环境变量 AI 配置
# ─────────────────────────────────────────────

def scan_env_ai_config():
    """扫描 shell 配置文件和当前环境变量中的 AI 相关变量，脱敏处理。"""
    AI_KEYWORDS = [
        'openai', 'anthropic', 'claude', 'gemini', 'groq', 'mistral',
        'deepseek', 'dashscope', 'qwen', 'tongyi', 'zhipu', 'moonshot',
        'spark', 'together', 'perplexity', 'replicate', 'huggingface',
        'hf_', 'langchain', 'ollama', 'litellm', 'cohere', 'stability',
        'ai_', 'api_key', 'llm_', 'model_', 'chatgpt', 'copilot',
        'cursor', 'vllm', 'llama', 'whisper', 'tiktoken', 'dify', 'dify_',
    ]

    SHELL_RC_FILES = [
        Path.home() / '.zshrc',
        Path.home() / '.bashrc',
        Path.home() / '.bash_profile',
        Path.home() / '.zprofile',
        Path.home() / '.profile',
    ]

    EXPORT_PATTERN = re.compile(
        r'^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+?)\s*$',
        re.MULTILINE
    )

    def is_ai_var(name):
        name_l = name.lower()
        return any(kw in name_l for kw in AI_KEYWORDS)

    def mask_value(name, value):
        """脱敏：路径保留，URL 保留域名，key 只留前4字符。"""
        # 路径类型
        if '/' in value or '\\' in value:
            return value
        # URL 类型
        if value.startswith(('http://', 'https://')):
            try:
                from urllib.parse import urlparse
                parsed = urlparse(value)
                return f'{parsed.scheme}://{parsed.netloc}'
            except Exception:
                return value[:30] + '***'
        # Key / token 类型
        if len(value) > 4:
            return value[:4] + '***'
        return '***'

    items = []
    seen_names = set()

    # 1. 读取 shell 配置文件
    for rc_file in SHELL_RC_FILES:
        if not rc_file.exists() or not rc_file.is_file():
            continue
        try:
            content = rc_file.read_text(encoding='utf-8', errors='ignore')
            for m in EXPORT_PATTERN.finditer(content):
                var_name = m.group(1)
                var_value = m.group(2).strip().strip('"').strip("'")
                if not is_ai_var(var_name):
                    continue
                dedup_key = (var_name, str(rc_file.name))
                if dedup_key in seen_names:
                    continue
                seen_names.add(dedup_key)
                items.append({
                    'name': var_name,
                    'value_hint': mask_value(var_name, var_value),
                    'source_file': rc_file.name,
                    'is_ai': True,
                })
        except Exception:
            pass

    # 2. 读取当前进程环境变量
    for var_name, var_value in os.environ.items():
        if not is_ai_var(var_name):
            continue
        dedup_key = (var_name, 'env')
        if dedup_key in seen_names:
            continue
        seen_names.add(dedup_key)
        items.append({
            'name': var_name,
            'value_hint': mask_value(var_name, var_value),
            'source_file': 'env',
            'is_ai': True,
        })

    return items


# ─────────────────────────────────────────────
#  维度 14：浏览器 AI 插件
# ─────────────────────────────────────────────

def scan_browser_ai_plugins():
    AI_KEYWORDS = {
        'ai', 'gpt', 'claude', 'copilot', 'translate', 'chatbot',
        'chatgpt', 'gemini', 'perplexity', 'monica', 'sider', 'merlin',
        'immersive', 'openai', 'kimi', 'wenxin', 'doubao',
    }
    items = []
    seen = set()

    if PLATFORM == 'Darwin':
        ext_bases = [
            (Path.home() / 'Library' / 'Application Support' / 'Google' / 'Chrome' / 'Default' / 'Extensions', 'Chrome'),
            (Path.home() / 'Library' / 'Application Support' / 'Microsoft Edge' / 'Default' / 'Extensions', 'Edge'),
            (Path.home() / 'Library' / 'Application Support' / 'BraveSoftware' / 'Brave-Browser' / 'Default' / 'Extensions', 'Brave'),
        ]
        ff_profiles_base = Path.home() / 'Library' / 'Application Support' / 'Firefox' / 'Profiles'
    else:
        appdata = os.environ.get('APPDATA', '')
        ext_bases = [
            (Path(appdata) / 'Google' / 'Chrome' / 'User Data' / 'Default' / 'Extensions', 'Chrome'),
            (Path(appdata) / 'Microsoft' / 'Edge' / 'User Data' / 'Default' / 'Extensions', 'Edge'),
        ]
        ff_profiles_base = Path(appdata) / 'Mozilla' / 'Firefox' / 'Profiles'

    for ext_base, browser in ext_bases:
        if not ext_base.exists():
            continue
        for ext_id in ext_base.iterdir():
            if not ext_id.is_dir():
                continue
            for ver_dir in sorted(ext_id.iterdir(), reverse=True):
                manifest = ver_dir / 'manifest.json'
                if manifest.exists():
                    try:
                        data = json.loads(manifest.read_text(encoding='utf-8', errors='ignore'))
                        name = data.get('name', '')
                        if name.startswith('__MSG_'):
                            break
                        desc = data.get('description', '').lower()
                        uid = f"{browser}-{ext_id.name}"
                        if uid not in seen and any(kw in name.lower() or kw in desc
                                                   for kw in AI_KEYWORDS):
                            seen.add(uid)
                            items.append({
                                'name': name,
                                'browser': browser,
                                'description': data.get('description', '')[:200],
                                'version': data.get('version', ''),
                                'accuracy': 'high',
                            })
                    except Exception:
                        pass
                    break

    # Firefox
    if ff_profiles_base.exists():
        for profile in ff_profiles_base.iterdir():
            ext_dir = profile / 'extensions'
            if ext_dir.exists():
                for ext in ext_dir.iterdir():
                    name = ext.stem
                    if name not in seen and any(kw in name.lower() for kw in AI_KEYWORDS):
                        seen.add(name)
                        items.append({'name': name, 'browser': 'Firefox', 'accuracy': 'medium'})

    return items


# ─────────────────────────────────────────────
#  维度 14：Docker AI 镜像
# ─────────────────────────────────────────────

def scan_docker_ai_images():
    AI_IMAGE_KEYWORDS = {
        'ollama', 'localai', 'comfyui', 'stable-diffusion', 'vllm',
        'llama', 'whisper', 'text-generation', 'huggingface', 'transformers',
        'pytorch', 'tensorflow', 'nvidia/cuda', 'rocm', 'triton',
        'tgi', 'infinity', 'fastchat', 'llm-server',
    }

    out = run('docker images --format "{{.Repository}}:{{.Tag}}\t{{.Size}}"', timeout=15)
    items = []
    if not out:
        return items

    for line in out.splitlines():
        if '\t' not in line:
            continue
        name_tag, size = line.split('\t', 1)
        name_l = name_tag.lower()
        if any(kw in name_l for kw in AI_IMAGE_KEYWORDS):
            items.append({
                'name': name_tag,
                'size': size.strip(),
                'accuracy': 'high',
            })

    return items


# ─────────────────────────────────────────────
#  维度 15：Jupyter Notebook
# ─────────────────────────────────────────────

def scan_jupyter():
    result = {
        'installed': False,
        'notebook_count': 0,
        'kernels': [],
        'ai_imports_detected': [],
    }

    which_cmd = 'which jupyter' if PLATFORM == 'Darwin' else 'where jupyter'
    result['installed'] = bool(run(which_cmd, timeout=5))

    if result['installed']:
        kernels_out = run('jupyter kernelspec list --json', timeout=10)
        try:
            kdata = json.loads(kernels_out) if kernels_out else {}
            result['kernels'] = list(kdata.get('kernelspecs', {}).keys())
        except Exception:
            pass

    home = Path.home()
    AI_IMPORTS = {
        'torch', 'tensorflow', 'transformers', 'openai', 'anthropic',
        'langchain', 'sklearn', 'keras', 'huggingface_hub', 'diffusers',
        'llama_index', 'chromadb', 'groq', 'cohere', 'litellm',
    }

    find_cmd = (
        f'find "{home}" -name "*.ipynb" '
        '-not -path "*/node_modules/*" -not -path "*/.git/*" '
        '-maxdepth 5'
        if PLATFORM == 'Darwin'
        else f'dir /s /b "{home}\\*.ipynb"'
    )

    notebook_paths = []
    try:
        out = run(find_cmd, timeout=15)
        notebook_paths = [p.strip() for p in out.splitlines() if p.strip()]
        result['notebook_count'] = len(notebook_paths)
    except Exception:
        pass

    import_counts = {}
    for nb_path in notebook_paths[:10]:
        try:
            nb_data = json.loads(Path(nb_path).read_text(encoding='utf-8', errors='ignore'))
            for cell in nb_data.get('cells', []):
                if cell.get('cell_type') == 'code':
                    source = ''.join(cell.get('source', []))
                    for ai_import in AI_IMPORTS:
                        if f'import {ai_import}' in source or f'from {ai_import}' in source:
                            import_counts[ai_import] = import_counts.get(ai_import, 0) + 1
        except Exception:
            pass

    result['ai_imports_detected'] = list(import_counts.keys())
    return result


# ─────────────────────────────────────────────
#  主函数
# ─────────────────────────────────────────────

DIMENSIONS = [
    ('apps',                '应用程序',       scan_apps),
    ('cli_tools',           '终端工具',        scan_cli_tools),
    ('npm_globals',         'npm 全局包',      scan_npm_globals),
    ('claude_skills',       'Skills',          scan_claude_skills),
    ('model_configs',       '模型配置文件',    scan_model_configs),
    ('python_ai_packages',  'Python AI 包',    scan_python_ai_packages),
    ('ide_ai_plugins',      'IDE AI 插件',     scan_ide_ai_plugins),
    ('ai_home_folders',     'AI 文件夹',       scan_ai_home_folders),
    ('hardware',            '设备硬件',        scan_hardware),
    ('network',             '网络能力',        scan_network),
    ('local_models',        '本地模型文件',    scan_local_models),
    ('api_keys',            'API Key 配置',    scan_api_keys),
    ('env_ai_config',       '环境变量 AI 配置', scan_env_ai_config),
    ('browser_ai_plugins',  '浏览器 AI 插件', scan_browser_ai_plugins),
    ('docker_ai_images',    'Docker AI 镜像', scan_docker_ai_images),
    ('jupyter',             'Jupyter',         scan_jupyter),
]


def main():
    print('[ai-level-skill] 开始扫描设备 AI 能力...')
    print(f'[ai-level-skill] 平台: {PLATFORM}，共 {len(DIMENSIONS)} 个扫描维度\n')
    t0 = time.time()

    result = {
        'platform': PLATFORM,
        'collected_at': datetime.datetime.now().isoformat(),
    }

    completed = {}
    lock = __import__('threading').Lock()

    def scan_one(key, label, fn):
        try:
            data = fn()
            with lock:
                count = len(data) if isinstance(data, list) else '✓'
                print(f'  [✓] {label:<20} {count}')
            return key, data
        except Exception as e:
            with lock:
                print(f'  [✗] {label:<20} 跳过（{e}）')
            return key, [] if key not in ('hardware', 'network', 'api_keys', 'jupyter') else {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        futures = {ex.submit(scan_one, key, label, fn): key
                   for key, label, fn in DIMENSIONS}
        for future in concurrent.futures.as_completed(futures):
            key, data = future.result()
            result[key] = data

    out_path = OUTPUT_DIR / 'raw_data.json'
    out_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )

    elapsed = round(time.time() - t0, 1)
    print(f'\n[ai-level-skill] 扫描完成，耗时 {elapsed}s')
    print(f'[ai-level-skill] 输出文件: {out_path}')


if __name__ == '__main__':
    main()
