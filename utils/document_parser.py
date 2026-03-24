from langchain.text_splitter import MarkdownHeaderTextSplitter


def split_markdown_document(markdown_text):
    """
    将 Markdown 格式的需求文档按标题层级拆分
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
        parsed_content.append({
            "id": i,
            "level1_module": doc.metadata.get("一级模块", "无"),
            "level2_module": doc.metadata.get("二级子模块", "无"),
            "level3_function": doc.metadata.get("三级功能点", "无"),
            "content": doc.page_content
        })

    return parsed_content