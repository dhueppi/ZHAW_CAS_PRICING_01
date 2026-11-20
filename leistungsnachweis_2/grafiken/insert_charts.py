from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parents[1]
CHARTS = Path(__file__).resolve().parent / "output"
DECK = ROOT / "LN2_AquaClean_Alba_Hotel_Preiskonzept_2026.pptx"

NAVY = "14283B"
INK = "263B4C"
TEAL = "007C78"
MINT = "E2F2EF"
PALE = "F3F6F8"
LINE = "D8E1E7"
MID = "657685"
GOLD = "D7A13A"
GOLDPALE = "FFF3D9"
RED = "B84D48"
WHITE = "FFFFFF"


def rgb(value):
    return RGBColor.from_string(value)


def remove_shape(slide, shape):
    element = shape._element
    embedded_ids = {
        blip.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed")
        for blip in element.xpath(".//a:blip")
    }
    element.getparent().remove(element)
    for rel_id in embedded_ids:
        if rel_id and rel_id in slide.part.rels:
            slide.part.drop_rel(rel_id)


def deduplicate_archive(path):
    temporary = path.with_name(path.stem + ".tmp" + path.suffix)
    with ZipFile(path, "r") as source:
        entries = {}
        for info in source.infolist():
            entries[info.filename] = (info, source.read(info))
    with ZipFile(temporary, "w", compression=ZIP_DEFLATED) as target:
        for info, content in entries.values():
            target.writestr(info.filename, content)
    temporary.replace(path)


def add_rect(slide, x, y, w, h, fill, rounded=False):
    kind = MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE
    shape = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = rgb(fill)
    shape.line.color.rgb = rgb(fill)
    if rounded:
        shape.adjustments[0] = 0.10
    return shape


def add_text(slide, x, y, w, h, value, size, fill, bold=False,
             margin=0.04, valign=MSO_ANCHOR.TOP):
    shape = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = shape.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.margin_left = Inches(margin)
    frame.margin_right = Inches(margin)
    frame.margin_top = Inches(margin)
    frame.margin_bottom = Inches(margin)
    frame.vertical_anchor = valign
    p = frame.paragraphs[0]
    p.text = value
    p.font.name = "Arial"
    p.font.size = Pt(size)
    p.font.bold = bold
    p.font.color.rgb = rgb(fill)
    return shape


def populate_assumptions_slide(slide):
    add_rect(slide, 0, 0, 13.333, 0.10, TEAL)
    add_text(slide, 0.58, 0.22, 10.9, 0.23,
             "ANHANG · MODELLANNAHMEN", 9, TEAL, True)
    add_text(slide, 0.58, 0.50, 12.15, 0.58,
             "Annahmen hinter den neun Diagrammen", 23, NAVY, True)
    add_rect(slide, 0.58, 1.18, 12.15, 0.014, LINE)
    add_text(slide, 0.72, 1.35, 11.9, 0.40,
             "Fakten, Teaminputs und illustrative Modellwerte sind getrennt. Sämtliche Kosten- und WTP-Annahmen unten sind noch nicht validiert.",
             12, INK, True)

    items = [
        ("02 · Segmentmatrix", "4 Hotel-Archetypen qualitativ; Achsen und Pilotpriorität sind strategische Hypothesen, keine quantitative Segmentstudie.", TEAL),
        ("03 · Preisanker", "CH WC-Set 279; Designkeramik 790; Alba Shop 899/Richtpreis 1’143; Peer 1’299–1’999. Hotel CHF 790 netto → CHF 854 brutto äquivalent. Preisarten gemischt.", NAVY),
        ("04 · Kostenwasserfall", "Teaminputs: HK 250, Hotelbasis 790 netto, Referenz 1’000 netto. Rohertrag 540/750 vor Logistik, Vertrieb, Installation, Service und Fixkosten.", TEAL),
        ("05 · Peerpreise", "Alba 899; VitrA 1’299; Duravit 1’390; Grohe/Laufen 1’999 CHF. Schweizer Shop-Momentaufnahmen; Ausstattung und Preisstatus prüfen.", NAVY),
        ("06 · WTS / WTP", "Featurekosten angenommen: Fleet 70, Predict 45, Care 160 netto. WTS-Hürde = Kosten/(1−30%). WTP-Proxies: 201.67, 92.51, 185.01 netto; nicht gemessen.", GOLD),
        ("07 · Leistungsstaffel", "1–4 Einzelabruf; Fleet ab 5; Care ab 10 Geräten je Standort. Schwellen und enthaltene Leistungen sind Prüfannahmen, kein Beschluss.", TEAL),
        ("08 · Pay-per-Flush", "Herstellung 250 + Installation 150 über 5 Jahre; Service 45/Jahr; Connectivity/Admin 25/Jahr; 0.20 CHF/Nutzung → Modell-Break-even 750 Nutzungen/Jahr.", GOLD),
        ("09 · Preis-Zeit", "790 netto → 854 brutto, Referenz 1’000 netto → 1’081 brutto; Fleet/Predict/Care 1’299/1’399/1’599 brutto. Verschiedene Leistungspakete; Gates hypothetisch.", NAVY),
        ("10 · Projekt-BE", "Low: DB 240/Fix 5’000 → 21 Geräte. Basis: 340/3’500 → 11. Hoch: 600/3’000 → 5. Ausser HK/Preisen sind alle Kosten illustrativ.", RED),
    ]
    xs = [0.68, 4.82, 8.96]
    ys = [1.95, 3.40, 4.85]
    w, h = 3.72, 1.25
    for i, (title, body, accent) in enumerate(items):
        x, y = xs[i % 3], ys[i // 3]
        add_rect(slide, x, y, w, h, PALE, rounded=True)
        add_rect(slide, x, y, 0.065, h, accent)
        add_text(slide, x + 0.15, y + 0.11, w - 0.28, 0.25,
                 title, 10.5, NAVY, True)
        add_text(slide, x + 0.15, y + 0.43, w - 0.28, 0.74,
                 body, 8.6, INK)
    add_text(slide, 0.62, 6.43, 12.0, 0.30,
             "Vollständige Herleitungen und Abgrenzungen: grafiken/annahmen_diagramme.md · Team-WTP-Hypothesen sind keine erhobene Hotel-Zahlungsbereitschaft.",
             9.2, MID)
    add_text(slide, 0.58, 7.13, 11.75, 0.17,
             "CAS Pricing · Leistungsnachweis 2 · Annahmen dokumentiert am 20.11.2026",
             8, MID)
    add_text(slide, 12.30, 7.10, 0.42, 0.20, "19", 9, MID)


def main():
    if not DECK.exists():
        raise FileNotFoundError(f"Slidedoc not found: {DECK}")
    prs = Presentation(DECK)
    if len(prs.slides) < 18:
        raise ValueError(f"Expected at least 18 slides, found {len(prs.slides)}")

    # Replace the text/card bodies on slides 2–10 with the requested charts.
    mappings = {
        1: "02_segment_matrix.png",
        2: "03_price_ladder.png",
        3: "04_cost_waterfall.png",
        4: "05_peer_prices.png",
        5: "06_wts_wtp.png",
        6: "07_performance_matrix.png",
        7: "08_usage_breakeven.png",
        8: "09_price_time_gates.png",
        9: "10_breakeven_scenarios.png",
    }
    for slide_index, filename in mappings.items():
        slide = prs.slides[slide_index]
        for shape in list(slide.shapes):
            top = shape.top / 914400
            if 1.92 <= top < 7.0:
                remove_shape(slide, shape)
        used_image_ids = {
            blip.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed")
            for shape in slide.shapes
            for blip in shape._element.xpath(".//a:blip")
        }
        for rel_id, rel in list(slide.part.rels.items()):
            if rel.reltype.endswith("/image") and rel_id not in used_image_ids:
                slide.part.drop_rel(rel_id)
        image_path = CHARTS / filename
        if not image_path.exists():
            raise FileNotFoundError(f"Chart image not found: {image_path}")
        picture = slide.shapes.add_picture(
            str(image_path), Inches(0.70), Inches(2.00), width=Inches(11.95)
        )
        if picture.top + picture.height > Inches(6.78):
            picture.height = Inches(6.78) - picture.top

    # Update the existing assumptions page in place so repeated runs stay clean.
    assumptions_slide = None
    for slide in prs.slides:
        texts = [shape.text for shape in slide.shapes
                 if getattr(shape, "has_text_frame", False)]
        if any("Annahmen hinter den neun Diagrammen" in value for value in texts):
            assumptions_slide = slide
            break
    if assumptions_slide is None:
        assumptions_slide = prs.slides.add_slide(prs.slide_layouts[6])
    else:
        for shape in list(assumptions_slide.shapes):
            remove_shape(assumptions_slide, shape)
    populate_assumptions_slide(assumptions_slide)

    # Refresh the printed page numbers in the footer.
    for page_number, slide in enumerate(prs.slides, start=1):
        for shape in slide.shapes:
            if (getattr(shape, "has_text_frame", False)
                    and shape.left >= Inches(12.15)
                    and shape.top >= Inches(7.0)
                    and shape.width <= Inches(0.6)):
                shape.text_frame.text = f"{page_number:02d}"

    prs.save(DECK)
    deduplicate_archive(DECK)
    print(f"Inserted 9 charts and assumptions slide into {DECK}")
    print(f"Total slides: {len(prs.slides)} (10 main + 9 appendix)")


if __name__ == "__main__":
    main()
