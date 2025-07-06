import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..agent.graph import create_graph
from ..prompts import STEP_DESCRIPTIONS

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Handles the WebSocket connection to run the agent and stream events.
    """
    await websocket.accept()
    langgraph_app = create_graph()
    try:
        query_data = await websocket.receive_text()
        inputs = {"user_query": query_data}
        config = {"recursion_limit": 50}

        async for event in langgraph_app.astream_events(inputs, config=config, version="v1"):
            kind = event["event"]
            if kind == "on_chain_start":
                node_name = event["name"]
                if node_name in STEP_DESCRIPTIONS:
                    await websocket.send_json({"type": "step", "message": STEP_DESCRIPTIONS[node_name]})
            elif kind == "on_chain_end" and event["name"] == "LangGraph":
                print(event["data"]["output"])
                await websocket.send_json({"type": "result", "data": event["data"]["output"]})

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"An error occurred: {e}")
        await websocket.send_json({"type": "error", "message": str(e)})
    finally:
        await websocket.close()