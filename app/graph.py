import asyncio
from typing import Dict, Any

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_chat_agent
from pydantic import BaseModel

from app.schemas import ApprovalRequest, ApprovalState, ApprovalResponse
from app.models import User
from app.database import get_session
from app.utils import get_user_by_id


class WorkflowState(ApprovalState):
    pass


def generate_approval_prompt(state: Dict[str, Any]) -> str:
    return (
        f"User {state['user_name']} requests approval for action: {state['action']}. "
        "Respond with 'approve' or 'deny'."
    )


async def ask_user_for_approval(state: WorkflowState) -> WorkflowState:
    user_id = state["user_id"]
    async with get_session() as session:
        user: User | None = await get_user_by_id(session, user_id)
    if not user:
        raise ValueError(f"User {user_id} not found")
    prompt = generate_approval_prompt(state.dict())
    agent = create_chat_agent()
    response = await agent.arun(prompt)
    decision = "approve" in response.lower()
    state.approval = decision
    return state


async def handle_result(state: WorkflowState) -> WorkflowState:
    if not state.approval:
        state.result = "Action denied by user."
        return state
    state.result = "Action approved and executed."
    return state


def build_graph() -> StateGraph[WorkflowState]:
    graph = StateGraph(WorkflowState)
    graph.add_node("ask_user", ask_user_for_approval)
    graph.add_node("handle_result", handle_result)
    graph.set_entry_point("ask_user")
    graph.add_edge("ask_user", "handle_result")
    graph.add_conditional_edges(
        "handle_result",
        lambda s: END,
    )
    return graph


async def run_workflow(request: ApprovalRequest) -> ApprovalResponse:
    state = WorkflowState(
        user_id=request.user_id,
        action=request.action,
        user_name="",
        approval=False,
        result="",
    )
    async with get_session() as session:
        user: User | None = await get_user_by_id(session, request.user_id)
        if not user:
            raise ValueError(f"User {request.user_id} not found")
        state.user_name = user.name
    graph = build_graph()
    runner = graph.compile()
    final_state = await runner.run(state.dict())
    return ApprovalResponse(
        approved=final_state.approval,
        result=final_state.result,
    )