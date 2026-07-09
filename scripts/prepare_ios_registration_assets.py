#!/usr/bin/env python3
"""Generate repo-side iOS App Store Connect registration assets.

The generated screenshots are draft product-page candidates for the
Training-only iOS shell. They intentionally avoid claiming production DB
connectivity or hosted service behavior.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ICON = ROOT / "ios/App/App/Assets.xcassets/AppIcon.appiconset/AppIcon-512@2x.png"
OUT = ROOT / "app_store_assets/ios-registration"


FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/System/Library/Fonts/Supplemental/Helvetica.ttf",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/Library/Fonts/Arial.ttf",
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if bold:
        bold_candidates = [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/Library/Fonts/Arial Bold.ttf",
        ]
        for candidate in bold_candidates:
            if Path(candidate).exists():
                return ImageFont.truetype(candidate, size=size)
    for candidate in FONT_CANDIDATES:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont, max_width: int) -> str:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        trial = " ".join([*current, word])
        bbox = draw.textbbox((0, 0), trial, font=fnt)
        if bbox[2] - bbox[0] <= max_width or not current:
            current.append(word)
        else:
            lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return "\n".join(lines)


def draw_multiline(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fnt: ImageFont.ImageFont,
    fill: str,
    max_width: int,
    spacing: int = 12,
) -> int:
    wrapped = wrap(draw, text, fnt, max_width)
    draw.multiline_text(xy, wrapped, font=fnt, fill=fill, spacing=spacing)
    bbox = draw.multiline_textbbox(xy, wrapped, font=fnt, spacing=spacing)
    return bbox[3]


def gradient_background(width: int, height: int) -> Image.Image:
    img = Image.new("RGB", (width, height), "#071019")
    px = img.load()
    for y in range(height):
        for x in range(width):
            t = (x / width) * 0.42 + (y / height) * 0.58
            r = int(7 + 10 * t)
            g = int(16 + 28 * t)
            b = int(25 + 35 * t)
            px[x, y] = (r, g, b)
    return img


def card(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], fill: str, outline: str = "#244058") -> None:
    draw.rounded_rectangle(xy, radius=26, fill=fill, outline=outline, width=2)


def status_bar(draw: ImageDraw.ImageDraw, width: int, margin: int) -> None:
    small = font(30)
    draw.text((margin, margin), "9:41", font=small, fill="#dce8f2")
    draw.rounded_rectangle((width - margin - 180, margin + 6, width - margin - 12, margin + 34), radius=12, outline="#dce8f2", width=3)
    draw.rounded_rectangle((width - margin - 170, margin + 12, width - margin - 36, margin + 28), radius=8, fill="#67e8c4")
    draw.rounded_rectangle((width - margin - 8, margin + 14, width - margin, margin + 26), radius=4, fill="#dce8f2")


def terminal_ui(draw: ImageDraw.ImageDraw, left: int, top: int, right: int, bottom: int, mode_label: str, command: str, result: str) -> None:
    card(draw, (left, top, right, bottom), "#0d1b27")
    draw.rounded_rectangle((left + 34, top + 30, left + 58, top + 54), radius=12, fill="#ff6b6b")
    draw.rounded_rectangle((left + 72, top + 30, left + 96, top + 54), radius=12, fill="#f6c65b")
    draw.rounded_rectangle((left + 110, top + 30, left + 134, top + 54), radius=12, fill="#67e8c4")
    draw.text((left + 34, top + 92), mode_label, font=font(34, bold=True), fill="#f4fbff")
    draw.text((left + 34, top + 150), "> " + command, font=font(30), fill="#67e8c4")
    draw.rounded_rectangle((left + 34, top + 220, right - 34, bottom - 34), radius=20, fill="#101f2d", outline="#1f3447", width=2)
    draw_multiline(draw, (left + 62, top + 252), result, font(31), "#d6e5f0", right - left - 124, spacing=14)


def screenshot(device: str, size: tuple[int, int], title: str, subtitle: str, command: str, result: str, output: Path) -> None:
    width, height = size
    img = gradient_background(width, height)
    draw = ImageDraw.Draw(img)
    margin = max(54, int(width * 0.055))
    status_bar(draw, width, margin)

    y = int(height * 0.105)
    draw.text((margin, y), "CoQuery Training", font=font(int(width * 0.044), bold=True), fill="#67e8c4")
    y += int(height * 0.055)
    y = draw_multiline(draw, (margin, y), title, font(int(width * 0.07), bold=True), "#f6fbff", width - margin * 2, spacing=18)
    y += int(height * 0.022)
    y = draw_multiline(draw, (margin, y), subtitle, font(int(width * 0.033)), "#b8cad8", width - margin * 2, spacing=12)

    badge_y = y + int(height * 0.035)
    badge_h = int(height * 0.052)
    badges = ["Training Mode", "Sample Data", "No Production DB"]
    x = margin
    for badge in badges:
        w = int(draw.textlength(badge, font=font(int(width * 0.027), bold=True))) + 44
        draw.rounded_rectangle((x, badge_y, x + w, badge_y + badge_h), radius=badge_h // 2, fill="#102c3a", outline="#275a70", width=2)
        draw.text((x + 22, badge_y + int(badge_h * 0.24)), badge, font=font(int(width * 0.027), bold=True), fill="#dff8ff")
        x += w + 18

    ui_top = badge_y + badge_h + int(height * 0.04)
    ui_bottom = height - margin - int(height * 0.055)
    terminal_ui(
        draw,
        margin,
        ui_top,
        width - margin,
        ui_bottom,
        device,
        command,
        result,
    )

    footer = "First TestFlight scope: bundled SQL practice only"
    draw.text((margin, height - margin - 20), footer, font=font(int(width * 0.025)), fill="#7f98aa")
    output.parent.mkdir(parents=True, exist_ok=True)
    img.save(output, "PNG", optimize=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    icon_dir = OUT / "icons"
    icon_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SOURCE_ICON, icon_dir / "app-icon-1024.png")

    scenes = [
        (
            "01-training-home.png",
            "Learn SQL without connecting a real database",
            "CoQuery Training opens in a local practice shell, so first testers can inspect commands safely before any production workflow exists.",
            "practice_list",
            "3 SQL basics problems ready\n- Select customers\n- Filter regions\n- Review attempts",
        ),
        (
            "02-practice-flow.png",
            "Practice with bundled sample data",
            "Run read-only SELECT statements against the included sql_basics pack and compare results without accounts, API keys, or server setup.",
            "practice_grade basic_select_customers",
            "Result: needs review\nHint: include id, name, and region\nAttempt saved locally on device",
        ),
        (
            "03-safety-boundary.png",
            "Training first, production access blocked",
            "The first iPhone build is not a production DB client. Production Assist remains reviewed, read-only, and outside the iOS Training release.",
            "production_review",
            "Blocked in iOS Training shell\nNo production credentials requested\nNo Python local server embedded",
        ),
    ]

    specs = {
        "iphone-69": ("iPhone 6.9 display", (1320, 2868)),
        "ipad-13": ("iPad 13 display", (2048, 2732)),
    }

    generated: list[dict[str, object]] = []
    for folder, (label, size) in specs.items():
        for filename, title, subtitle, command, result in scenes:
            path = OUT / "screenshots" / folder / filename
            screenshot(label, size, title, subtitle, command, result, path)
            generated.append(
                {
                    "kind": "screenshot",
                    "device": label,
                    "size": list(size),
                    "path": str(path.relative_to(ROOT)),
                    "source": "Generated from CoQuery Training first-TestFlight scope.",
                }
            )

    manifest = {
        "generated_at": "2026-07-09",
        "app_name": "CoQuery Training",
        "bundle_id": "app.coquery.training",
        "scope": "TestFlight-first Training Mode registration assets",
        "icon": {
            "path": str((icon_dir / "app-icon-1024.png").relative_to(ROOT)),
            "size": [1024, 1024],
            "source": str(SOURCE_ICON.relative_to(ROOT)),
        },
        "screenshots": generated,
        "not_included": [
            "Apple Developer team signing assets",
            "Hosted privacy/support URLs",
            "Archived .ipa upload",
            "Device-captured screenshots after signing",
        ],
    }
    (OUT / "asset-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared iOS registration assets at {OUT}")


if __name__ == "__main__":
    main()
