from html.parser import HTMLParser
from pathlib import Path
import unittest


INDEX_HTML = Path(__file__).resolve().parents[1] / "index.html"


class TechnicalToolkitParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.categories = {}
        self._in_skills = False
        self._current_category = None
        self._capture_heading = None
        self._text_parts = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)

        if tag == "section" and attributes.get("id") == "skills":
            self._in_skills = True
        elif self._in_skills and tag in {"h3", "h4"}:
            self._capture_heading = tag
            self._text_parts = []

    def handle_data(self, data):
        if self._capture_heading is not None:
            self._text_parts.append(data)

    def handle_endtag(self, tag):
        if self._capture_heading == tag:
            heading = " ".join("".join(self._text_parts).split())
            if tag == "h3":
                self._current_category = heading
                self.categories[heading] = []
            elif self._current_category is not None:
                self.categories[self._current_category].append(heading)

            self._capture_heading = None
            self._text_parts = []
        elif tag == "section" and self._in_skills:
            self._in_skills = False
            self._current_category = None


class TechnicalToolkitTest(unittest.TestCase):
    def test_backend_ai_and_delivery_skills_are_grouped_by_specialty(self):
        parser = TechnicalToolkitParser()
        parser.feed(INDEX_HTML.read_text(encoding="utf-8"))

        self.assertIn("Backend", parser.categories)
        self.assertIn("AI Systems", parser.categories)
        self.assertIn("Cloud and Delivery", parser.categories)
        self.assertEqual(
            parser.categories["Backend"],
            [
                "Python",
                "Django",
                "REST APIs",
                "SQL",
                "Microservices",
                "Kafka",
                "PySpark",
                "PostgreSQL",
            ],
        )
        self.assertEqual(
            parser.categories["AI Systems"],
            ["AI Agents", "RAG", "LLMs", "Model Serving", "Vector Databases (Weaviate, Qdrant)", "PyTorch"],
        )
        self.assertEqual(
            parser.categories["Cloud and Delivery"],
            [
                "AWS (EC2, Lambda, S3)",
                "Docker",
                "Jenkins",
                "CI/CD",
                "Observability",
                "Kubernetes",
                "Prometheus",
                "Grafana",
            ],
        )
        self.assertEqual(set(parser.categories), {"Backend", "AI Systems", "Cloud and Delivery"})


if __name__ == "__main__":
    unittest.main()
