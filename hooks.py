"""
https://www.mkdocs.org/dev-guide/plugins/#events
"""

import pathlib
from typing import Literal

HERE = pathlib.Path(__file__).parent
# There's probably a better way to do this 🤷
REPLACEMENTS = {
    "[docs/user_guide.md](docs/user_guide.md)": "[user_guide.md](user_guide.md)",
    "[contribution guide](docs/contributing.md)": "[contribution guide](contributing.md)",
    '<span align="center">': '<p style="text-align: center;">',
    "</span>": "</p>",
}


def on_startup(
    command: Literal["build", "gh-deploy", "serve"],
    dirty: bool,
) -> None:
    """
    Copy the project readme into the ``docs`` directory.
    """

    source_path = HERE.parent / "README.md"
    target_path = HERE / "index.md"

    target_path.touch(exist_ok=True)
    content = source_path.read_text()
    for old, new in REPLACEMENTS.items():
        content = content.replace(old, new)

    target_path.write_text(content)
