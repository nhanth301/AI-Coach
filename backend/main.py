import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from src.agent.graph import create_graph

app = FastAPI()

with open("index.html", "r", encoding="utf-8") as f:
    html_content = f.read()

STEP_DESCRIPTIONS = {
    "rewrite_query": "✍️ Optimizing query...",
    "router": "🧭 Analyzing and routing...",
    "web_search": "🌐 Searching the web...",
    "arxiv_search": "🔬 Searching ArXiv...",
    "process_web_results": "📄 Processing and summarizing web results...",
    "process_arxiv_results": "📚 Processing and summarizing scientific documents...",
}

@app.get("/")
async def get():
    return HTMLResponse(html_content)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    langgraph_app = create_graph()

    try:
        query_data = await websocket.receive_text()
        inputs = {"user_query": query_data}

        async for event in langgraph_app.astream_events(inputs, version="v1"):
            kind = event["event"]
            

            if kind == "on_chain_start":
                node_name = event["name"]
                if node_name in STEP_DESCRIPTIONS:
                    step_message = STEP_DESCRIPTIONS[node_name]
                    await websocket.send_json({"type": "step", "message": step_message})
                    await asyncio.sleep(0.5) 

            if kind == "on_chain_end" and event["name"] == "LangGraph":
                final_result = event["data"]["output"]
                await websocket.send_json({"type": "result", "data": final_result})

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"An error occurred: {e}")
        await websocket.send_json({"type": "error", "message": str(e)})
    finally:
        await websocket.close()