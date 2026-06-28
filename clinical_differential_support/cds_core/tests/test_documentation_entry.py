from django.conf import settings
from django.test import SimpleTestCase


class DocumentationEntryTests(SimpleTestCase):
    def test_primary_chinese_docs_use_windows_readable_utf8_bom(self):
        for filename in ["README.md", "QUICK_START.zh.md"]:
            path = settings.BASE_DIR / filename
            with self.subTest(filename=filename):
                self.assertTrue(path.exists())
                self.assertTrue(path.read_bytes().startswith(b"\xef\xbb\xbf"))

    def test_quick_start_leads_with_next_action_and_open_urls(self):
        quick_start = settings.BASE_DIR / "QUICK_START.zh.md"

        content = quick_start.read_text(encoding="utf-8-sig")

        self.assertIn("下一步", content)
        self.assertIn("步驟 1/6", content)
        self.assertIn("步驟 6/6", content)
        self.assertIn("現在做這個", content)
        self.assertIn("http://127.0.0.1:8000/review/login/", content)
        self.assertIn("Final Verification Gate", content)
