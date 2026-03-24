import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# 初始化大模型 (这里以兼容 OpenAI API 格式的模型为例，如 GLM, DeepSeek 等)
# 实际使用时，建议将 API Key 放在环境变量或 .env 文件中
llm = ChatOpenAI(
    model="glm-4",  # 替换为你实际使用的模型名称，如 glm-4 或 deepseek-chat
    openai_api_key=os.environ.get("OPENAI_API_KEY", "your_api_key_here"),
    openai_api_base=os.environ.get("OPENAI_API_BASE", "https://open.bigmodel.cn/api/paas/v4/")
)

# 初始化 JSON 解析器
json_parser = JsonOutputParser()


def generate_test_points(context, module_name, function_name):
    """
    调用大模型，根据上下文生成结构化测试点
    """
    # 按照你方案中的 Prompt 进行构建
    template = """
    你是一名专业软件测试工程师。
    精通软件测试理论和实践。
    熟悉软件测试方法、工具和技术。
    能够根据需求规格说明书、用户手册和技术文档，进行测试用例设计。
    具备良好的沟通能力和团队合作精神。
    请根据以下上下文，分析出标准、清晰、可直接用于表格展示的测试点。

    上下文: {context}
    模块: {module}
    功能点: {function}

    要求：
    1. 所有测试点必须以「验证」二字开头，格式固定为：验证 + 具体测试内容。
    2. 测试点必须**仅从当前提供的功能描述文本中提取**，禁止凭空编造、扩展或联想。
    3. 每个测试点是独立、可执行的测试项。
    4. 描述简洁，长度不超过20个字符。
    5. 只返回纯JSON，不要任何多余文字、解释、符号。
    6. 若当前文本中无任何可提取的测试场景，必须返回空数组 `[]`，禁止乱生成。
    7. 返回格式必须严格为以下 JSON 结构：
    {{
        "testpoint": {{
            "{function}": ["验证xxx", "验证xxx"]
        }}
    }}
    """

    prompt = PromptTemplate(
        template=template,
        input_variables=["context", "module", "function"],
    )

    # 构建 LangChain 管道 (LCEL 语法)
    chain = prompt | llm | json_parser

    try:
        # 执行调用
        result = chain.invoke({
            "context": context,
            "module": module_name,
            "function": function_name
        })
        return result
    except Exception as e:
        print(f"大模型调用失败: {e}")
        # 降级处理：返回空结构，避免整个流程崩溃
        return {"testpoint": {function_name: []}}