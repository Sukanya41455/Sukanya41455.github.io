from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
STYLE_CSS = ROOT / "style.css"
MEDIAQUERIES_CSS = ROOT / "mediaqueries.css"


def declarations_for(css, selector):
    match = re.search(rf"{re.escape(selector)}\s*\{{(?P<body>[^}}]*)\}}", css)
    if match is None:
        return {}

    return {
        name.strip(): value.strip()
        for name, value in (
            declaration.split(":", 1)
            for declaration in match.group("body").split(";")
            if ":" in declaration
        )
    }


class EducationAlignmentTest(unittest.TestCase):
    def test_desktop_titles_reserve_srm_two_line_spacing(self):
        declarations = declarations_for(
            STYLE_CSS.read_text(encoding="utf-8"), ".education-card h3"
        )

        self.assertEqual(declarations.get("min-height"), "2lh")

    def test_stacked_titles_return_to_natural_height(self):
        responsive_css = MEDIAQUERIES_CSS.read_text(encoding="utf-8")
        mobile_rules = responsive_css.split(
            "@media screen and (max-width: 900px)", 1
        )[1].split("@media screen and (max-width: 600px)", 1)[0]
        declarations = declarations_for(mobile_rules, ".education-card h3")

        self.assertEqual(declarations.get("min-height"), "auto")


if __name__ == "__main__":
    unittest.main()
