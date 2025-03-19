import pytest
from preswald.engine.managers.layout import LayoutManager

def test_add_component_basic():
    layout = LayoutManager()
    component = {"size": 0.5}
    layout.add_component(component)
    assert len(layout.current_row) == 1
    assert layout.current_row_size == 0.5

def test_add_component_with_id():
    layout = LayoutManager()
    component = {"id": "test", "size": 0.5}
    layout.add_component(component)
    assert "test" in layout.seen_ids

def test_add_component_separator():
    layout = LayoutManager()
    component1 = {"size": 0.5}
    component2 = {"type": "separator"}
    component3 = {"size": 0.5}

    layout.add_component(component1)
    layout.add_component(component2)
    layout.add_component(component3)

    assert len(layout.rows) == 1
    assert len(layout.current_row) == 1

def test_add_component_new_row():
    layout = LayoutManager()
    component1 = {"size": 0.6}
    component2 = {"size": 0.6}

    layout.add_component(component1)
    layout.add_component(component2)

    assert len(layout.rows) == 1
    assert len(layout.current_row) == 1

def test_add_component_exact_row():
    layout = LayoutManager()
    component1 = {"size": 0.5}
    component2 = {"size": 0.5}

    layout.add_component(component1)
    layout.add_component(component2)

    assert len(layout.rows) == 1
    assert len(layout.current_row) == 0

def test_finish_current_row():
    layout = LayoutManager()
    component1 = {"size": 0.3}
    component2 = {"size": 0.3}

    layout.add_component(component1)
    layout.add_component(component2)
    layout.finish_current_row()

    assert len(layout.rows) == 1
    assert len(layout.current_row) == 0
    assert layout.current_row_size == 0.0

    # Check flex values
    row = layout.rows[0]
    assert row[0]["flex"] == 0.5
    assert row[1]["flex"] == 0.5

def test_get_layout_empty():
    layout = LayoutManager()
    result = layout.get_layout()
    assert result == []

def test_get_layout_with_components():
    layout = LayoutManager()
    component1 = {"size": 0.3}
    component2 = {"size": 0.3}

    layout.add_component(component1)
    layout.add_component(component2)

    result = layout.get_layout()
    assert len(result) == 1
    assert len(result[0]) == 2

def test_clear_layout():
    layout = LayoutManager()
    component = {"id": "test", "size": 0.5}
    layout.add_component(component)
    layout.finish_current_row()

    layout.clear_layout()

    assert len(layout.rows) == 0
    assert len(layout.current_row) == 0
    assert layout.current_row_size == 0.0
    assert len(layout.seen_ids) == 0

def test_add_component_default_size():
    layout = LayoutManager()
    component = {}  # No size specified
    layout.add_component(component)

    # Default size is 1.0 so row should be finished
    assert len(layout.rows) == 1
    assert len(layout.current_row) == 0
    assert layout.current_row_size == 0.0

def test_add_multiple_components_across_rows():
    layout = LayoutManager()
    components = [
        {"size": 0.4},
        {"size": 0.4},
        {"size": 0.4},
        {"size": 0.4}
    ]

    for component in components:
        layout.add_component(component)

    result = layout.get_layout()
    assert len(result) == 2
    assert len(result[0]) == 2
    assert len(result[1]) == 2

def test_add_component_with_invalid_size():
    layout = LayoutManager()
    component = {"size": "invalid"}
    with pytest.raises(ValueError):
        layout.add_component(component)

def test_add_component_with_zero_size():
    layout = LayoutManager()
    component = {"size": 0}
    layout.add_component(component)
    assert layout.current_row_size == 0.0
    assert len(layout.current_row) == 1

def test_add_component_with_negative_size():
    layout = LayoutManager()
    component = {"size": -0.5}
    layout.add_component(component)
    assert layout.current_row_size == -0.5
    assert len(layout.current_row) == 1
