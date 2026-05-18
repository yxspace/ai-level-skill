#!/usr/bin/env python3
"""将 raw_data.json 拆分为 5 个子代理评分组"""

import json
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
OUTPUT_DIR = Path.cwd() / 'output'


def main():
    raw_path = OUTPUT_DIR / 'raw_data.json'
    if not raw_path.exists():
        print(f'[split_data] 错误: {raw_path} 不存在，请先运行 collector.py')
        return

    raw = json.loads(raw_path.read_text(encoding='utf-8'))

    slices = {
        'slice_ui': {
            'apps':               raw.get('apps', []),
            'browser_ai_plugins': raw.get('browser_ai_plugins', []),
            'ide_ai_plugins':     raw.get('ide_ai_plugins', []),
        },
        'slice_dev': {
            'cli_tools':          raw.get('cli_tools', []),
            'npm_globals':        raw.get('npm_globals', []),
            'claude_skills':      raw.get('claude_skills', []),
            'python_ai_packages': raw.get('python_ai_packages', []),
            'env_ai_config':      raw.get('env_ai_config', []),
        },
        'slice_model': {
            'model_configs':      raw.get('model_configs', []),
            'api_keys':           raw.get('api_keys', {}),
            'local_models':       raw.get('local_models', []),
            'docker_ai_images':   raw.get('docker_ai_images', []),
        },
        'slice_practice': {
            'jupyter':            raw.get('jupyter', {}),
            'ai_home_folders':    raw.get('ai_home_folders', []),
        },
        'slice_infra': {
            'hardware':           raw.get('hardware', {}),
            'network':            raw.get('network', {}),
        },
    }

    for name, data in slices.items():
        out_path = OUTPUT_DIR / f'{name}.json'
        out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        size_kb = round(out_path.stat().st_size / 1024, 1)
        print(f'  [✓] {name}.json  ({size_kb} KB)')

    print('\n[split_data] 拆分完成')


if __name__ == '__main__':
    main()
