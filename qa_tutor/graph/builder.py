"""Connects the nodes into a graph:  load -> analyze -> sme -> tutor."""
from __future__ import annotations

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from qa_tutor.config import Settings
from qa_tutor.graph.nodes.analyze import make_analyze_node
from qa_tutor.graph.nodes.load_document import make_load_document_node
from qa_tutor.graph.nodes.sme import make_sme_node
from qa_tutor.graph.nodes.tutor import make_tutor_node
from qa_tutor.graph.state import TutorState


def route_start(state: dict) -> str:
    """Prep once; later turns go straight to the tutor."""
    return "tutor" if state.get("sme_brief") else "load_document"


def route_after_sme(state: dict) -> str:
    return END if state.get("mode") == "prep" else "tutor"


def build_graph(llm, settings: Settings, checkpointer=None):
    graph = StateGraph(TutorState)

    graph.add_node("load_document", make_load_document_node(settings))
    graph.add_node("analyze", make_analyze_node(llm, settings))
    graph.add_node("sme_training", make_sme_node(llm, settings))
    graph.add_node("tutor", make_tutor_node(llm, settings))

    graph.add_conditional_edges(
        START, route_start, {"tutor": "tutor", "load_document": "load_document"}
    )
    graph.add_edge("load_document", "analyze")
    graph.add_edge("analyze", "sme_training")
    graph.add_conditional_edges(
        "sme_training", route_after_sme, {"tutor": "tutor", END: END}
    )
    graph.add_edge("tutor", END)

    return graph.compile(checkpointer=checkpointer or MemorySaver())
