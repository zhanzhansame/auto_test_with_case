import json
import logging
import os
import time

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


class LLMServiceError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


def _load_prompt_template():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(current_dir, "..", "prompts", "test_points_prompt.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def _load_config():
    """从本地配置文件加载配置"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "..", "config.json")

    if not os.path.exists(config_path):
        raise RuntimeError(f"配置文件不存在: {config_path}")

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config
    except json.JSONDecodeError as e:
        raise RuntimeError(f"配置文件格式错误: {e}")


def _create_llm():
    config = _load_config()

    api_key = config.get("openai_api_key", "").strip()
    if not api_key or api_key == "your_openai_api_key_here":
        raise RuntimeError("OPENAI_API_KEY 未配置，请在 config.json 中设置")

    return ChatOpenAI(
        model=config.get("llm_model", "glm-4"),
        api_key=api_key,
        base_url=config.get("openai_api_base", "https://open.bigmodel.cn/api/paas/v4/"),
        timeout=float(config.get("llm_timeout_seconds", "30")),
        max_retries=0,
    )


_PROMPT_TEMPLATE = _load_prompt_template()
_PROMPT = PromptTemplate(
    template=_PROMPT_TEMPLATE, input_variables=["context", "module", "function"]
)
_JSON_PARSER = JsonOutputParser()
_LLM = _create_llm()


def _classify_error(exc):
    msg = str(exc).lower()
    # 覆盖中文/下划线等情况，避免落入默认分支导致信息不可读
    if (
        "openai_api_key" in msg
        or "未配置" in msg
        or "api key" in msg
        or "unauthorized" in msg
        or "401" in msg
    ):
        return "llm_auth_failed", "未配置 OPENAI_API_KEY，请在启动后端前设置环境变量"
    if "429" in msg or "rate limit" in msg:
        return "llm_rate_limited", "大模型调用频率受限，请稍后重试"
    if "timed out" in msg or "timeout" in msg:
        return "llm_timeout", "大模型请求超时"
    if "json" in msg or "parse" in msg:
        return "llm_parse_error", "大模型返回结果解析失败"
    # 兜底：尽量带上原始异常简要信息（避免前端只看到空泛提示）
    return "llm_call_failed", f"大模型调用失败：{type(exc).__name__}"


def _invoke_with_retry(chain, payload):
    config = _load_config()
    retries = int(config.get("llm_retry_times", "2"))
    backoff_seconds = float(config.get("llm_retry_backoff_seconds", "1.0"))
    last_exc = None

    for attempt in range(retries + 1):
        try:
            return chain.invoke(payload)
        except Exception as exc:
            last_exc = exc
            logger.warning("LLM invoke failed at attempt %s: %s", attempt + 1, exc)
            if attempt < retries:
                time.sleep(backoff_seconds * (2**attempt))

    if last_exc:
        raise last_exc
    raise RuntimeError(
        "LLM chain failed to execute without capturing a specific exception."
    )


def generate_test_points(context, module_name, function_name):
    """
    调用大模型，根据上下文生成结构化测试点。
    """
    global _LLM
    try:
        if _LLM is None:
            _LLM = _create_llm()
    except Exception as exc:
        code, message = _classify_error(exc)
        raise LLMServiceError(code, message) from exc

    chain = _PROMPT | _LLM | _JSON_PARSER
    payload = {"context": context, "module": module_name, "function": function_name}

    try:
        return _invoke_with_retry(chain, payload)
    except Exception as exc:
        code, message = _classify_error(exc)
        logger.exception("LLM 调用异常: %s", exc)
        raise LLMServiceError(code, message) from exc
