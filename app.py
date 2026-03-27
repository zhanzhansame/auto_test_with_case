import logging

from flask import Flask, jsonify, request
from flask_cors import CORS

from common.logger import init_logger
from services.llm_service import LLMServiceError, generate_test_points
from utils.document_parser import parse_document_text
from utils.file_validators import validate_upload_file
from utils.pdf_parser import extract_text_from_pdf_bytes

init_logger()
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)


def success_response(data, **extra):
    payload = {"status": "success", "data": data}
    payload.update(extra)
    return jsonify(payload), 200


def error_response(code, message, status_code=400):
    return jsonify({"status": "error", "error": {"code": code, "message": message}}), status_code


@app.errorhandler(Exception)
def handle_unexpected_error(exc):
    logger.exception("Unhandled exception: %s", exc)
    return error_response("internal_error", "服务内部错误，请稍后重试", 500)


@app.route("/api/analyze_document", methods=["POST"])
def analyze_document():
    """
    接收 markdown 文本，返回拆分后的模块列表。
    """
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error_response("invalid_payload", "请求体必须是 JSON 对象", 400)

    content = data.get("content", "")
    if not isinstance(content, str) or not content.strip():
        return error_response("invalid_content", "缺少文档内容 content 参数", 400)

    parsed_blocks = parse_document_text(content, "md")
    return success_response(parsed_blocks, total_blocks=len(parsed_blocks))


@app.route("/api/analyze_file", methods=["POST"])
def analyze_file():
    """
    接收上传文件（md/pdf），返回拆分后的模块列表。
    """
    uploaded_file = request.files.get("file")
    try:
        ext = validate_upload_file(uploaded_file)
    except ValueError as exc:
        return error_response("invalid_file", str(exc), 400)

    file_bytes = uploaded_file.read()

    if ext in {"md", "markdown"}:
        try:
            content = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return error_response("decode_error", "Markdown 文件必须是 UTF-8 编码", 400)
        parsed_blocks = parse_document_text(content, "md")
    elif ext == "pdf":
        try:
            extracted_text = extract_text_from_pdf_bytes(file_bytes)
        except ValueError as exc:
            return error_response("pdf_extract_failed", str(exc), 400)
        parsed_blocks = parse_document_text(extracted_text, "pdf_text")
    else:
        return error_response("unsupported_file_type", f"不支持的文件类型: {ext}", 400)

    return success_response(parsed_blocks, total_blocks=len(parsed_blocks), file_type=ext)


@app.route("/api/generate_points", methods=["POST"])
def generate_points():
    """
    接收文本块，调用大模型生成测试点。
    """
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error_response("invalid_payload", "请求体必须是 JSON 对象", 400)

    context = (data.get("content") or "").strip()
    module_name = data.get("module", "未知模块")
    function_name = data.get("function", "未知功能点")

    if not context:
        return error_response("invalid_content", "上下文内容不能为空", 400)

    try:
        test_points = generate_test_points(context, module_name, function_name)
        return success_response(test_points)
    except LLMServiceError as exc:
        return error_response(exc.code, exc.message, 502)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)