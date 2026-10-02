from pathlib import Path
import re
import unittest


STYLE_CSS = Path(__file__).resolve().parents[1] / "style.css"
MEDIAQUERIES_CSS = Path(__file__).resolve().parents[1] / "mediaqueries.css"


def declarations_for(css, selector):
    match = re.search(rf"{re.escape(selector)}\s*\{{([^}}]+)\}}", css)
    if match is None:
        return {}

    return {
        property_name.strip(): value.strip()
        for property_name, value in re.findall(r"([\w-]+)\s*:\s*([^;]+);", match.group(1))
    }


def block_for(css, header):
    start = css.find(header)
    if start == -1:
        return ""

    opening_brace = css.find("{", start)
    depth = 0
    for index in range(opening_brace, len(css)):
        if css[index] == "{":
            depth += 1
        elif css[index] == "}":
            depth -= 1
            if depth == 0:
                return css[opening_brace + 1 : index]

    return ""


class ProjectLayoutTest(unittest.TestCase):
    def test_odd_final_project_card_uses_the_centered_desktop_grid_tracks(self):
        css = MEDIAQUERIES_CSS.read_text(encoding="utf-8")
        wide_layout_css = block_for(css, "@media screen and (min-width: 901px)")
        grid_declarations = declarations_for(wide_layout_css, ".project-grid")
        card_declarations = declarations_for(wide_layout_css, ".project-card")
        declarations = declarations_for(
            wide_layout_css,
            ".project-card:last-child:nth-child(odd)",
        )

        self.assertEqual(grid_declarations.get("grid-template-columns"), "repeat(4, minmax(0, 1fr))")
        self.assertEqual(card_declarations.get("grid-column"), "span 2")
        self.assertEqual(declarations.get("grid-column"), "2 / span 2")


if __name__ == "__main__":
    unittest.main()
