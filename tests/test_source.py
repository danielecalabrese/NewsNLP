import pytest

from newsnlp.models.source import Source


def test_source_with_name_is_valid():
    source = Source(name="BBC")

    assert source.name == "BBC"
    assert source.section is None


def test_source_with_section_is_valid():
    source = Source(name="BBC", section="economy")

    assert source.name == "BBC"
    assert source.section == "economy"


def test_source_name_cannot_be_empty():
    with pytest.raises(ValueError):
        Source(name="")