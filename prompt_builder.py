"""Prompt builder for 4-panel manga generation."""

from typing import List, Dict, Any
from models import CharacterInput, SceneInput
import yaml


def build_manga_prompt(
    characters: List[CharacterInput],
    scenes: List[SceneInput],
    has_layout_ref: bool
) -> str:
    """Build structured YAML prompt for Gemini API.

    Args:
        characters: List of character information
        scenes: List of 4 scene specifications
        has_layout_ref: Whether layout reference image is provided

    Returns:
        Structured YAML prompt string

    Raises:
        ValueError: If scenes count is not exactly 4
    """
    if len(scenes) != 4:
        raise ValueError(f"Expected exactly 4 scenes, got {len(scenes)}")

    # Build structured data
    prompt_data: Dict[str, Any] = {
        "task": "4-panel manga generation",
        "output_format": "single image containing all 4 panels"
    }

    # Priority and layout compliance
    if has_layout_ref:
        prompt_data["CRITICAL_PRIORITY"] = {
            "highest_priority": "layout_reference_compliance",
            "requirement": "MUST follow layout reference with ABSOLUTE PRECISION",
            "mandatory_elements": [
                "Panel arrangement must match reference exactly",
                "Panel sizes must match reference exactly",
                "Panel positions must match reference exactly",
                "Panel borders/frames must match reference exactly",
                "Spacing between panels must match reference exactly",
                "Overall composition must be visually identical to reference"
            ],
            "constraint": "Do NOT deviate from layout reference in ANY way",
            "note": "All other instructions are secondary to layout compliance",
            "CRITICAL_NOTE": "The aspect ratio specification (3:4) defines the CANVAS dimensions ONLY. It does NOT define the panel layout within the canvas. The layout reference image defines the panel arrangement. Simply fit the layout reference into a 3:4 canvas."
        }
        prompt_data["instruction"] = "Generate 4-panel manga following specifications below while maintaining EXACT adherence to layout reference. The 3:4 aspect ratio is for the OVERALL CANVAS only - the panel layout must match the reference image exactly."
    else:
        prompt_data["instruction"] = "Generate 4-panel manga based on specifications below with free choice of panel layout"

    # Character references
    if characters:
        prompt_data["character_references"] = {
            "count": len(characters),
            "characters": []
        }
        for idx, char in enumerate(characters, 1):
            char_data = {
                "id": idx,
                "name": char.name,
                "reference_image_provided": True
            }
            if char.description:
                char_data["description"] = char.description
            prompt_data["character_references"]["characters"].append(char_data)

    # Layout reference details
    if has_layout_ref:
        prompt_data["layout_reference"] = {
            "provided": True,
            "requirements": {
                "panel_positions": "Copy exact X/Y coordinates of each panel relative to the reference",
                "panel_dimensions": "Match width and height proportions precisely",
                "panel_borders": "Replicate thickness and style exactly",
                "spacing": "Maintain exact gaps between panels",
                "composition": "Final image must be visually identical in layout",
                "non_negotiable": "Layout reference is the blueprint - follow exactly",
                "aspect_ratio_clarification": "The 3:4 aspect ratio is for the CANVAS (overall output image). The layout reference shows the INTERNAL panel arrangement. Simply reproduce the layout reference panel arrangement within a 3:4 portrait canvas."
            }
        }

    # Panel specifications
    prompt_data["panels"] = []
    for idx, scene in enumerate(scenes, 1):
        panel_data = {
            "panel_number": idx,
            "scene_description": scene.scene_description
        }

        if scene.character_states:
            panel_data["characters"] = {}
            for char_idx_str, state in scene.character_states.items():
                char_idx = int(char_idx_str)
                if 0 <= char_idx < len(characters):
                    char_name = characters[char_idx].name
                else:
                    char_name = f"Character_{char_idx + 1}"
                panel_data["characters"][char_name] = state

        if scene.objects_background:
            panel_data["background_and_objects"] = scene.objects_background

        prompt_data["panels"].append(panel_data)

    # Output requirements
    requirements = {
        "priority_order": []
    }

    if has_layout_ref:
        requirements["priority_order"] = [
            {
                "priority": 1,
                "name": "layout_compliance",
                "description": "Follow layout reference image EXACTLY",
                "details": [
                    "Panel positions, sizes, borders, spacing must match precisely",
                    "Layout structure is more important than any other aspect"
                ]
            },
            {
                "priority": 2,
                "name": "character_consistency",
                "description": "Maintain character appearance across panels using provided reference images"
            },
            {
                "priority": 3,
                "name": "scene_content",
                "description": "Show scene, characters, and background described in each panel"
            },
            {
                "priority": 4,
                "name": "text_and_symbols",
                "rules": {
                    "speech_bubbles": "COMPLETELY EMPTY (no dialogue text)",
                    "text_forbidden": "Do NOT write letters, words, text, sound effects (like 'ドン')",
                    "symbols_allowed": "Manga symbols ARE allowed (♪, !, ?, sweat drops, effect lines, emotion marks)",
                    "text_inclusion": "Only include text explicitly specified in panel descriptions",
                    "layout_priority": "While keeping bubbles empty, maintain exact layout from reference"
                }
            },
            {
                "priority": 5,
                "name": "art_style_and_coloring",
                "requirements": {
                    "color_mode": "COLOR ILLUSTRATION (NOT black and white)",
                    "coloring_technique": "Flat colors with even, beautiful coloring throughout",
                    "character_emphasis": {
                        "main_characters": {
                            "colors": "bold, vibrant colors",
                            "linework": "thicker lines"
                        },
                        "objects_and_background": {
                            "colors": "subdued, muted colors",
                            "linework": "thinner, lighter lines"
                        }
                    },
                    "background_handling": {
                        "when_specified": "Color appropriately with muted tones",
                        "when_not_specified": "Interpret context and add appropriate colors or abstract background"
                    },
                    "style": "manga/comic art style with professional flat coloring"
                }
            }
        ]
    else:
        requirements["no_layout_reference"] = {
            "character_consistency": "Maintain appearance across panels using provided reference images",
            "scene_content": "Show scene, characters, and background as described",
            "text_rules": {
                "forbidden": "No letters, words, dialogue, or sound effect text",
                "speech_bubbles": "Draw but keep completely empty",
                "allowed": "Manga symbols (♪, !, ?, sweat, emotion marks, effect lines)",
                "inclusion": "Only include text explicitly mentioned in panel specifications"
            },
            "art_style_and_coloring": {
                "color_mode": "COLOR ILLUSTRATION (NOT black and white)",
                "coloring_technique": "Flat colors with even, beautiful coloring throughout",
                "character_emphasis": {
                    "main_characters": {
                        "colors": "bold, vibrant colors",
                        "linework": "thicker lines"
                    },
                    "objects_and_background": {
                        "colors": "subdued, muted colors",
                        "linework": "thinner, lighter lines"
                    }
                },
                "background_handling": {
                    "when_specified": "Color appropriately with muted tones",
                    "when_not_specified": "Interpret context and add appropriate colors or abstract background"
                },
                "style": "manga/comic art style with professional flat coloring"
            }
        }

    prompt_data["output_requirements"] = requirements

    # Convert to YAML
    yaml_prompt = yaml.dump(prompt_data, allow_unicode=True, default_flow_style=False, sort_keys=False)

    return yaml_prompt
