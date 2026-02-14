"""Tests for prompt builder module."""

import pytest
from models import CharacterInput, SceneInput


# Test will be written for prompt_builder module
def test_build_manga_prompt_no_characters():
    """Test prompt building with no characters."""
    from prompt_builder import build_manga_prompt

    scenes = [
        SceneInput(
            scene_description="A sunny day in the park",
            character_states={},
            objects_background="Trees and benches"
        ),
        SceneInput(
            scene_description="Dark clouds appear",
            character_states={},
            objects_background="Storm clouds"
        ),
        SceneInput(
            scene_description="Rain starts falling",
            character_states={},
            objects_background="Rain"
        ),
        SceneInput(
            scene_description="Rainbow appears",
            character_states={},
            objects_background="Rainbow and sunshine"
        )
    ]

    prompt = build_manga_prompt(
        characters=[],
        scenes=scenes,
        has_layout_ref=False
    )

    assert "# 4-Panel Manga Generation Request" in prompt
    assert "## Overall Instructions" in prompt
    assert "## Panel Specifications" in prompt
    assert "### Panel 1" in prompt
    assert "### Panel 2" in prompt
    assert "### Panel 3" in prompt
    assert "### Panel 4" in prompt
    assert "A sunny day in the park" in prompt
    assert "Trees and benches" in prompt


def test_build_manga_prompt_with_characters():
    """Test prompt building with characters."""
    from prompt_builder import build_manga_prompt

    characters = [
        CharacterInput(
            name="Alice",
            ref_image="alice.png",
            description="A cheerful girl"
        ),
        CharacterInput(
            name="Bob",
            ref_image="bob.png",
            description="A serious boy"
        )
    ]

    scenes = [
        SceneInput(
            scene_description="Meeting at school",
            character_states={"0": "smiling", "1": "looking serious"},
            objects_background="School hallway"
        ),
        SceneInput(
            scene_description="Talking about homework",
            character_states={"0": "worried", "1": "confident"},
            objects_background="Classroom"
        ),
        SceneInput(
            scene_description="Working together",
            character_states={"0": "focused", "1": "helping"},
            objects_background="Library"
        ),
        SceneInput(
            scene_description="Success!",
            character_states={"0": "happy", "1": "proud"},
            objects_background="School gate"
        )
    ]

    prompt = build_manga_prompt(
        characters=characters,
        scenes=scenes,
        has_layout_ref=False
    )

    assert "## Character References" in prompt
    assert "2 character(s) are provided" in prompt
    assert "### Character 1: Alice" in prompt
    assert "### Character 2: Bob" in prompt
    assert "A cheerful girl" in prompt
    assert "A serious boy" in prompt
    assert "Alice: smiling" in prompt
    assert "Bob: looking serious" in prompt


def test_build_manga_prompt_with_layout_ref():
    """Test prompt building with layout reference."""
    from prompt_builder import build_manga_prompt

    scenes = [
        SceneInput(scene_description="Scene 1", character_states={}, objects_background=""),
        SceneInput(scene_description="Scene 2", character_states={}, objects_background=""),
        SceneInput(scene_description="Scene 3", character_states={}, objects_background=""),
        SceneInput(scene_description="Scene 4", character_states={}, objects_background="")
    ]

    prompt = build_manga_prompt(
        characters=[],
        scenes=scenes,
        has_layout_ref=True
    )

    assert "## Layout Reference" in prompt
    assert "layout reference image is provided" in prompt


def test_build_manga_prompt_output_requirements():
    """Test that output requirements are included."""
    from prompt_builder import build_manga_prompt

    scenes = [
        SceneInput(scene_description=f"Scene {i+1}", character_states={}, objects_background="")
        for i in range(4)
    ]

    prompt = build_manga_prompt(
        characters=[],
        scenes=scenes,
        has_layout_ref=False
    )

    assert "## Output Requirements" in prompt
    assert "Generate a single image containing all 4 panels" in prompt
    assert "Maintain character consistency across panels" in prompt
    assert "manga/comic art style" in prompt
