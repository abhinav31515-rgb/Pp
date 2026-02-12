from __future__ import annotations

import os
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

from PIL import Image, ImageDraw
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.util import Inches, Pt


@dataclass
class BrandStyle:
    name: str
    primary: Tuple[int, int, int]
    secondary: Tuple[int, int, int]
    accent: Tuple[int, int, int]
    title_font: str
    body_font: str


STYLE_LIBRARY: Dict[str, BrandStyle] = {
    "luxury": BrandStyle(
        name="Luxury Noir",
        primary=(17, 17, 17),
        secondary=(38, 35, 33),
        accent=(196, 162, 96),
        title_font="Playfair Display",
        body_font="Aptos",
    ),
    "tech": BrandStyle(
        name="Cinematic Tech",
        primary=(10, 20, 38),
        secondary=(25, 49, 88),
        accent=(125, 249, 255),
        title_font="Montserrat",
        body_font="Aptos",
    ),
    "fashion": BrandStyle(
        name="Editorial Vogue",
        primary=(30, 24, 26),
        secondary=(84, 58, 67),
        accent=(245, 216, 176),
        title_font="Bodoni MT",
        body_font="Aptos",
    ),
}


def infer_use_case(all_text: str) -> str:
    text = all_text.lower()
    if any(k in text for k in ["saas", "ai", "cloud", "platform", "api"]):
        return "tech"
    if any(k in text for k in ["fashion", "luxury", "collection", "style", "brand"]):
        return "fashion"
    return "luxury"


def pick_style(use_case: str, feedback: str) -> BrandStyle:
    feedback_lower = feedback.lower()
    if "tech" in feedback_lower or "futur" in feedback_lower:
        return STYLE_LIBRARY["tech"]
    if "fashion" in feedback_lower or "editorial" in feedback_lower:
        return STYLE_LIBRARY["fashion"]
    return STYLE_LIBRARY.get(use_case, STYLE_LIBRARY["luxury"])


def _set_slide_background(slide, color: Tuple[int, int, int]):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(*color)


def _style_text_frame(text_frame, style: BrandStyle, is_title: bool = False):
    for paragraph in text_frame.paragraphs:
        paragraph.space_before = Pt(0)
        paragraph.space_after = Pt(8 if is_title else 4)
        for run in paragraph.runs:
            run.font.name = style.title_font if is_title else style.body_font
            run.font.bold = is_title
            run.font.size = Pt(38 if is_title else 19)
            run.font.color.rgb = RGBColor(*style.accent if is_title else (235, 235, 235))


def _add_placeholder_image(slide, style: BrandStyle, temp_dir: Path) -> None:
    placeholder_path = temp_dir / f"placeholder-{uuid.uuid4().hex}.png"
    image = Image.new("RGB", (1280, 720), style.secondary)
    draw = ImageDraw.Draw(image)
    draw.rectangle((40, 40, 1240, 680), outline=style.accent, width=8)
    draw.text((100, 330), "Premium Placeholder Visual", fill=style.accent)
    image.save(placeholder_path)

    slide.shapes.add_picture(str(placeholder_path), Inches(6.2), Inches(1.3), Inches(6.6), Inches(3.7))


def analyze_presentation(input_path: str) -> Dict:
    prs = Presentation(input_path)
    all_text: List[str] = []
    image_count = 0
    title_count = 0

    for slide in prs.slides:
        if slide.shapes.title and slide.shapes.title.has_text_frame:
            title_count += 1
            all_text.append(slide.shapes.title.text)
        for shape in slide.shapes:
            if hasattr(shape, "text") and shape.text:
                all_text.append(shape.text)
            if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                image_count += 1

    combined = " ".join(all_text)
    use_case = infer_use_case(combined)
    return {
        "slides": len(prs.slides),
        "image_count": image_count,
        "title_coverage": round((title_count / max(len(prs.slides), 1)) * 100, 1),
        "use_case": use_case,
        "quality_flags": [
            "Low visual hierarchy" if title_count < len(prs.slides) else "Good title consistency",
            "Need stronger brand contrast",
            "Spacing and alignment can be improved",
        ],
        "animation_plan": [
            "Fade-up for title and key metrics",
            "Cinematic zoom for hero imagery",
            "Staggered reveal for bullet points",
        ],
    }


def enhance_presentation(input_path: str, output_dir: str, feedback: str = "") -> Dict:
    report = analyze_presentation(input_path)
    style = pick_style(report["use_case"], feedback)

    prs = Presentation(input_path)
    temp_dir = Path(output_dir)
    modifications = []

    for index, slide in enumerate(prs.slides, start=1):
        _set_slide_background(slide, style.primary)
        modifications.append(f"Slide {index}: applied {style.name} background and palette")

        has_picture = False
        for shape in slide.shapes:
            if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                has_picture = True
            if not getattr(shape, "has_text_frame", False):
                continue
            if shape == slide.shapes.title:
                _style_text_frame(shape.text_frame, style, is_title=True)
            else:
                _style_text_frame(shape.text_frame, style, is_title=False)

        if not has_picture:
            _add_placeholder_image(slide, style, temp_dir)
            modifications.append(f"Slide {index}: inserted premium placeholder visual")

        notes_frame = slide.notes_slide.notes_text_frame
        notes_frame.text = (
            "Motion cue: soft fade-in for title (0.6s), content stagger (0.2s delay), "
            "image parallax emphasis for cinematic delivery."
        )

    output_name = f"luxury-{uuid.uuid4().hex[:8]}.pptx"
    output_path = os.path.join(output_dir, output_name)
    prs.save(output_path)

    return {
        "analysis": report,
        "style_applied": style.name,
        "fonts": [style.title_font, style.body_font],
        "modifications": modifications,
        "output_file": output_name,
    }
