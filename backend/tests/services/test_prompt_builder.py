"""
Tests for app/services/prompt_builder.py
"""
import pytest

from app.models import SearchResult
from app.services.prompt_builder import (
    _PIVOT_QUESTIONS,
    _choose_followup_question,
    build_chat_prompt,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _section(content: str, section_type: str = "skills", similarity: float = 0.9):
    return SearchResult(content=content, section_type=section_type, similarity=similarity)


# ---------------------------------------------------------------------------
# _choose_followup_question
# ---------------------------------------------------------------------------


def test_choose_followup_contextual_when_random_below_threshold(monkeypatch):
    """random() < 0.6 → contextual follow-up instruction."""
    monkeypatch.setattr("app.services.prompt_builder.random.random", lambda: 0.1)
    result = _choose_followup_question([_section("Python")])
    assert "follow-up question" in result.lower()
    assert result not in _PIVOT_QUESTIONS


def test_choose_followup_pivot_when_random_above_threshold(monkeypatch):
    """random() >= 0.6 → one of the pre-written pivot questions."""
    monkeypatch.setattr("app.services.prompt_builder.random.random", lambda: 0.9)
    # Force random.choice to return the first pivot
    monkeypatch.setattr(
        "app.services.prompt_builder.random.choice", lambda seq: seq[0]
    )
    result = _choose_followup_question([_section("Python")])
    assert result == _PIVOT_QUESTIONS[0]


# ---------------------------------------------------------------------------
# build_chat_prompt
# ---------------------------------------------------------------------------


def test_build_returns_empty_string_when_no_sections():
    result = build_chat_prompt("What is your experience?", [], "")
    assert result == ""


def test_build_contains_user_message():
    sections = [_section("Built REST APIs with FastAPI")]
    prompt = build_chat_prompt("Tell me about your APIs", sections, "")
    assert "Tell me about your APIs" in prompt


def test_build_contains_all_section_contents():
    sections = [
        _section("FastAPI expert"),
        _section("Led a team of 5"),
    ]
    prompt = build_chat_prompt("Skills?", sections, "")
    assert "- FastAPI expert" in prompt
    assert "- Led a team of 5" in prompt


def test_build_contains_history_context():
    sections = [_section("Python dev")]
    history = "User: hi\nAssistant: hello\n\n"
    prompt = build_chat_prompt("More?", sections, history)
    assert history in prompt


def test_build_contains_followup_instruction(monkeypatch):
    monkeypatch.setattr("app.services.prompt_builder.random.random", lambda: 0.1)
    sections = [_section("content")]
    prompt = build_chat_prompt("question", sections, "")
    assert "End your response with one follow-up question" in prompt


def test_build_empty_history_still_renders():
    sections = [_section("content")]
    prompt = build_chat_prompt("question", sections, "")
    # Should not raise and prompt must be non-empty
    assert len(prompt) > 50


def test_build_acts_as_cv_owner():
    sections = [_section("content")]
    prompt = build_chat_prompt("who are you?", sections, "")
    assert "Act as me" in prompt
