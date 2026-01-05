import gradio as gr
import requests
import json
import pandas as pd
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

def query_far(query, intent, tenant_id):
    try:
        response = requests.post(f"{API_URL}/query", json={
            "query": query,
            "intent": intent,
            "tenant_id": tenant_id
        })
        response.raise_for_status()
        data = response.json()
        
        # Format stats for display
        stats_df = pd.DataFrame(data.get("stats", []))
        
        return (
            data.get("summary", "No summary"), 
            data.get("context", "No context"),
            stats_df,
            json.dumps(data.get("evidence", []), indent=2)
        )
    except Exception as e:
        return f"Error: {e}", "", pd.DataFrame(), ""

def ingest_memory(content, mtype, key, entities):
    try:
        metadata = {}
        if entities:
            metadata["entities"] = [e.strip() for e in entities.split(",")]
        if key:
            metadata["key"] = key
            
        payload = {
            "content": content,
            "type": mtype,
            "metadata": metadata
        }
        
        response = requests.post(f"{API_URL}/ingest", json=payload)
        response.raise_for_status()
        return f"Success: {response.json()}"
    except Exception as e:
        return f"Error: {e}"

with gr.Blocks(title="FAR Architecture Demo") as demo:
    gr.Markdown("# Fission-Augmented Reasoning (FAR) Explorer")
    
    with gr.Tab("Query (MHCCR)"):
        with gr.Row():
            q_input = gr.Textbox(label="Query", placeholder="What is the status of Project Alpha?")
            intent_input = gr.Dropdown(choices=["general", "factual", "how-to", "status", "history"], label="Intent", value="general")
        
        btn_query = gr.Button("Run Fission", variant="primary")
        
        with gr.Row():
            summary_out = gr.Textbox(label="Energy Summary", lines=3)
        
        with gr.Row():
             stats_out = gr.Dataframe(label="Fission Generation Stats (k_hat)")
             
        with gr.Accordion("Deep Dive (Context & Evidence)", open=False):
            context_out = gr.Textbox(label="Assembled Context", lines=10)
            evidence_out = gr.Code(label="Raw Evidence JSON", language="json")
            
        btn_query.click(query_far, inputs=[q_input, intent_input, gr.State("default")], outputs=[summary_out, context_out, stats_out, evidence_out])

    with gr.Tab("Ingest Memory"):
        with gr.Row():
            m_type = gr.Dropdown(choices=["fact", "event", "procedure", "state"], label="Memory Type")
            m_content = gr.Textbox(label="Content", lines=3)
        
        with gr.Row():
            m_key = gr.Textbox(label="Key (for State)", placeholder="e.g. status_project_x")
            m_entities = gr.Textbox(label="Entities (comma-separated)", placeholder="e.g. project-x, sector-7")
            
        btn_ingest = gr.Button("Ingest")
        ingest_res = gr.Textbox(label="Result")
        
        btn_ingest.click(ingest_memory, inputs=[m_content, m_type, m_key, m_entities], outputs=[ingest_res])

if __name__ == "__main__":
    demo.launch(server_port=7860)
