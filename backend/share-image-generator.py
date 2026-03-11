import sqlite3
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from datetime import datetime
import urllib.request
import os

# Database paths
DB_PATH = '/var/www/nzpt/urgency.sqlite3'
BILLCOUNTER_PATH = '/var/www/nzpt/billcounter.txt'
LASTUPDATE_PATH = '/var/www/nzpt/lastupdate.txt'

# Image settings — 1024x1024 square
IMG_W = 1024
IMG_H = 1024
FONT_PATH_BOLD   = "genresource/arial_bold.ttf"   # fallback handled below
FONT_PATH_REGULAR= "genresource/arial.ttf"

# Background image
BG_IMAGE_URL  = "https://upload.wikimedia.org/wikipedia/commons/7/7e/Beehive%2C_Wellington%2C_New_Zealand.jpg"
BG_IMAGE_PATH = "beehive_bg.jpg"

# Colour palette
C_NAVY        = (10,  20,  45)
C_ACCENT      = (134, 20,  255)        # #8614ff purple
C_VALUE       = (255, 255, 255)        # white
C_RED         = (255, 70,  70)         # red for % value cards
C_RED         = (255, 70,  70)         # red for % values
C_TITLE       = (180, 200, 230)        # muted blue-white
C_FOOTER      = (140, 160, 190)

# Card layout  —  2 columns × 3 rows
# Order: Sitting Days | Bills This Parliament
#        Urgent Sitting Days | Bills Under Urgency
#        % of Days Urgent | % of Bills Urgent
CARD_COLS   = 2
CARD_ROWS   = 3
PAD_X       = 50
PAD_TOP     = 170
PAD_BOTTOM  = 80
GAP_X       = 20
GAP_Y       = 20

CARD_W = (IMG_W - 2 * PAD_X - (CARD_COLS - 1) * GAP_X) // CARD_COLS
CARD_H = (IMG_H - PAD_TOP - PAD_BOTTOM - (CARD_ROWS - 1) * GAP_Y) // CARD_ROWS

TITLES = [
    "Sitting Days",         "Bills This Parliament",
    "Urgent Sitting Days",  "Bills Under Urgency",
    "% of Days Urgent",     "% of Bills Urgent",
]

# Indices of cards that should show red values (the % cards)
RED_VALUE_INDICES = {4, 5}

# ---------------------------------------------------------------------------

def load_bg():
    if not os.path.exists(BG_IMAGE_PATH):
        try:
            urllib.request.urlretrieve(BG_IMAGE_URL, BG_IMAGE_PATH)
        except Exception as e:
            print(f"Could not download background: {e}")
            return None
    try:
        return Image.open(BG_IMAGE_PATH).convert("RGB")
    except Exception:
        return None


def get_data():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('SELECT COUNT(id) FROM urgency')
    num_days_sat = c.fetchone()[0]

    c.execute('SELECT COUNT(id) FROM urgency WHERE in_urgency = 1')
    num_days_urgency = c.fetchone()[0]

    percent_urgency = round((num_days_urgency / num_days_sat) * 100, 1) if num_days_sat > 0 else 0

    c.execute('SELECT COUNT(id) FROM bills')
    count_bills_urgent = c.fetchone()[0]

    conn.close()

    try:
        with open(BILLCOUNTER_PATH, 'r') as f:
            billcounter = f.read().strip()
        count_bills_all, billcounter_date = billcounter.split(',')
        count_bills_all = int(count_bills_all)
    except Exception:
        count_bills_all = 0
        billcounter_date = 'N/A'

    percent_bills_urgent = round((count_bills_urgent / count_bills_all) * 100, 1) if count_bills_all > 0 else 0

    values = [
        # col 1              col 2
        str(num_days_sat),   str(count_bills_all),       # row 1
        str(num_days_urgency), str(count_bills_urgent),  # row 2
        f"{percent_urgency}%", f"{percent_bills_urgent}%",  # row 3 (red)
    ]
    return values, billcounter_date


def load_fonts():
    # Try fonts in order of preference
    BOLD_CANDIDATES = [
        FONT_PATH_BOLD,
        "genresource/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]
    REGULAR_CANDIDATES = [
        FONT_PATH_REGULAR,
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]

    def find_font(candidates, size):
        for path in candidates:
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
        # Last resort: load_default doesn't support size, so we use a workaround
        try:
            return ImageFont.load_default(size=size)
        except TypeError:
            return ImageFont.load_default()

    sizes = {}
    sizes['heading']  = find_font(BOLD_CANDIDATES,    52)
    sizes['subhead']  = find_font(REGULAR_CANDIDATES, 22)
    sizes['card_val'] = find_font(BOLD_CANDIDATES,    52)
    sizes['card_lbl'] = find_font(REGULAR_CANDIDATES, 18)
    sizes['footer']   = find_font(REGULAR_CANDIDATES, 18)
    sizes['badge']    = find_font(BOLD_CANDIDATES,    16)
    return sizes


def rounded_rect(draw, xy, radius, fill, outline=None, outline_width=1):
    """Draw a filled rounded rectangle; outline is optional."""
    x0, y0, x1, y1 = xy
    # Use draw.rounded_rectangle if available (Pillow ≥ 8.2)
    try:
        draw.rounded_rectangle(xy, radius=radius, fill=fill,
                               outline=outline, width=outline_width)
    except AttributeError:
        draw.rectangle(xy, fill=fill, outline=outline, width=outline_width)


def alpha_composite_color(base_img, color_rgba, region=None):
    """Blend a solid RGBA colour over a region of base_img (RGB)."""
    overlay = Image.new("RGBA", base_img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    region = region or (0, 0, *base_img.size)
    draw.rectangle(region, fill=color_rgba)
    base_rgba = base_img.convert("RGBA")
    composited = Image.alpha_composite(base_rgba, overlay)
    return composited.convert("RGB")


def make_glass_card(draw, x, y, w, h, radius=14):
    """Draw a frosted-glass card effect using RGBA compositing trick via draw."""
    # semi-transparent white fill
    try:
        draw.rounded_rectangle(
            [x, y, x + w, y + h],
            radius=radius,
            fill=(255, 255, 255, 22),
            outline=(255, 255, 255, 60),
            width=1,
        )
    except TypeError:
        # older Pillow: rounded_rectangle doesn't support RGBA fill via draw
        draw.rounded_rectangle([x, y, x + w, y + h], radius=radius,
                                fill=(40, 60, 90), outline=(90, 130, 180), width=1)


def draw_image(values, billcounter_date, fonts, bg):
    # Create image with navy background
    canvas = Image.new("RGB", (IMG_W, IMG_H), C_NAVY)

    if bg is not None:
        # Crop bg to fill canvas (cover behaviour)
        bg_ratio = bg.width / bg.height
        canvas_ratio = IMG_W / IMG_H
        if bg_ratio > canvas_ratio:
            new_h = IMG_H
            new_w = int(bg_ratio * new_h)
        else:
            new_w = IMG_W
            new_h = int(new_w / bg_ratio)
        bg_resized = bg.resize((new_w, new_h), Image.LANCZOS)
        # centre-crop
        ox = (new_w - IMG_W) // 2
        oy = (new_h - IMG_H) // 2
        bg_cropped = bg_resized.crop((ox, oy, ox + IMG_W, oy + IMG_H))
        # darken + blur for legibility
        bg_cropped = bg_cropped.filter(ImageFilter.GaussianBlur(radius=4))
        bg_cropped = ImageEnhance.Brightness(bg_cropped).enhance(0.38)
        canvas.paste(bg_cropped, (0, 0))

    # dark navy overlay for contrast
    canvas = alpha_composite_color(canvas, (8, 18, 38, 185))

    # ------------------------------------------------------------------ draw layer
    draw = ImageDraw.Draw(canvas, "RGBA")

    # ── accent bar left edge ──────────────────────────────────────────────
    draw.rectangle([0, 0, 7, IMG_H], fill=C_ACCENT)

    # ── header ───────────────────────────────────────────────────────────
    badge_text = "NZPolToolbox | NZPT"
    badge_x, badge_y = 28, 36
    bw = draw.textlength(badge_text, font=fonts['subhead']) + 28
    bh = 34
    draw.rounded_rectangle([badge_x, badge_y, badge_x + bw, badge_y + bh],
                            radius=8, fill=C_ACCENT)
    draw.text((badge_x + 14, badge_y + bh // 2), badge_text,
              font=fonts['subhead'], fill=C_VALUE, anchor="lm")

    draw.text((28, badge_y + bh + 10), "Urgency Tracker",
              font=fonts['heading'], fill=C_VALUE, anchor="lt")

    # thin purple rule under header
    rule_y = PAD_TOP - 20
    draw.rectangle([28, rule_y, IMG_W - 28, rule_y + 2],
                   fill=(134, 20, 255, 160))

    # ── cards ─────────────────────────────────────────────────────────────
    for i in range(6):
        col = i % CARD_COLS
        row = i // CARD_COLS

        cx = PAD_X + col * (CARD_W + GAP_X)
        cy = PAD_TOP + row * (CARD_H + GAP_Y)

        make_glass_card(draw, cx, cy, CARD_W, CARD_H, radius=12)

        # purple accent strip on top edge of card
        card_cx = cx + CARD_W // 2
        draw.rectangle([card_cx - 24, cy, card_cx + 24, cy + 3], fill=C_ACCENT)

        # label — centred
        draw.text(
            (card_cx, cy + 18),
            TITLES[i].upper(),
            font=fonts['card_lbl'],
            fill=C_TITLE,
            anchor="mt",
        )

        # value — centred; red for % boxes (indices 4 & 5)
        val_color = C_RED if i in RED_VALUE_INDICES else C_VALUE
        draw.text(
            (card_cx, cy + CARD_H // 2 + 8),
            values[i],
            font=fonts['card_val'],
            fill=val_color,
            anchor="mm",
        )

    # ── footer ────────────────────────────────────────────────────────────
    footer_y = IMG_H - 52
    draw.rectangle([PAD_X, footer_y - 10, IMG_W - PAD_X, footer_y - 9],
                   fill=(134, 20, 255, 80))

    try:
        last_updated = open(LASTUPDATE_PATH).read().strip()
    except Exception:
        last_updated = datetime.now().strftime("%d %b %Y")

    draw.text(
        (PAD_X, footer_y),
        f"Last updated: {last_updated}   •   nzpt.cjs.nz",
        font=fonts['footer'],
        fill=C_FOOTER,
        anchor="lt",
    )

    draw.text(
        (PAD_X, footer_y + 24),
        "Data sourced from parliament.nz",
        font=fonts['footer'],
        fill=(100, 120, 150),
        anchor="lt",
    )

    return canvas


def main():
    bg     = load_bg()
    fonts  = load_fonts()

    try:
        values, billcounter_date = get_data()
    except Exception as e:
        print(f"Database not available ({e}) — using demo data")
        values = ["142", "312", "38", "87", "26.8%", "27.9%"]
        billcounter_date = datetime.now().strftime("%d %b %Y")

    img = draw_image(values, billcounter_date, fonts, bg)
    out = "/var/www/nzpt/assets/nzptshare.png"
    img.save(out, quality=95)
    print(f"Saved → {out}  ({IMG_W}×{IMG_H})")


if __name__ == "__main__":
    main()