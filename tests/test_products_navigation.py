from html.parser import HTMLParser
from pathlib import Path
import unittest


INDEX_HTML = Path(__file__).resolve().parents[1] / "index.html"


class PortfolioHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []
        self.headings = []
        self._current_link = None
        self._current_heading = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if element_id := attributes.get("id"):
            self.ids.add(element_id)
        if tag == "a":
            self._current_link = {
                "href": attributes.get("href"),
                "text": "",
            }
        if tag == "h2":
            self._current_heading = ""

    def handle_data(self, data):
        if self._current_link is not None:
            self._current_link["text"] += data
        if self._current_heading is not None:
            self._current_heading += data

    def handle_endtag(self, tag):
        if tag == "a" and self._current_link is not None:
            self._current_link["text"] = self._current_link["text"].strip()
            self.links.append(self._current_link)
            self._current_link = None
        if tag == "h2" and self._current_heading is not None:
            self.headings.append(self._current_heading.strip())
            self._current_heading = None


class ProductsNavigationTest(unittest.TestCase):
    def test_products_navigation_targets_products_section(self):
        parser = PortfolioHTMLParser()
        parser.feed(INDEX_HTML.read_text(encoding="utf-8"))

        product_links = [link for link in parser.links if link["text"] == "Products"]
        project_links = [link for link in parser.links if link["text"] == "Projects"]

        self.assertTrue(product_links, "Expected Products navigation links")
        self.assertTrue(
            all(link["href"] == "#products" for link in product_links),
            "Every Products navigation link should target #products",
        )
        self.assertFalse(project_links, "Old Projects navigation labels should be removed")
        self.assertIn("products", parser.ids)
        self.assertIn("Products", parser.headings)


if __name__ == "__main__":
    unittest.main()
