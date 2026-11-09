from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, SystemMessage

from app.agents.schemas import RouteResult
from app.core.config import settings
from app.core.logging import get_logger
from app.utils.small_talk_recognition import match_social_intent, response_by_social_intent

logger = get_logger(__name__)

SYSTEM_PROMPT = """
你是保险商城智能客服的意图识别节点，请判断用户消息应该交给哪个工作流。

intent只能从以下选项中选择：
- recommendation_plan：保险产品咨询、产品条款、保险推荐、方案管理和投保咨询
- claim：报案、理赔责任、理赔材料、理赔流程和理赔进度
- human_handoff：投诉、高风险问题或用户明确要求人工服务
- chitchat：与保险业务无关的普通聊天
- fallback：无法判断用户意图
""".strip()


class IntentRouter:

    def __init__(self) -> None:
        model = init_chat_model(
            model=settings.llm.chat_model,  # 意图识别不需要大模型，工作中这里用工公司的小模型即可
            model_provider="deepseek",
            api_key=settings.llm.api_key,
            extra_body={"thinking": {"type": "disabled"}},
        )
        # 给模型绑定结构化输出，让模型按照要求输出路由结果
        self.route_model = model.with_structured_output(RouteResult)

    async def route(
            self,
            query: str,  # 本轮用户的提问
            context: str  # 历史对话的上下文（可以包含：上一轮的工作流名字、上一轮AI回复的消息）
    ) -> RouteResult:
        try:
            # 寒暄识别（基于规则 -> 正则表达式）
            intent = match_social_intent(query)
            if intent:
                # 返回固定的寒暄回复
                return response_by_social_intent(intent)
            # 基于模型的意图识别
            result: RouteResult = await self.route_model.ainvoke([
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(f"历史对话信息：{context}\n 用户本轮消息：{query}\n"),
            ])
        except:
            result = RouteResult(
                intent="fallback",
                reason="模型意图识别失败",
            )
        logger.info(f"意图识别完成，intent: {result.intent}, reason: {result.reason}")
        return result


intent_router = IntentRouter()
