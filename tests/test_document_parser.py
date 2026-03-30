import unittest

try:
    from utils.document_parser import parse_document_text, split_markdown_document

    _HAS_DOC_PARSER_DEPS = True
except ModuleNotFoundError as exc:
    parse_document_text = None
    split_markdown_document = None
    _HAS_DOC_PARSER_DEPS = False
    _DOC_PARSER_IMPORT_ERROR = exc


@unittest.skipUnless(_HAS_DOC_PARSER_DEPS, f"缺少文档解析依赖：{_DOC_PARSER_IMPORT_ERROR}")
class TestDocumentParser(unittest.TestCase):
    def test_split_markdown_document(self):
        md = "# 模块A\n## 子模块B\n### 功能C\n这里是需求描述"
        blocks = split_markdown_document(md)
        self.assertTrue(len(blocks) >= 1)
        self.assertEqual(blocks[0]["level1_module"], "模块A")

    def test_parse_document_text_pdf_mode(self):
        plain = "第一段需求。第二段需求。第三段需求。"
        blocks = parse_document_text(plain, "pdf_text")
        self.assertTrue(len(blocks) >= 1)
        self.assertIn("content", blocks[0])

    def test_parse_document_text_invalid_type(self):
        with self.assertRaises(ValueError):
            parse_document_text("abc", "docx")


if __name__ == "__main__":
    unittest.main()
