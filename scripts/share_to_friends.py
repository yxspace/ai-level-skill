#!/usr/bin/env python3
"""Share flow: generate share card PNG -> upload to sm.ms -> generate QR code.

Steps:
  1. Call generate_share_card.py to create share_card.png
  2. Upload PNG to sm.ms image bed (no API key needed)
  3. Generate QR code image for the sm.ms URL
  4. Print the image URL and QR code in terminal
  5. Return the image URL so report.html can embed it
"""

import json
import os
import subprocess
import sys
import urllib.request
import urllib.error
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
OUTPUT_DIR = Path.cwd() / 'output'
PNG_FILE = OUTPUT_DIR / 'share_card.png'
QRCODE_FILE = OUTPUT_DIR / 'qrcode.png'
URL_FILE = OUTPUT_DIR / 'share_url.txt'

SM_MS_UPLOAD_URL = 'https://sm.ms/api/v2/upload'
SM_MS_MAX_SIZE_MB = 5  # sm.ms free tier limit


def log(tag, msg):
    print(f"[{tag}] {msg}")


# ─── Step 1: Generate share card PNG ─────────────────────────────────

def generate_share_card():
    """Run generate_share_card.py and return the PNG path on success."""
    script = SKILL_DIR / 'scripts' / 'generate_share_card.py'
    if not script.exists():
        log("share", f"脚本不存在: {script}")
        return None

    try:
        result = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode != 0:
            log("share", f"分享卡片生成失败: {result.stderr.strip()}")
            return None
    except Exception as exc:
        log("share", f"分享卡片生成异常: {exc}")
        return None

    if PNG_FILE.exists():
        size_mb = PNG_FILE.stat().st_size / (1024 * 1024)
        log("share", f"分享卡片已生成: {PNG_FILE} ({size_mb:.1f} MB)")
        if size_mb > SM_MS_MAX_SIZE_MB:
            log("share", f"警告: 文件超过 {SM_MS_MAX_SIZE_MB}MB 限制，上传可能失败")
        return str(PNG_FILE)

    log("share", "分享卡片 PNG 未生成")
    return None


# ─── Step 2: Upload to sm.ms ─────────────────────────────────────────

def upload_to_sm_ms(image_path):
    """Upload share card image. Tries sm.ms first, falls back to Netlify deployment."""
    if not image_path or not os.path.exists(image_path):
        log("share", "图片文件不存在，跳过上传")
        return None

    # Try sm.ms with requests library
    try:
        import requests as req_lib
        log("share", "正在上传到 sm.ms 图床...")
        with open(image_path, 'rb') as f:
            resp = req_lib.post(
                SM_MS_UPLOAD_URL,
                files={'smfile': (os.path.basename(image_path), f, 'image/png')},
                headers={'User-Agent': 'AI-Level-Skill/1.0'},
                timeout=60,
                allow_redirects=True,
            )
        resp_data = resp.json()
        if resp_data.get('success'):
            image_url = resp_data['data']['url']
            delete_url = resp_data['data'].get('delete', '')
            log("share", f"sm.ms 上传成功: {image_url}")
            _save_url(image_url, delete_url)
            return image_url
        else:
            msg = resp_data.get('message', '未知错误')
            log("share", f"sm.ms 上传失败: {msg}")
            if 'data' in resp_data and isinstance(resp_data['data'], dict) and 'url' in resp_data['data']:
                url = resp_data['data']['url']
                _save_url(url)
                return url
    except Exception as exc:
        log("share", f"sm.ms 上传异常: {exc}")

    # Fallback: deploy as HTML page to Netlify
    return _deploy_to_netlify(image_path)


def _save_url(image_url, delete_url=''):
    with open(URL_FILE, 'w', encoding='utf-8') as f:
        f.write(image_url + '\n')
        if delete_url:
            f.write(delete_url + '\n')


def _deploy_to_netlify(image_path=None):
    """Deploy report.html directly to Netlify."""
    log("share", "正在部署海报到 Netlify...")

    report_html = OUTPUT_DIR / 'report.html'
    if not report_html.exists():
        log("share", f"report.html 不存在: {report_html}")
        return None

    deploy_dir = OUTPUT_DIR / 'share_deploy'
    deploy_dir.mkdir(parents=True, exist_ok=True)

    # report.html already has the save button embedded by generate_report.py
    content = report_html.read_text(encoding='utf-8')
    (deploy_dir / 'index.html').write_text(content, encoding='utf-8')

    try:
        result = subprocess.run(
            ['netlify', 'deploy', '--dir', str(deploy_dir), '--prod', '--message', 'AI Level Share Poster'],
            capture_output=True, text=True, timeout=120,
        )
        for line in result.stdout.split('\n'):
            if 'Production URL:' in line:
                url = line.split('Production URL:')[1].strip().strip('<>').strip()
                if url.startswith('http'):
                    log("share", f"Netlify 部署成功: {url}")
                    _save_url(url)
                    return url
        log("share", f"Netlify 部署输出未找到 URL: {result.stdout[:200]}")
        return None
    except Exception as exc:
        log("share", f"Netlify 部署异常: {exc}")
        return None


# ─── Step 3: Generate QR code ────────────────────────────────────────

def _try_install_qrcode():
    try:
        import qrcode  # noqa: F401
        return True
    except ImportError:
        pass
    try:
        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install', 'qrcode[pil]'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        import qrcode  # noqa: F401
        return True
    except Exception:
        return False


def generate_qrcode(url):
    """Generate QR code image and ASCII for terminal. Returns (ascii_qr, png_path, success)."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not _try_install_qrcode():
        log("share", "qrcode 库不可用，跳过二维码生成")
        return None, None, False

    try:
        import qrcode
        from qrcode.constants import ERROR_CORRECT_M

        qr = qrcode.QRCode(
            version=None,
            error_correction=ERROR_CORRECT_M,
            box_size=10,
            border=2,
        )
        qr.add_data(url)
        qr.make(fit=True)

        # Terminal output: 2 rows per line with half-block chars to compensate
        # for terminal char aspect ratio (~2:1 height:width)
        matrix = qr.get_matrix()
        rows = len(matrix)
        cols = len(matrix[0])
        lines = []
        for y in range(0, rows, 2):
            line = []
            for x in range(cols):
                top = matrix[y][x]
                bot = matrix[y + 1][x] if y + 1 < rows else False
                if top and bot:
                    line.append('█')
                elif top:
                    line.append('▀')
                elif bot:
                    line.append('▄')
                else:
                    line.append(' ')
            lines.append(''.join(line))
        ascii_qr = '\n'.join(lines)

        # Save PNG
        img = qr.make_image(fill_color='black', back_color='white')
        img = img.resize((400, 400))
        img.save(str(QRCODE_FILE))

        return ascii_qr, str(QRCODE_FILE), True

    except Exception as exc:
        log("share", f"二维码生成失败: {exc}")
        return None, None, False


# ─── Main ────────────────────────────────────────────────────────────

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Deploy report.html directly to Netlify (consistent with the poster)
    share_url = _deploy_to_netlify()
    if not share_url:
        log("share", "部署失败，流程终止")
        return None

    # Generate QR code
    ascii_qr, qr_path, qr_ok = generate_qrcode(share_url)

    # Output
    print()
    print(f"  分享海报链接: {share_url}")

    if qr_ok and QRCODE_FILE.exists():
        print(f"  二维码已保存: {QRCODE_FILE}")

    # Display ASCII QR code
    if ascii_qr:
        print()
        width = max(len(line) for line in ascii_qr.split('\n'))
        border = '─' * (width + 2)
        print('┌' + border + '┐')
        for line in ascii_qr.split('\n'):
            print(f'│ {line:<{width}} │')
        print('└' + border + '┘')
        print()
        print("  扫码打开海报，点击「保存图片」分享到朋友圈")
    else:
        print()
        print(f"  请手动访问: {share_url}")

    return share_url


if __name__ == '__main__':
    result = main()
    if result:
        # Write URL so generate_report.py can pick it up
        url_marker = OUTPUT_DIR / 'share_image_url.txt'
        url_marker.write_text(result, encoding='utf-8')

        # Regenerate report.html to embed QR code at the bottom
        report_script = SKILL_DIR / 'scripts' / 'generate_report.py'
        try:
            subprocess.run(
                [sys.executable, str(report_script)],
                capture_output=True, text=True, timeout=60,
            )
            log("share", "已将二维码嵌入 report.html 底部")
        except Exception as exc:
            log("share", f"report.html 更新失败（可手动重新运行 generate_report.py）: {exc}")
