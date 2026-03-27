from langchain.text_splitter import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter


def _build_block(idx, content, level1="无", level2="无", level3="无"):
    return {
        "id": idx,
        "level1_module": level1,
        "level2_module": level2,
        "level3_function": level3,
        "content": content.strip(),
    }


def split_markdown_document(markdown_text):
    """
    将 Markdown 格式文档按标题层级拆分。
    """
    # 定义需要拆分的标题层级
    headers_to_split_on = [
        ("#", "一级模块"),
        ("##", "二级子模块"),
        ("###", "三级功能点"),
        ("####", "四级细节")
    ]

    # 初始化分割器
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

    # 执行拆分
    md_header_splits = markdown_splitter.split_text(markdown_text)

    # 将拆分后的 Document 对象转换为字典列表，方便 API 传输和后续处理
    parsed_content = []
    for i, doc in enumerate(md_header_splits):
        parsed_content.append(
            _build_block(
                i,
                doc.page_content,
                doc.metadata.get("一级模块", "无"),
                doc.metadata.get("二级子模块", "无"),
                doc.metadata.get("三级功能点", "无"),
            )
        )
    return parsed_content


def split_plain_text_document(text, chunk_size=1200, chunk_overlap=150):
    """
    将非结构化纯文本分块，适用于 PDF 提取后的文本。
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", "。", ".", "；", ";", "，", ",", " "],
    )
    chunks = splitter.split_text(text)
    parsed_content = []
    for i, chunk in enumerate(chunks):
        if chunk.strip():
            parsed_content.append(_build_block(i, chunk, level1="PDF文档", level2="自动分块", level3=f"片段{i+1}"))
    return parsed_content


def parse_document_text(content, file_type):
    """
    统一解析入口：根据文件类型选择合适的分块策略。
    """
    normalized_type = (file_type or "").strip().lower()
    if normalized_type in {"md", "markdown"}:
        return split_markdown_document(content)
    if normalized_type == "pdf_text":
        return split_plain_text_document(content)
    raise ValueError(f"不支持的文档类型: {file_type}")