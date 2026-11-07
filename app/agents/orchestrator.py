from langchain_core.messages import AIMessage, BaseMessage
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command

from app.agents.intent_router import intent_router
from app.agents.schemas import InsuranceAgentState, Intent


# 一、定义节点

# 1.路由节点
async def route_node(state: InsuranceAgentState) -> Command[Intent]:
    """意图识别节点，后续再完善"""

    # 1.获取active_workflow，也就是上一轮会话的工作流
    previous_workflow = state.get("active_workflow", "")
    # 获取用户本轮提问
    messages = state.get("messages")
    user_query = messages[-1]
    # 上下文
    previous_ai_message = find_previous_ai_message(messages)
    content = f"上一轮工作流：{previous_workflow} \n 上一轮AI回复的信息：{previous_ai_message}"
    # 2.调用路由工具，完成意图识别
    result = await intent_router.route(user_query, content)

    return Command(
        update={
            "previous_workflow": previous_workflow,
            "active_workflow": result.intent
        },
        goto=result.intent
    )


def find_previous_ai_message(messages: list[BaseMessage]) -> str:
    """查找本轮用户消息之前最近一条可展示的AI回复"""

    for message in reversed(messages[:-1]):
        # 跳过非AIMessage
        if not isinstance(message, AIMessage):
            continue
        # 跳过工具消息
        if message.tool_calls:
            continue
        # 如果是正常AIMessage，直接返回
        if message.text:
            return message.text
    # 如果是空消息
    return ""


# 2.闲聊节点
async def chitchat_node(state: InsuranceAgentState) -> dict:
    return {"messages": [AIMessage("你好，我是测试代码，今天想聊点什么？")]}


# 3.保险推荐节点
async def recommendation_node(state: InsuranceAgentState) -> dict:
    return {"messages": [AIMessage("保险推荐工作流暂未接入。")]}


# 4.理赔节点
async def claim_node(state: InsuranceAgentState) -> dict:
    return {"messages": [AIMessage("理赔工作流暂未接入。")]}


# 5.人工节点
def human_handoff_node(state: InsuranceAgentState) -> dict:
    return {"messages": [AIMessage("已记录转人工请求，后续可接入人工客服系统。")]}


# 6.fallback节点
def fallback_node(state: InsuranceAgentState) -> dict:
    return {"messages": [AIMessage("我还不能确定你的需求，请说明是想咨询保险、推荐方案还是办理理赔。")]}


# 二、定义主Graph
def init_insurance_agent(checkpointer: AsyncPostgresSaver):
    """初始化保险顾问主Graph"""

    builder = StateGraph(InsuranceAgentState)
    builder.add_node("route", route_node)
    builder.add_node("chitchat", chitchat_node)
    builder.add_node("recommendation_plan", recommendation_node)
    builder.add_node("claim", claim_node)
    builder.add_node("human_handoff", human_handoff_node)
    builder.add_node("fallback", fallback_node)

    builder.add_edge(START, "route")
    builder.add_edge("chitchat", END)
    builder.add_edge("recommendation_plan", END)
    builder.add_edge("claim", END)
    builder.add_edge("human_handoff", END)
    builder.add_edge("fallback", END)

    return builder.compile(checkpointer=checkpointer)
