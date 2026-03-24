from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.document_parser import split_markdown_document
from services.llm_service import generate_test_points

app = Flask(__name__)
# 允许跨域请求，方便前端联调
CORS(app)


@app.route('/api/analyze_document', methods=['POST'])
def analyze_document():
    """
    接口 1：接收 Markdown 文档，返回拆分后的模块列表
    """
    data = request.json
    if not data or 'content' not in data:
        return jsonify({"error": "缺少文档内容 content 参数"}), 400

    markdown_content = data['content']
    parsed_blocks = split_markdown_document(markdown_content)

    return jsonify({
        "status": "success",
        "total_blocks": len(parsed_blocks),
        "data": parsed_blocks
    })


@app.route('/api/generate_points', methods=['POST'])
def generate_points():
    """
    接口 2：接收特定的文本块，调用大模型生成测试点
    """
    data = request.json
    context = data.get('content', '')
    module_name = data.get('module', '未知模块')
    function_name = data.get('function', '未知功能点')

    if not context:
        return jsonify({"error": "上下文内容不能为空"}), 400

    # 调用 LLM 生成测试点
    test_points = generate_test_points(context, module_name, function_name)

    return jsonify({
        "status": "success",
        "data": test_points
    })


if __name__ == '__main__':
    # 启动服务，默认端口 5000
    app.run(host='0.0.0.0', port=5000, debug=True)