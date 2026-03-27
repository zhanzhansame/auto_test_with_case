import unittest
from io import BytesIO

from utils.file_validators import validate_upload_file


class DummyFile:
    def __init__(self, filename, content_type, data):
        self.filename = filename
        self.content_type = content_type
        self.stream = BytesIO(data)

    def read(self):
        self.stream.seek(0)
        return self.stream.read()


class TestFileValidators(unittest.TestCase):
    def test_validate_markdown_file(self):
        file_obj = DummyFile("req.md", "text/markdown", b"# hello")
        ext = validate_upload_file(file_obj)
        self.assertEqual(ext, "md")

    def test_validate_pdf_file(self):
        file_obj = DummyFile("req.pdf", "application/pdf", b"%PDF-1.4")
        ext = validate_upload_file(file_obj)
        self.assertEqual(ext, "pdf")

    def test_reject_unsupported_extension(self):
        file_obj = DummyFile("req.docx", "application/vnd.openxmlformats-officedocument", b"x")
        with self.assertRaises(ValueError):
            validate_upload_file(file_obj)


if __name__ == "__main__":
    unittest.main()
