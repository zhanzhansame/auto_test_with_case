import os


MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {"md", "markdown", "pdf"}
ALLOWED_MIME_TYPES = {
    "md": {"text/markdown", "text/plain", "application/octet-stream"},
    "markdown": {"text/markdown", "text/plain", "application/octet-stream"},
    "pdf": {"application/pdf", "application/octet-stream"},
}


def get_extension(filename):
    _, ext = os.path.splitext(filename or "")
    return ext.lower().lstrip(".")


def validate_upload_file(file_storage, max_size=MAX_UPLOAD_SIZE_BYTES):
    if not file_storage:
        raise ValueError("缺少上传文件 file")

    filename = file_storage.filename or ""
    if not filename:
        raise ValueError("文件名不能为空")

    ext = get_extension(filename)
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"不支持的文件类型: .{ext}")

    content_type = (file_storage.content_type or "").lower()
    if content_type and content_type not in ALLOWED_MIME_TYPES.get(ext, set()):
        raise ValueError(f"文件 MIME 类型不支持: {content_type}")

    file_storage.stream.seek(0, os.SEEK_END)
    size = file_storage.stream.tell()
    file_storage.stream.seek(0)
    if size <= 0:
        raise ValueError("文件内容为空")
    if size > max_size:
        raise ValueError(f"文件大小超过限制，最大允许 {max_size // (1024 * 1024)}MB")

    return ext
