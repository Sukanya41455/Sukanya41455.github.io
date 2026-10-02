from html.parser import HTMLParser
from pathlib import Path
import unittest


INDEX_HTML = Path(__file__).resolve().parents[1] / "index.html"


class ProductOutcomesParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cards = []
        self._card = None
        self._capture_title = False
        self._capture_outcome = False
        self._title_parts = []
        self._outcome_parts = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = set(attributes.get("class", "").split())

        if tag == "article" and "project-card" in classes:
            self._card = {
                "title": "",
                "outcomes": [],
                "has_description": False,
                "image_src": "",
                "github_href": "",
            }
        elif self._card is not None and tag == "img" and "project-img" in classes:
            self._card["image_src"] = attributes.get("src", "")
        elif (
            self._card is not None
            and tag == "a"
            and "github.com" in attributes.get("href", "")
        ):
            self._card["github_href"] = attributes["href"]
        elif self._card is not None and tag == "h3" and "project-title" in classes:
            self._capture_title = True
            self._title_parts = []
        elif self._card is not None and tag == "p" and "project-description" in classes:
            self._card["has_description"] = True
        elif self._card is not None and tag == "li" and "project-outcome" in classes:
            self._capture_outcome = True
            self._outcome_parts = []

    def handle_data(self, data):
        if self._capture_title:
            self._title_parts.append(data)
        if self._capture_outcome:
            self._outcome_parts.append(data)

    def handle_endtag(self, tag):
        if tag == "h3" and self._capture_title:
            self._card["title"] = " ".join("".join(self._title_parts).split())
            self._capture_title = False
        elif tag == "li" and self._capture_outcome:
            outcome = " ".join("".join(self._outcome_parts).split())
            self._card["outcomes"].append(outcome)
            self._capture_outcome = False
        elif tag == "article" and self._card is not None:
            self.cards.append(self._card)
            self._card = None


class ProductOutcomesTest(unittest.TestCase):
    def test_each_product_presents_impact_without_a_description(self):
        parser = ProductOutcomesParser()
        parser.feed(INDEX_HTML.read_text(encoding="utf-8"))

        self.assertEqual(len(parser.cards), 5)
        for card in parser.cards:
            with self.subTest(product=card["title"]):
                self.assertFalse(card["has_description"])
                self.assertGreater(len(card["outcomes"]), 0)

    def test_each_product_exposes_supplied_impact_as_list_items(self):
        parser = ProductOutcomesParser()
        parser.feed(INDEX_HTML.read_text(encoding="utf-8"))

        outcomes_by_title = {
            card["title"]: card["outcomes"] for card in parser.cards
        }

        self.assertEqual(len(outcomes_by_title["CaseTrace"]), 2)
        self.assertIn("50+ typed payment-investigation workflows", outcomes_by_title["CaseTrace"][0])
        self.assertIn("30+ risky actions stopped in testing", outcomes_by_title["CaseTrace"][1])

        self.assertEqual(len(outcomes_by_title["MedReL: Radiology Report Generation"]), 1)
        self.assertIn("4,000+ chest X-rays", outcomes_by_title["MedReL: Radiology Report Generation"][0])

        self.assertEqual(len(outcomes_by_title["Howdy Orgs"]), 1)
        self.assertIn("1,200+ student organizations", outcomes_by_title["Howdy Orgs"][0])

        self.assertEqual(len(outcomes_by_title["LLM Bias Detection Framework"]), 1)
        self.assertIn("60 model outputs across 6 demographic bias categories", outcomes_by_title["LLM Bias Detection Framework"][0])

    def test_streamforge_card_uses_supplied_content_and_links(self):
        parser = ProductOutcomesParser()
        parser.feed(INDEX_HTML.read_text(encoding="utf-8"))

        self.assertEqual(
            parser.cards[0]["title"],
            "StreamForge: Real-time Marketplace Analytics Platform",
        )

        cards_by_title = {card["title"]: card for card in parser.cards}
        title = "StreamForge: Real-time Marketplace Analytics Platform"
        self.assertIn(title, cards_by_title)
        streamforge = cards_by_title[title]

        self.assertEqual(streamforge["image_src"], "./assets/project_streamforge.png")
        self.assertEqual(
            streamforge["github_href"],
            "https://github.com/Sukanya41455/StreamForge",
        )
        self.assertEqual(len(streamforge["outcomes"]), 1)
        self.assertIn("250+ events/sec", streamforge["outcomes"][0])
        self.assertIn("stream recovery in <30 seconds", streamforge["outcomes"][0])
        self.assertIn("API p95 latency below 300 ms", streamforge["outcomes"][0])


if __name__ == "__main__":
    unittest.main()
