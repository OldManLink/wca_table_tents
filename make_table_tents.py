from PIL import Image, ImageDraw, ImageFont
import os
import subprocess
import re
import csv
import sys

PAGE_W, PAGE_H = 3508, 2480  # A4 landscape @300 DPI
FOLD_Y = PAGE_H // 2

OUT_DIR = "table_tents"
os.makedirs(OUT_DIR, exist_ok=True)


def load_font(size, bold=False):
    candidates = []

    if bold:
        candidates += [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/Library/Fonts/Arial Bold.ttf",
        ]

    candidates += [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]

    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass

    try:
        name = "Arial Bold" if bold else "Arial"
        path = subprocess.check_output(
            ["fc-match", "-f", "%{file}", name],
            text=True
        ).strip()
        if path:
            return ImageFont.truetype(path, size)
    except Exception:
        pass

    return ImageFont.load_default()


def draw_flag(draw, code, x, y, w, h):
    code = code.upper()

    if code == "SE":
        draw.rectangle([x, y, x + w, y + h], fill="#006AA7")
        draw.rectangle([x + w * 0.29, y, x + w * 0.43, y + h], fill="#FECC00")
        draw.rectangle([x, y + h * 0.40, x + w, y + h * 0.60], fill="#FECC00")

    elif code == "NO":
        draw.rectangle([x, y, x + w, y + h], fill="#BA0C2F")
        draw.rectangle([x + w * 0.27, y, x + w * 0.45, y + h], fill="white")
        draw.rectangle([x, y + h * 0.36, x + w, y + h * 0.64], fill="white")
        draw.rectangle([x + w * 0.32, y, x + w * 0.40, y + h], fill="#00205B")
        draw.rectangle([x, y + h * 0.43, x + w, y + h * 0.57], fill="#00205B")

    elif code == "DK":
        draw.rectangle([x, y, x + w, y + h], fill="#C8102E")
        draw.rectangle([x + w * 0.30, y, x + w * 0.42, y + h], fill="white")
        draw.rectangle([x, y + h * 0.42, x + w, y + h * 0.58], fill="white")

    elif code == "FI":
        draw.rectangle([x, y, x + w, y + h], fill="white")
        draw.rectangle([x + w * 0.28, y, x + w * 0.44, y + h], fill="#002F6C")
        draw.rectangle([x, y + h * 0.38, x + w, y + h * 0.62], fill="#002F6C")

    elif code == "IE":
        draw.rectangle([x, y, x + w / 3, y + h], fill="#169B62")
        draw.rectangle([x + w / 3, y, x + 2 * w / 3, y + h], fill="white")
        draw.rectangle([x + 2 * w / 3, y, x + w, y + h], fill="#FF883E")

    elif code in ("GB", "UK"):
        draw.rectangle([x, y, x + w, y + h], fill="#012169")

        # White diagonals
        draw.polygon(
            [
                (x, y),
                (x + w * 0.10, y),
                (x + w, y + h * 0.82),
                (x + w, y + h),
                (x + w * 0.90, y + h),
                (x, y + h * 0.18),
            ],
            fill="white",
        )
        draw.polygon(
            [
                (x + w, y),
                (x + w, y + h * 0.18),
                (x + w * 0.10, y + h),
                (x, y + h),
                (x, y + h * 0.82),
                (x + w * 0.90, y),
            ],
            fill="white",
        )

        # Red diagonals
        draw.polygon(
            [
                (x, y),
                (x + w * 0.055, y),
                (x + w, y + h * 0.86),
                (x + w, y + h),
                (x + w * 0.945, y + h),
                (x, y + h * 0.14),
            ],
            fill="#C8102E",
        )
        draw.polygon(
            [
                (x + w, y),
                (x + w, y + h * 0.14),
                (x + w * 0.055, y + h),
                (x, y + h),
                (x, y + h * 0.86),
                (x + w * 0.945, y),
            ],
            fill="#C8102E",
        )

        # White cross
        draw.rectangle([x + w * 0.40, y, x + w * 0.60, y + h], fill="white")
        draw.rectangle([x, y + h * 0.36, x + w, y + h * 0.64], fill="white")

        # Red cross
        draw.rectangle([x + w * 0.45, y, x + w * 0.55, y + h], fill="#C8102E")
        draw.rectangle([x, y + h * 0.43, x + w, y + h * 0.57], fill="#C8102E")

    elif code == "DE":
        draw.rectangle([x, y, x + w, y + h / 3], fill="black")
        draw.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill="#DD0000")
        draw.rectangle([x, y + 2 * h / 3, x + w, y + h], fill="#FFCE00")

    elif code == "LT":
        draw.rectangle([x, y, x + w, y + h / 3], fill="#FDB913")
        draw.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill="#006A44")
        draw.rectangle([x, y + 2 * h / 3, x + w, y + h], fill="#C1272D")

    elif code == "CH":
        draw.rectangle([x, y, x + w, y + h], fill="#DA291C")
        cx = x + w / 2
        cy = y + h / 2
        draw.rectangle([cx - w * 0.09, cy - h * 0.27, cx + w * 0.09, cy + h * 0.27], fill="white")
        draw.rectangle([cx - w * 0.27, cy - h * 0.09, cx + w * 0.27, cy + h * 0.09], fill="white")

    elif code == "HU":
        draw.rectangle([x, y, x + w, y + h / 3], fill="#CE2939")
        draw.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill="white")
        draw.rectangle([x, y + 2 * h / 3, x + w, y + h], fill="#477050")

    else:
        draw.rectangle([x, y, x + w, y + h], outline="black", width=4)
        font = load_font(80)
        draw.text((x + w / 2, y + h / 2), code, font=font, anchor="mm", fill="black")


def wrap_name(draw, name, font, max_width):
    words = name.split()
    lines = []
    current = ""

    for word in words:
        test = word if not current else current + " " + word
        if draw.textlength(test, font=font) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines


def extract_event_name(csv_path):
    filename = os.path.basename(csv_path)
    name, _ = os.path.splitext(filename)

    # Megaminx_seeds.csv -> Megaminx
    # 6x6_seeds.csv      -> 6x6
    # Clock_seeds.csv    -> Clock
    event = re.sub(r"_seeds$", "", name, flags=re.IGNORECASE)

    # Optional nicety: Megaminx_Final_seeds.csv -> Megaminx Final
    event = event.replace("_", " ").strip()

    return event


def safe_filename(s):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", s).strip("_")


def draw_card_content(target, event, country_code, competitor_name, seed):
    draw = ImageDraw.Draw(target)

    small_font = load_font(92)
    name_font = load_font(200, bold=True)

    x0, y0 = 220, 245

    flag_w, flag_h = 780, 420
    draw_flag(draw, country_code, x0, y0 + 95, flag_w, flag_h)

    text_x = x0 + flag_w + 80

    draw.text(
        (text_x, y0 + 90),
        f"{event} Final - Seed #{seed}",
        font=small_font,
        fill="black",
    )

    lines = wrap_name(draw, competitor_name, name_font, PAGE_W - text_x - 250)

    ascent, descent = name_font.getmetrics()
    line_gap = int((ascent + descent) * 1.2)

    for i, line in enumerate(lines):
        draw.text(
            (text_x, y0 + 245 + i * line_gap),
            line,
            font=name_font,
            fill="black",
        )


def create_page(event, country_code, competitor_name, seed):
    page = Image.new("RGB", (PAGE_W, PAGE_H), "white")
    draw = ImageDraw.Draw(page)

    draw.line([(0, FOLD_Y), (PAGE_W, FOLD_Y)], fill="#dddddd", width=2)

    half_h = PAGE_H // 2

    bottom = Image.new("RGB", (PAGE_W, half_h), "white")
    draw_card_content(bottom, event, country_code, competitor_name, seed)
    page.paste(bottom, (0, FOLD_Y))

    top = Image.new("RGB", (PAGE_W, half_h), "white")
    draw_card_content(top, event, country_code, competitor_name, seed)
    page.paste(top.rotate(180), (0, 0))

    return page


def make_cards_from_csv(csv_path):
    event = extract_event_name(csv_path)
    pages = []

    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        required = {"country_code", "competitor_name"}
        missing = required - set(reader.fieldnames or [])

        if missing:
            raise ValueError(f"CSV is missing required columns: {', '.join(sorted(missing))}")

        for seed, row in enumerate(reader, start=1):
            country_code = row["country_code"].strip()
            competitor_name = row["competitor_name"].strip()

            if not country_code or not competitor_name:
                print(f"Skipping incomplete row: {row}")
                continue

            pages.append(create_page(event, country_code, competitor_name, seed))

    if not pages:
        print("No valid rows found.")
        return

    output_path = os.path.join(OUT_DIR, f"{safe_filename(event)}_table_tents.pdf")

    pages[0].save(
        output_path,
        "PDF",
        resolution=300.0,
        save_all=True,
        append_images=pages[1:],
    )

    print(f"Event: {event}")
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 make_table_tents.py Megaminx_seeds.csv")
        sys.exit(1)

    make_cards_from_csv(sys.argv[1])

