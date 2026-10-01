from html.parser import HTMLParser
from pathlib import Path
import unittest


INDEX_HTML = Path(__file__).resolve().parents[1] / "index.html"


class ExperienceParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.heading = ""
        self.roles = []
        self.metrics = {}
        self.image_count = 0
        self._in_experience = False
        self._role = None
        self._capture_tag = None
        self._capture_field = None
        self._text_parts = []
        self._metric_company = None
        self._metric_group_depth = 0
        self._metric_tile_depth = None
        self._metric_parts = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = set(attributes.get("class", "").split())

        if tag == "section" and attributes.get("id") == "experience":
            self._in_experience = True
            return
        if not self._in_experience:
            return

        if tag == "img":
            self.image_count += 1
        elif tag == "h2":
            self._start_capture(tag, "heading")
        elif tag == "article" and "experience-role" in classes:
            self._role = {
                "title": "",
                "company": "",
                "dates": "",
                "location": "",
                "summary": "",
                "bullets": [],
            }
        elif self._role is not None:
            if tag == "h3" and "role-title" in classes:
                self._start_capture(tag, "title")
            elif tag == "p" and "role-company" in classes:
                self._start_capture(tag, "company")
            elif tag == "time" and "role-dates" in classes:
                self._start_capture(tag, "dates")
            elif tag == "span" and "role-location" in classes:
                self._start_capture(tag, "location")
            elif tag == "p" and "role-summary" in classes:
                self._start_capture(tag, "summary")
            elif tag == "li" and "experience-bullet" in classes:
                self._start_capture(tag, "bullet")

        if tag == "div" and "company-metrics" in classes:
            self._metric_company = attributes["data-company"]
            self.metrics[self._metric_company] = []
            self._metric_group_depth = 1
        elif self._metric_group_depth:
            if tag == "div":
                self._metric_group_depth += 1
                if "metric-tile" in classes:
                    self._metric_tile_depth = self._metric_group_depth
                    self._metric_parts = []

    def handle_data(self, data):
        if self._capture_tag is not None:
            self._text_parts.append(data)
        if self._metric_tile_depth is not None:
            self._metric_parts.append(data)

    def handle_endtag(self, tag):
        if tag == self._capture_tag:
            text = " ".join("".join(self._text_parts).split())
            if self._capture_field == "heading":
                self.heading = text
            elif self._capture_field == "bullet":
                self._role["bullets"].append(text)
            else:
                self._role[self._capture_field] = text
            self._capture_tag = None
            self._capture_field = None
            self._text_parts = []

        if tag == "article" and self._role is not None:
            self.roles.append(self._role)
            self._role = None

        if tag == "div" and self._metric_group_depth:
            if self._metric_tile_depth == self._metric_group_depth:
                metric = " ".join("".join(self._metric_parts).split())
                self.metrics[self._metric_company].append(metric)
                self._metric_tile_depth = None
                self._metric_parts = []
            self._metric_group_depth -= 1
            if self._metric_group_depth == 0:
                self._metric_company = None

        if tag == "section" and self._in_experience:
            self._in_experience = False

    def _start_capture(self, tag, field):
        self._capture_tag = tag
        self._capture_field = field
        self._text_parts = []


class ExperienceContentTest(unittest.TestCase):
    def setUp(self):
        self.parser = ExperienceParser()
        self.parser.feed(INDEX_HTML.read_text(encoding="utf-8"))

    def test_roles_lead_with_resume_identity_and_exact_bullets(self):
        self.assertEqual(self.parser.heading, "Relevant Professional Experience")
        self.assertEqual(self.parser.image_count, 0)
        self.assertEqual(
            self.parser.roles,
            [
                {
                    "title": "Backend Software Engineer (AI Platform)",
                    "company": "Hewlett Packard Enterprise",
                    "dates": "Mar 2026 - Present",
                    "location": "Houston, TX",
                    "summary": "",
                    "bullets": [
                        "Built a database intelligence platform in Python with AI agents that processes 30M+ logs per day, cutting manual database troubleshooting by over 90%, by automating root-cause analysis and routing every corrective action through human approval.",
                        "Automated dev and test environment setup for 30+ deployments per month, shrinking setup time from 3 hours to 15 minutes per deployment, by building CI/CD pipelines in Jenkins and Docker.",
                    ],
                },
                {
                    "title": "Backend Software Engineering Intern",
                    "company": "Hewlett Packard Enterprise",
                    "dates": "May 2025 - Dec 2025",
                    "location": "Houston, TX",
                    "summary": "",
                    "bullets": [
                        "Established observability across 1,000+ production database clusters, resulting in 60% faster detection of performance issues, by turning log and query signals into alerts and stress testing slow queries in SQL.",
                        "Built a RAG assistant over 20,000+ internal database runbooks for HPE's database engineers, saving 30 minutes on each troubleshooting lookup, by indexing the runbooks into Weaviate and grounding each answer in their text.",
                    ],
                },
                {
                    "title": "Machine Learning Research Assistant",
                    "company": "Texas A&M University",
                    "dates": "Nov 2024 - Dec 2025",
                    "location": "College Station, TX",
                    "summary": "Biomedical machine learning research on pulmonary blood-flow modeling and medical imaging.",
                    "bullets": [
                        "Developed a transformer model that estimates pulmonary artery blood pressure across 200+ patient vessel models without an invasive procedure, producing results accepted at ASME SB3C 2025, by training on 3D vessel geometry and boundary conditions to an R² of 0.95.",
                        "Trained a U-Net model that segments 500+ CT scans into 3D pulmonary artery reconstructions, saving 2 weeks of manual anatomy prep per patient case, by automating segmentation ahead of blood-flow simulation.",
                    ],
                },
                {
                    "title": "Software Engineer (Backend)",
                    "company": "Affinsys AI",
                    "dates": "Sep 2021 - Jul 2024",
                    "location": "",
                    "summary": "Conversational AI platform for banks, insurers, and telecoms (BankBuddy.ai, InsureBuddy.ai, TelcoBuddy.ai) with clients including Mastercard and Dubai Islamic Bank across 20 countries.",
                    "bullets": [
                        "Productionized multilingual BERT pipelines for intent and entity classification serving 350K+ users, reducing compute use by over 60%, by optimizing model inference and serving predictions through Django REST APIs.",
                        "Replaced rule-based chatbot pipelines with a RAG platform across 50+ client chatbots, lowering model retraining effort by 80%, by pairing semantic search in Qdrant with LLM-generated responses.",
                        "Deployed 5 LLM agents to in-house servers and AWS, leading to 40% lower inference cost, by setting up model serving on EC2 and Lambda with S3 storage.",
                        "Led a team of 5 engineers to ship a real-time voice assistant for bank customer calls in 4 months, cutting response latency by 30%, by running half-duplex speech recognition and text-to-speech as streaming microservices.",
                        "Integrated sentiment analysis into 30+ multilingual client chatbots, lifting customer retention by 20% YoY, by personalizing each response to the customer's tone and context.",
                    ],
                },
            ],
        )

    def test_company_metrics_are_evidence_based(self):
        self.assertEqual(
            self.parser.metrics,
            {
                "Hewlett Packard Enterprise": [
                    "30M+ database logs read per day",
                    "Over 90% less manual troubleshooting",
                    "1,000+ production database clusters monitored",
                ],
                "Affinsys AI": [
                    "350K+ users served",
                    "80% less model retraining effort",
                    "5 engineers led",
                ],
                "Texas A&M University": [
                    "200+ patient vessel models",
                    "2 weeks of manual prep saved per patient case",
                    "Accepted at ASME SB3C 2025",
                ],
            },
        )


if __name__ == "__main__":
    unittest.main()
