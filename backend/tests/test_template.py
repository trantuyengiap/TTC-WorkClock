from app.utils.template import render_template


def test_render_template_replaces_variables() -> None:
    result = render_template('Hello {name}, machine {device_name}', {'name': 'Lan', 'device_name': 'MCC-01'})
    assert result == 'Hello Lan, machine MCC-01'
