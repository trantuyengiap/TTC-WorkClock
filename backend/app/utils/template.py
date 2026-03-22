from __future__ import annotations


def render_template(template: str, context: dict[str, object]) -> str:
    rendered = template
    for key, value in context.items():
        rendered = rendered.replace(f'{{{key}}}', str(value))
    return rendered
