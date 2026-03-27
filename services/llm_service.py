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


def _create_llm():
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY 未配置，服务无法启动")

    return ChatOpenAI(
        model=os.environ.get("LLM_MODEL", "glm-4"),
        openai_api_key=api_key,
        openai_api_base=os.environ.get("OPENAI_API_BASE", "https://open.bigmodel.cn/api/paas/v4/"),
        timeout=float(os.environ.get("LLM_TIMEOUT_SECONDS", "30")),
        max_retries=0,
    )


_PROMPT_TEMPLATE = _load_prompt_template()
_PROMPT = PromptTemplate(template=_PROMPT_TEMPLATE, input_variables=["context", "module", "function"])
_JSON_PARSER = JsonOutputParser()
_LLM = _create_llm()


def _classify_error(exc):
    msg = str(exc).lower()
    if "401" in msg or "unauthorized" in msg or "api key" in msg:
        return "llm_auth_failed", "大模型鉴权失败，请检查 API Key"
    if "429" in msg or "rate limit" in msg:
        return "llm_rate_limited", "大模型调用频率受限，请稍后重试"
    if "timed out" in msg or "timeout" in msg:
        return "llm_timeout", "大模型请求超时"
    if "json" in msg or "parse" in msg:
        return "llm_parse_error", "大模型返回结果解析失败"
    return "llm_call_failed", "大模型调用失败"


def _invoke_with_retry(chain, payload):
    retries = int(os.environ.get("LLM_RETRY_TIMES", "2"))
    backoff_seconds = float(os.environ.get("LLM_RETRY_BACKOFF_SECONDS", "1.0"))
    last_exc = None

    for attempt in range(retries + 1):
        try:
            return chain.invoke(payload)
        except Exception as exc:
            last_exc = exc
            logger.warning("LLM invoke failed at attempt %s: %s", attempt + 1, exc)
            if attempt < retries:
                time.sleep(backoff_seconds * (2 ** attempt))

    raise last_exc


def generate_test_points(context, module_name, function_name):
    """
    调用大模型，根据上下文生成结构化测试点。
    """
    chain = _PROMPT | _LLM | _JSON_PARSER
    payload = {"context": context, "module": module_name, "function": function_name}

    try:
        return _invoke_with_retry(chain, payload)
    except Exception as exc:
        code, message = _classify_error(exc)
        logger.exception("LLM 调用异常: %s", exc)
        raise LLMServiceError(code, message) from exc