#!/usr/bin/env python3
"""Merge 5 partial_score_*.json files into score_result.json.

This script handles the mechanical parts of Step 5 deterministically so models
don't have to manually parse and merge JSON (which is error-prone):
  - Sums group_total to get total_score
  - Merges dimension_scores (handles both dict and int formats from models)
  - Normalizes rare_achievements to {level, title, tool, copy}
  - Deduplicates achievements (keep highest level per tool)
  - Determines title from total_score
  - Generates roadmap if actions are missing
  - Writes score_result.json

After this script runs, the model only needs to fill in highlights, weaknesses,
and roadmap.phases[*].actions (three semantic fields).
"""
import json
import os
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
OUTPUT_DIR = Path.cwd() / 'output'

TITLE_MAP = [
    (10000, 'AI 极客'),
    (6000,  'AI 超级用户'),
    (3000,  'AI 工程师'),
    (1500,  'AI 进阶玩家'),
    (800,   'AI 实践者'),
    (300,   'AI 尝鲜者'),
    (0,     'AI 初探者'),
]

ROADMAP = {
    'AI 极客': {
        'next_level': '（已达顶级）',
        'phases': [
            {'phase': 1, 'title': '近期（1-2 个月）', 'actions': [
                '尝试 LoRA/QLoRA 微调开源模型，在本地数据集上跑通训练流程',
                '参与一个 AI 相关开源项目，贡献 PR 或文档',
                '用 LangGraph 或 AutoGen 构建一个多智能体协作 demo',
            ]},
            {'phase': 2, 'title': '中期（3-6 个月）', 'actions': [
                '搭建私有 RAG 知识库，接入至少 3 个不同来源的数据',
                '部署本地推理服务（vLLM / llama.cpp），对外提供 API',
                '系统学习 AI 安全与对齐基础知识',
            ]},
            {'phase': 3, 'title': '长期（6 个月以上）', 'actions': [
                '发表一篇 AI 工程实践相关的技术文章或开源项目',
                '探索多模态模型（视觉 + 语言）在实际业务中的落地',
                '研究 AI Agent 在生产环境的可靠性与可观测性',
            ]},
        ],
    },
    'AI 超级用户': {
        'next_level': 'AI 极客',
        'phases': [
            {'phase': 1, 'title': '近期（1-2 个月）', 'actions': [
                '在本地运行 34B+ 开源模型（LM Studio 或 ollama）',
                '学习 LoRA 微调基础，在小数据集上完成一次微调实验',
                '配置 Jupyter Notebook 并运行至少一个 AI 训练 notebook',
            ]},
            {'phase': 2, 'title': '中期（3-6 个月）', 'actions': [
                '用 LangChain 或 LlamaIndex 构建一个完整的 RAG 应用',
                '接入至少两个不同厂商的 AI API，构建对比测试工具',
                '用 Docker 部署一个 AI 推理服务',
            ]},
            {'phase': 3, 'title': '长期（6 个月以上）', 'actions': [
                '完成从数据准备到训练到部署的完整 AI 项目',
                '研究并实践 AI Agent 框架（AutoGen / CrewAI）',
                '参与 AI 相关竞赛或开源社区',
            ]},
        ],
    },
    'AI 工程师': {
        'next_level': 'AI 超级用户',
        'phases': [
            {'phase': 1, 'title': '近期（1-2 个月）', 'actions': [
                '安装 PyTorch，跑通官方入门 demo',
                '注册并调用至少 3 个 AI API（OpenAI / Anthropic / 国内厂商）',
                '安装 ollama，在本地运行一个 7B 级别的开源模型',
            ]},
            {'phase': 2, 'title': '中期（3-6 个月）', 'actions': [
                '用 LangChain 构建一个简单的问答应用',
                '学习 Prompt Engineering 最佳实践',
                '在 Jupyter 中完成一个完整的数据分析 + AI 推理 notebook',
            ]},
            {'phase': 3, 'title': '长期（6 个月以上）', 'actions': [
                '尝试微调一个小型语言模型',
                '部署自己的 AI Web 应用到云端',
                '探索 AI Agent 在自动化工作流中的应用',
            ]},
        ],
    },
    'AI 进阶玩家': {
        'next_level': 'AI 工程师',
        'phases': [
            {'phase': 1, 'title': '近期（1-2 个月）', 'actions': [
                '安装 Python，学习调用 openai 或 anthropic 包',
                '注册并使用至少两个 AI API',
                '尝试用 aider 或 claude-code 进行 AI 辅助编程',
            ]},
            {'phase': 2, 'title': '中期（3-6 个月）', 'actions': [
                '学习 LangChain 基础，构建一个简单的 AI 应用',
                '尝试安装 ollama 并在本地运行小模型',
                '系统学习 Prompt Engineering',
            ]},
            {'phase': 3, 'title': '长期（6 个月以上）', 'actions': [
                '构建并部署第一个完整的 AI Web 应用',
                '学习 PyTorch 基础，了解模型推理原理',
                '探索向量数据库与 RAG 应用开发',
            ]},
        ],
    },
}

DEFAULT_ROADMAP = {
    'next_level': 'AI 进阶玩家',
    'phases': [
        {'phase': 1, 'title': '近期（1-2 个月）', 'actions': [
            '安装 Cursor 或 Windsurf，体验 AI 辅助编程',
            '注册 Claude 或 ChatGPT，开始在日常工作中使用 AI',
            '安装 claude-code CLI，尝试 AI 终端编程',
        ]},
        {'phase': 2, 'title': '中期（3-6 个月）', 'actions': [
            '安装 Python，学习使用 openai 包调用 AI API',
            '尝试安装 ollama，在本地运行开源模型',
            '学习 Prompt Engineering 基础',
        ]},
        {'phase': 3, 'title': '长期（6 个月以上）', 'actions': [
            '构建第一个完整的 AI 应用',
            '学习 LangChain 或 LlamaIndex 框架',
            '探索 AI 在你当前工作领域的具体落地方向',
        ]},
    ],
}


def get_title(score):
    for threshold, title in TITLE_MAP:
        if score >= threshold:
            return title
    return 'AI 初探者'


def extract_dim_score(val):
    """Extract (score, items) from a dimension value regardless of format."""
    if isinstance(val, (int, float)):
        return int(val), []
    if isinstance(val, dict):
        score = val.get('score') or val.get('total_score') or val.get('final_score') or 0
        items = val.get('items', [])
        return int(score), items
    return 0, []


def normalize_achievement(a):
    """Normalize to {level, title, tool, copy}. Return None if unusable."""
    if not isinstance(a, dict):
        return None
    level = a.get('level', 'R')
    if level not in ('R', 'SR', 'SSR'):
        return None
    title = a.get('title') or a.get('name') or ''
    tool  = a.get('tool')  or a.get('name') or ''
    copy_ = a.get('copy')  or a.get('description') or ''
    if not title:
        return None
    return {'level': level, 'title': title, 'tool': tool, 'copy': copy_}


def _try_repair_json(text):
    """Attempt lightweight repairs on common model JSON output issues."""
    import re
    # Remove BOM
    text = text.lstrip('﻿')
    # Strip trailing commas before ] or }
    text = re.sub(r',\s*([}\]])', r'\1', text)
    return text


def load_json(path):
    text = path.read_text(encoding='utf-8')
    try:
        return json.loads(text)
    except json.JSONDecodeError as first_err:
        # Try lightweight repair
        try:
            return json.loads(_try_repair_json(text))
        except json.JSONDecodeError:
            pass
        print(f"[merge] 警告: {path.name} JSON 解析失败 ({first_err})")
        print(f"[merge]   该文件内容可能含未转义的特殊字符，跳过此分组（不影响其他分组）")
        return None


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # ── Load partial scores ──────────────────────────────────────────
    files = {
        'ui':       OUTPUT_DIR / 'partial_score_ui.json',
        'dev':      OUTPUT_DIR / 'partial_score_dev.json',
        'model':    OUTPUT_DIR / 'partial_score_model.json',
        'practice': OUTPUT_DIR / 'partial_score_practice.json',
        'infra':    OUTPUT_DIR / 'partial_score_infra.json',
    }

    missing = [k for k, p in files.items() if not p.exists()]
    if missing:
        print(f"[merge] 警告: 以下分组文件不存在，跳过: {missing}")

    parts = {}
    for k, p in files.items():
        if not p.exists():
            continue
        result = load_json(p)
        if result is not None:
            parts[k] = result
        # None means parse failed — already logged, just skip

    if not parts:
        print("[merge] 错误: 所有 partial_score_*.json 均无法解析，无法继续。")
        sys.exit(1)

    # ── Sum total score ──────────────────────────────────────────────
    total_score = sum(p.get('group_total', 0) for p in parts.values())
    title = get_title(total_score)

    # ── Merge dimension_scores ───────────────────────────────────────
    dimension_scores = {}
    for part in parts.values():
        for dim, val in part.get('dimension_scores', {}).items():
            score, items = extract_dim_score(val)
            if dim not in dimension_scores:
                dimension_scores[dim] = {'score': score, 'items': items}
            else:
                # Accumulate if already present (shouldn't happen, but safe)
                dimension_scores[dim]['score'] += score
                dimension_scores[dim]['items'].extend(items)

    # Ensure all 15 expected dimensions exist
    expected = [
        'apps', 'cli_tools', 'npm_globals', 'claude_skills', 'model_configs',
        'python_ai_packages', 'ide_ai_plugins', 'ai_home_folders', 'hardware',
        'network', 'local_models', 'api_keys', 'browser_ai_plugins',
        'docker_ai_images', 'jupyter', 'env_ai_config',
    ]
    for dim in expected:
        dimension_scores.setdefault(dim, {'score': 0, 'items': []})

    # ── Merge rare_achievements ──────────────────────────────────────
    level_rank = {'SSR': 3, 'SR': 2, 'R': 1}
    seen = {}  # key -> achievement
    for part in parts.values():
        for a in part.get('rare_achievements', []):
            norm = normalize_achievement(a)
            if not norm:
                continue
            key = (norm['tool'] or norm['title']).lower()
            existing = seen.get(key)
            if not existing or level_rank.get(norm['level'], 0) > level_rank.get(existing['level'], 0):
                seen[key] = norm

    achievements = sorted(seen.values(), key=lambda x: level_rank.get(x['level'], 0), reverse=True)

    # ── Compute highlights and weaknesses from dimension_scores ──────
    scored = [(dim, v['score']) for dim, v in dimension_scores.items()]
    scored.sort(key=lambda x: x[1], reverse=True)

    dim_labels = {
        'apps': '应用程序', 'cli_tools': '终端 CLI 工具', 'npm_globals': 'npm 全局包',
        'claude_skills': 'AI Skills', 'model_configs': '模型配置',
        'python_ai_packages': 'Python AI 包', 'ide_ai_plugins': 'IDE AI 插件',
        'ai_home_folders': 'AI 文件夹', 'hardware': '设备硬件', 'network': '网络能力',
        'local_models': '本地模型文件', 'api_keys': 'AI API Key',
        'browser_ai_plugins': '浏览器 AI 插件', 'docker_ai_images': 'Docker AI 镜像',
        'jupyter': 'Jupyter Notebook', 'env_ai_config': '环境变量 AI 配置',
    }

    highlights = [
        f"在 {dim_labels.get(dim, dim)} 方面表现突出，得分 {s}"
        for dim, s in scored[:3] if s > 0
    ]
    weaknesses = [
        f"{dim_labels.get(dim, dim)} 方面有待提升"
        for dim, s in scored if s == 0
    ][:3]

    # ── Preserve existing user_name if score_result.json exists ──────
    user_name = ''
    result_path = OUTPUT_DIR / 'score_result.json'
    if result_path.exists():
        try:
            existing = load_json(result_path)
            user_name = existing.get('user_name', '')
            # If model already wrote non-empty highlights/weaknesses/roadmap, preserve them
            ext_highlights = existing.get('highlights', [])
            ext_weaknesses = existing.get('weaknesses', [])
            ext_roadmap = existing.get('roadmap', {})
            if ext_highlights:
                highlights = ext_highlights
            if ext_weaknesses:
                weaknesses = ext_weaknesses
        except Exception:
            ext_roadmap = {}
    else:
        ext_roadmap = {}

    # ── Build roadmap ────────────────────────────────────────────────
    rm_template = ROADMAP.get(title, DEFAULT_ROADMAP)
    # Check if existing roadmap has actions filled in
    existing_phases = ext_roadmap.get('phases', [])
    has_actions = any(p.get('actions') for p in existing_phases if isinstance(p, dict))
    if has_actions:
        roadmap_phases = existing_phases
        next_level = ext_roadmap.get('next_level', rm_template['next_level'])
    else:
        roadmap_phases = rm_template['phases']
        next_level = rm_template['next_level']

    # ── Write score_result.json ──────────────────────────────────────
    result = {
        'user_name': user_name,
        'total_score': total_score,
        'title': title,
        'dimension_scores': dimension_scores,
        'rare_achievements': achievements,
        'highlights': highlights,
        'weaknesses': weaknesses,
        'roadmap': {
            'current_level': title,
            'next_level': next_level,
            'phases': roadmap_phases,
        },
    }

    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # ── Summary ──────────────────────────────────────────────────────
    print(f"[merge] 合并完成")
    print(f"[merge] 总分: {total_score}  称号: {title}")
    print(f"[merge] 维度: {len(dimension_scores)} 个")
    print(f"[merge] 稀有成就: {len(achievements)} 个")
    for a in achievements:
        print(f"[merge]   [{a['level']}] {a['title']}")
    print(f"[merge] score_result.json → {result_path}")

    # Print what the model still needs to fill in
    print()
    print("[merge] 脚本已完成机械合并。")
    print("[merge] 请模型根据 score_result.json 完成以下语义性内容（可选优化）：")
    print("[merge]   - highlights: 用一两句话描述得分最高维度的亮点")
    print("[merge]   - weaknesses: 描述短板维度的建议")
    print("[merge]   - roadmap.phases[*].actions: 结合当前具体工具情况优化学习建议")


if __name__ == '__main__':
    main()
