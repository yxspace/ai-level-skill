#!/usr/bin/env python3
"""Read score_result.json, generate a desensitized 9:16 share card PNG using Pillow."""

import json
import math
import os
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
OUTPUT_DIR = Path.cwd() / 'output'

# ── Dimension metadata (same keys as score_result.json) ──
DIMENSION_META = {
    'apps':               ('应用程序'),
    'cli_tools':          ('终端工具'),
    'npm_globals':        ('npm 全局包'),
    'claude_skills':      ('Claude Skills'),
    'model_configs':      ('模型配置'),
    'python_ai_packages': ('Python AI 包'),
    'ide_ai_plugins':     ('IDE AI 插件'),
    'ai_home_folders':    ('AI 文件夹'),
    'hardware':           ('设备硬件'),
    'network':            ('网络能力'),
    'local_models':       ('本地模型'),
    'api_keys':           ('API Key'),
    'browser_ai_plugins': ('浏览器插件'),
    'docker_ai_images':   ('Docker AI'),
    'jupyter':            ('Jupyter'),
    'env_ai_config':      ('环境变量'),
}

ACH_COLORS = {
    'SSR': '#FFD700',
    'SR':  '#BF5FFF',
    'R':   '#00FFF0',
}

ACH_BG = {
    'SSR': (40, 35, 10),
    'SR':  (30, 15, 45),
    'R':   (10, 35, 35),
}

# ── Color palette ──
BG = (10, 10, 15)
BG_DARK = (6, 6, 12)
CYAN = (0, 255, 240)
PURPLE = (191, 95, 255)
ORANGE = (255, 107, 53)
GREEN = (0, 255, 136)
WHITE = (224, 224, 224)
MUTED = (136, 136, 136)
DIM_MUTED = (100, 100, 110)
CARD_BG = (15, 15, 26)
DIVIDER = (0, 255, 240, 40)


def _ensure_pillow():
    try:
        from PIL import Image, ImageDraw, ImageFont  # noqa: F401
        return True
    except ImportError:
        pass
    log("share_card", "Pillow 不可用，尝试安装...")
    try:
        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install', 'Pillow'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        from PIL import Image, ImageDraw, ImageFont  # noqa: F401
        return True
    except Exception as exc:
        log("share_card", f"Pillow 安装失败: {exc}")
        return False


def log(tag, msg):
    print(f"[{tag}] {msg}")


def _get_font(size, bold=False):
    """Try to find a suitable font, falling back to default."""
    from PIL import ImageFont
    font_names = []
    if sys.platform == 'darwin':
        font_names = [
            '/System/Library/Fonts/STHeiti Medium.ttc',
            '/System/Library/Fonts/PingFang.ttc',
            '/System/Library/Fonts/Helvetica.ttc',
            '/Library/Fonts/Arial Unicode.ttf',
        ]
    elif sys.platform == 'win32':
        font_names = [
            'C:/Windows/Fonts/msyh.ttc',
            'C:/Windows/Fonts/simhei.ttf',
            'C:/Windows/Fonts/arial.ttf',
        ]
    else:
        font_names = [
            '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        ]

    for name in font_names:
        if os.path.exists(name):
            try:
                return ImageFont.truetype(name, size)
            except Exception:
                continue

    # PIL default
    try:
        return ImageFont.truetype("DejaVuSans", size)
    except Exception:
        return ImageFont.load_default()


def _draw_rounded_rect(draw, xy, radius, fill=None, outline=None, width=1):
    """Draw a rounded rectangle."""
    x0, y0, x1, y1 = xy
    r = min(radius, (x1 - x0) // 2, (y1 - y0) // 2)

    # Fill
    if fill:
        draw.rectangle([x0 + r, y0, x1 - r, y1], fill=fill)
        draw.rectangle([x0, y0 + r, x1, y1 - r], fill=fill)
        draw.pieslice([x0, y0, x0 + 2*r, y0 + 2*r], 180, 270, fill=fill)
        draw.pieslice([x1 - 2*r, y0, x1, y0 + 2*r], 270, 360, fill=fill)
        draw.pieslice([x0, y1 - 2*r, x0 + 2*r, y1], 90, 180, fill=fill)
        draw.pieslice([x1 - 2*r, y1 - 2*r, x1, y1], 0, 90, fill=fill)

    # Outline
    if outline:
        draw.arc([x0, y0, x0 + 2*r, y0 + 2*r], 180, 270, fill=outline, width=width)
        draw.arc([x1 - 2*r, y0, x1, y0 + 2*r], 270, 360, fill=outline, width=width)
        draw.arc([x0, y1 - 2*r, x0 + 2*r, y1], 90, 180, fill=outline, width=width)
        draw.arc([x1 - 2*r, y1 - 2*r, x1, y1], 0, 90, fill=outline, width=width)
        draw.line([x0 + r, y0, x1 - r, y0], fill=outline, width=width)
        draw.line([x0 + r, y1, x1 - r, y1], fill=outline, width=width)
        draw.line([x0, y0 + r, x0, y1 - r], fill=outline, width=width)
        draw.line([x1, y0 + r, x1, y1 - r], fill=outline, width=width)


def _draw_radar(img, cx, cy, radius, labels, values, max_val):
    """Draw a radar chart on the image using PIL. Operates on an RGBA image."""
    from PIL import Image, ImageDraw

    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    n = len(labels)
    if n < 3:
        return

    def angle(i):
        return (i / n) * 2 * math.pi - math.pi / 2

    def point(i, scale):
        a = angle(i)
        return (cx + radius * scale * math.cos(a), cy + radius * scale * math.sin(a))

    # Grid rings
    for scale in [0.2, 0.4, 0.6, 0.8, 1.0]:
        pts = [point(i, scale) for i in range(n)]
        pts.append(pts[0])
        for j in range(n):
            draw.line([pts[j], pts[j+1]], fill=(0, 255, 240, 30), width=1)

    # Spokes
    for i in range(n):
        px, py = point(i, 1.0)
        draw.line([(cx, cy), (px, py)], fill=(0, 255, 240, 20), width=1)

    # Data polygon
    pts = []
    for i in range(n):
        v = values[i] / max_val if max_val > 0 else 0
        v = min(v, 1.0)
        pts.append(point(i, v))

    # Fill
    if len(pts) >= 3:
        flat = []
        for p in pts:
            flat.extend(p)
        draw.polygon(flat, fill=(0, 255, 240, 40))

    # Outline + dots
    for i in range(n):
        j = (i + 1) % n
        draw.line([pts[i], pts[j]], fill=CYAN, width=2)
    for p in pts:
        draw.ellipse([p[0]-4, p[1]-4, p[0]+4, p[1]+4], fill=CYAN)

    # Labels
    font_label = _get_font(16)
    for i in range(n):
        a = angle(i)
        lx = cx + (radius + 28) * math.cos(a)
        ly = cy + (radius + 28) * math.sin(a)
        draw.text((lx, ly), labels[i], fill=MUTED, font=font_label, anchor='mm')

    # Composite overlay onto image
    composited = Image.alpha_composite(img, overlay)
    img.paste(composited)


def _draw_gradient_line(draw, y, width, x_offset=0, height=2):
    """Draw a horizontal gradient line (cyan -> purple)."""
    for x in range(width):
        t = x / max(width - 1, 1)
        r = int(CYAN[0] * (1-t) + PURPLE[0] * t)
        g = int(CYAN[1] * (1-t) + PURPLE[1] * t)
        b = int(CYAN[2] * (1-t) + PURPLE[2] * t)
        for dy in range(height):
            draw.point((x_offset + x, y + dy), fill=(r, g, b))


def generate():
    if not _ensure_pillow():
        log("share_card", "Pillow 不可用，无法生成分享卡片 PNG")
        return None

    from PIL import Image, ImageDraw, ImageFont

    score_path = OUTPUT_DIR / 'score_result.json'
    with open(score_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    user_name = data.get('user_name', '')
    total_score = data.get('total_score', 0)
    title = data.get('title', '')
    scores = data.get('dimension_scores', {})
    achievements = data.get('rare_achievements', [])
    highlights = data.get('highlights', [])

    # ── Card dimensions ──
    W, H = 1080, 1920
    PAD = 60
    CARD_W = W - 2 * PAD

    img = Image.new('RGBA', (W, H), BG)
    draw = ImageDraw.Draw(img)

    # ── Fonts ──
    font_score = _get_font(96, bold=True)
    font_title = _get_font(36, bold=True)
    font_name = _get_font(24)
    font_section = _get_font(22, bold=True)
    font_body = _get_font(20)
    font_small = _get_font(18)
    font_ach_level = _get_font(16, bold=True)
    font_ach_title = _get_font(18)
    font_bar_score = _get_font(16)
    font_footer = _get_font(16)

    y = PAD

    # ── Hero section: gradient bg ──
    hero_h = 320
    for row in range(hero_h):
        t = row / hero_h
        r = int(BG[0] * (1-t) + 20 * t)
        g = int(BG[1] * (1-t) + 10 * t)
        b = int(BG[2] * (1-t) + 40 * t)
        draw.line([(0, row), (W, row)], fill=(r, g, b))

    # ── Total score ──
    y = PAD + 30
    score_str = f"{total_score:,}"
    bbox = draw.textbbox((0, 0), score_str, font=font_score)
    sw = bbox[2] - bbox[0]
    draw.text(((W - sw) // 2, y), score_str, fill=CYAN, font=font_score)
    y += bbox[3] - bbox[1] + 16

    # ── Title ──
    bbox = draw.textbbox((0, 0), title, font=font_title)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, y), title, fill=CYAN, font=font_title)
    y += bbox[3] - bbox[1] + 12

    # ── User name ──
    if user_name:
        name_str = user_name
        bbox = draw.textbbox((0, 0), name_str, font=font_name)
        nw = bbox[2] - bbox[0]
        draw.text(((W - nw) // 2, y), name_str, fill=MUTED, font=font_name)
        y += bbox[3] - bbox[1] + 8

    # ── Gradient divider ──
    y = PAD + hero_h - 20
    _draw_gradient_line(draw, y, W, x_offset=int(W * 0.1), height=2)

    y = PAD + hero_h + 20

    # ── Radar chart (only scored dimensions) ──
    scored_dims = []
    for k in DIMENSION_META:
        s = scores.get(k, {}).get('score', 0)
        if s > 0:
            scored_dims.append((k, DIMENSION_META[k], s))

    if len(scored_dims) >= 3:
        # Section label
        draw.text((PAD, y), "能  力  雷  达", fill=PURPLE, font=font_section)
        y += 40

        radar_labels = [d[1] for d in scored_dims]
        radar_values = [d[2] for d in scored_dims]
        max_val = max(radar_values) if radar_values else 1

        radar_radius = 160
        radar_cx = W // 2
        radar_cy = y + radar_radius + 10
        _draw_radar(img, radar_cx, radar_cy, radar_radius,
                     radar_labels, radar_values, max_val)
        draw = ImageDraw.Draw(img)  # Recreate draw after alpha_composite
        y = radar_cy + radar_radius + 50
    elif scored_dims:
        # Fallback: show as bar list if < 3 dimensions
        draw.text((PAD, y), "维  度  得  分", fill=PURPLE, font=font_section)
        y += 40

    # ── Top dimensions bar chart ──
    dim_items = []
    for k in DIMENSION_META:
        s = scores.get(k, {}).get('score', 0)
        if s > 0:
            dim_items.append((DIMENSION_META[k], s))
    dim_items.sort(key=lambda x: x[1], reverse=True)

    draw.text((PAD, y), "维  度  得  分" if len(scored_dims) < 3 else "Top  维  度", fill=PURPLE, font=font_section)
    y += 40

    top_dims = dim_items[:7]
    max_score = top_dims[0][1] if top_dims else 1
    bar_w = CARD_W - 200
    for label, score in top_dims:
        pct = score / max_score if max_score > 0 else 0
        # Label
        draw.text((PAD, y), label, fill=WHITE, font=font_body)
        # Bar background
        bar_x = PAD + 160
        bar_h = 18
        _draw_rounded_rect(draw, (bar_x, y + 2, bar_x + bar_w, y + 2 + bar_h),
                           radius=9, fill=(30, 30, 50))
        # Bar fill (gradient effect)
        fill_w = int(bar_w * pct)
        for bx in range(fill_w):
            t = bx / max(fill_w - 1, 1)
            r = int(CYAN[0] * (1-t) + PURPLE[0] * t)
            g = int(CYAN[1] * (1-t) + PURPLE[1] * t)
            b = int(CYAN[2] * (1-t) + PURPLE[2] * t)
            for dy in range(bar_h):
                draw.point((bar_x + bx, y + 2 + dy), fill=(r, g, b))
        # Score
        draw.text((PAD + CARD_W - 80, y), f"{score:,}", fill=CYAN, font=font_bar_score)
        y += 38

    y += 10

    # ── Rare achievements ──
    if achievements:
        draw.text((PAD, y), "稀  有  成  就", fill=PURPLE, font=font_section)
        y += 40

        for ach in achievements[:4]:
            level = ach.get('level', 'R')
            ach_title = ach.get('title', '')
            # Desensitize: omit the 'tool' field which may contain specific names
            color = tuple(int(ACH_COLORS.get(level, '#00FFF0').lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            bg_color = ACH_BG.get(level, (10, 35, 35))

            card_h = 52
            _draw_rounded_rect(draw, (PAD, y, PAD + CARD_W, y + card_h),
                               radius=10, fill=bg_color, outline=color, width=1)

            # Level badge
            badge_w = 44
            badge_h = 26
            bx = PAD + 12
            by = y + (card_h - badge_h) // 2
            _draw_rounded_rect(draw, (bx, by, bx + badge_w, by + badge_h),
                               radius=6, fill=color)
            bbox = draw.textbbox((0, 0), level, font=font_ach_level)
            lw = bbox[2] - bbox[0]
            lh = bbox[3] - bbox[1]
            draw.text((bx + (badge_w - lw) // 2, by + (badge_h - lh) // 2 - 2),
                      level, fill=(0, 0, 0), font=font_ach_level)

            # Title
            draw.text((PAD + 68, y + 14), ach_title, fill=WHITE, font=font_ach_title)
            y += card_h + 10

        y += 10

    # ── Highlights ──
    if highlights:
        draw.text((PAD, y), "亮  点", fill=PURPLE, font=font_section)
        y += 40

        for h in highlights[:5]:
            # Green dot
            dot_r = 5
            draw.ellipse([PAD + 4, y + 6, PAD + 4 + 2*dot_r, y + 6 + 2*dot_r], fill=GREEN)
            # Text with line wrapping
            max_chars_per_line = 28
            text = str(h)
            lines = [text[i:i+max_chars_per_line] for i in range(0, len(text), max_chars_per_line)]
            for li, line in enumerate(lines):
                draw.text((PAD + 22, y + li * 26), line, fill=WHITE, font=font_body)
            y += len(lines) * 26 + 12

        y += 10

    # ── Footer ──
    footer_y = H - 80
    _draw_gradient_line(draw, footer_y - 10, W, x_offset=int(W * 0.1), height=1)
    footer_text = "AI 能力侧写 · 扫码查看完整报告"
    bbox = draw.textbbox((0, 0), footer_text, font=font_footer)
    fw = bbox[2] - bbox[0]
    draw.text(((W - fw) // 2, footer_y), footer_text, fill=DIM_MUTED, font=font_footer)

    # ── Save ──
    out_path = OUTPUT_DIR / 'share_card.png'
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    # Convert RGBA back to RGB for PNG (no transparency needed in final output)
    final_img = Image.new('RGB', img.size, BG)
    final_img.paste(img, mask=img.split()[3] if img.mode == 'RGBA' else None)
    final_img.save(str(out_path), 'PNG', optimize=True)

    size_kb = out_path.stat().st_size / 1024
    log("share_card", f"分享卡片 PNG: {out_path} ({size_kb:.0f} KB)")
    return str(out_path)


if __name__ == '__main__':
    result = generate()
    if result:
        print(f"Share card generated: {result}")
    else:
        print("Failed to generate share card")
        sys.exit(1)
