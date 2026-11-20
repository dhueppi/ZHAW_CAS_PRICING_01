from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

ROOT = Path(__file__).parent
OUT = ROOT / "Behavioral_Pricing_Cases.pptx"
prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)

NAVY = RGBColor(20, 35, 54)
WHITE = RGBColor(255, 255, 255)
BG = RGBColor(247, 248, 250)
MUTED = RGBColor(160, 174, 187)
TEAL = RGBColor(0, 174, 164)
RED = RGBColor(204, 67, 63)
GREEN = RGBColor(53, 142, 103)
BLUE = RGBColor(69, 124, 184)
GOLD = RGBColor(195, 154, 76)


def box(slide, x, y, w, h, color, rounded=False):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE,
        Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    if rounded:
        shape.adjustments[0] = 0.12
    return shape


def text(slide, x, y, w, h, value, size, color=NAVY, bold=False,
         align=PP_ALIGN.LEFT):
    shape = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = shape.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.margin_left = Inches(0.02)
    frame.margin_right = Inches(0.02)
    frame.margin_top = Inches(0.01)
    frame.margin_bottom = Inches(0.01)
    p = frame.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = value
    run.font.name = "Aptos Display"
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return shape


def blank(bg=BG):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = bg
    return slide


def image_crop(source, crop_start, target_ratio=1.20):
    source = ROOT / source
    with Image.open(source) as image:
        width, height = image.size
        crop_height = min(height, int(width / target_ratio))
        top = min(max(crop_start, 0), height - crop_height)
        image = image.crop((0, top, width, top + crop_height))
        output = Path("/tmp") / (source.stem + "_slide_crop.png")
        image.save(output)
    return output


def case(name, color, evidence, effects, assessment, screenshot, crop_start, number):
    slide = blank()
    box(slide, 0, 0, 0.16, 7.5, color)
    text(slide, 0.75, 0.46, 5.65, 0.35,
         f"CASE 0{number}   /   BEHAVIORAL PRICING", 11, color, True)
    text(slide, 0.75, 0.95, 5.7, 0.75, name, 34, NAVY, True)
    text(slide, 0.8, 1.9, 5.5, 0.3, "BEOBACHTET", 10, color, True)
    text(slide, 0.8, 2.26, 5.45, 0.95, evidence, 17, NAVY, True)
    text(slide, 0.8, 3.42, 5.45, 0.3, "PRICE EFFECTS · SCRIPT S. 24", 10, color, True)
    y = 3.82
    for effect in effects:
        box(slide, 0.8, y + 0.04, 0.11, 0.11, color, True)
        text(slide, 1.06, y, 5.15, 0.45, effect, 16, NAVY, True)
        y += 0.55
    box(slide, 0.8, 5.62, 5.5, 0.9, color, True)
    text(slide, 1.02, 5.81, 5.05, 0.53, assessment, 14, WHITE, True)

    screenshot_path = image_crop(screenshot, crop_start)
    picture = slide.shapes.add_picture(
        str(screenshot_path), Inches(6.65), Inches(1.05),
        width=Inches(5.95), height=Inches(4.96))
    picture.line.color.rgb = RGBColor(224, 228, 232)
    text(slide, 6.7, 6.18, 5.8, 0.28,
         "WEBSITE-SCREENSHOT · 29.10.2026", 9, MUTED, True, PP_ALIGN.RIGHT)
    text(slide, 0.8, 7.05, 11.1, 0.2,
         "Effektnamen gemäss Behavioral Pricing Workshop 2026, Seite 24", 9, MUTED)
    text(slide, 12.0, 7.02, 0.5, 0.24, str(number + 1), 10, MUTED,
         align=PP_ALIGN.RIGHT)
    return slide


# Cover
slide = blank(NAVY)
box(slide, 0, 0, 0.2, 7.5, TEAL)
text(slide, 1.0, 1.08, 10.8, 0.35,
     "CAS PRICING   /   BEHAVIORAL PRICING", 13, TEAL, True)
text(slide, 1.0, 1.85, 11.0, 1.65,
     "Preise wirken.\nVier Marken. Vier Strategien.", 38, WHITE, True)
text(slide, 1.02, 4.45, 10.8, 0.55,
     "DENNER     BETTY BOSSI     APPLE     ROLEX", 19, MUTED, True)
text(slide, 1.02, 6.85, 10.8, 0.25,
     "Behavioral Pricing · Webseitenanalyse", 11, MUTED)

case(
    "Denner", RED, "49% · CHF 12.95 statt CHF 25.80",
    ["SALE SIGNS", "DISCOUNT PRESENTATION FORMAT", "COLOR, CENTS & FONT SIZE"],
    "Rabatt maximal sichtbar.", "denner_screenshot.png", 0, 1)
case(
    "Betty Bossi", GREEN, "20% Rabatt · Code AIRFRYER20",
    ["SALE SIGNS", "DISCOUNT PRESENTATION FORMAT", "9-ENDINGS"],
    "Aktion im Banner; Produktpreise oft .95.", "bettybossi_screenshot.png", 0, 2)
case(
    "Apple", BLUE, "iPhone 18 Pro ab CHF 1’199.–",
    ["FRAMING", "9-ENDINGS", "PRICE-QUALITY EFFECT"],
    "Trade-in separat; Einstiegspreis prominent.", "apple_screenshot.png", 390, 3)
case(
    "Rolex", GOLD, "Prestige und Qualität – Preis nicht angezeigt",
    ["PRICE-QUALITY EFFECT", "WILLFUL OVERPRICING"],
    "Interpretation: Preis nicht auf der Seite sichtbar.",
    "rolex_screenshot.png", 140, 4)

# Closing slide
slide = blank(NAVY)
text(slide, 0.95, 0.85, 11.4, 0.4, "DIE KERNBOTSCHAFT", 12, TEAL, True)
text(slide, 0.95, 1.6, 11.25, 1.35,
     "Der Preiseffekt muss\nzur Marke passen.", 36, WHITE, True)
items = [("SPAREN", "Denner", RED), ("AUSWÄHLEN", "Betty Bossi", GREEN),
         ("UPGRADEN", "Apple", BLUE), ("BEGEHREN", "Rolex", GOLD)]
for i, (verb, brand, color) in enumerate(items):
    x = 0.95 + i * 3.05
    box(slide, x, 4.0, 2.7, 0.12, color)
    text(slide, x, 4.3, 2.7, 0.35, verb, 13, color, True)
    text(slide, x, 4.75, 2.7, 0.45, brand, 19, WHITE, True)
text(slide, 0.95, 6.38, 11.0, 0.52,
     "Diskussion: Wo stimmt Preiswirkung und Markenversprechen am besten überein?",
     16, MUTED)

prs.save(OUT)
print(OUT)
