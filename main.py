from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
import hashlib, re

app = FastAPI(title="GenLink Jarvis Agent", version="1.0.0")

class LinkRequest(BaseModel):
    urls: List[str]
    topic: str = ""

class GraphRequest(BaseModel):
    text: str

class Node(BaseModel):
    id: str
    label: str
    type: str

class Edge(BaseModel):
    source: str
    target: str
    weight: float

class GraphResponse(BaseModel):
    nodes: List[Node]
    edges: List[Edge]
    summary: str

def slug(text): return hashlib.md5(text.encode()).hexdigest()[:8]

def extract_keywords(text):
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    return sorted(freq, key=freq.get, reverse=True)[:8]

@app.post("/analyze-links", response_model=GraphResponse)
def analyze_links(req: LinkRequest):
    nodes = [Node(id=slug(u), label=u[:40], type="url") for u in req.urls]
    if req.topic:
        nodes.append(Node(id="topic", label=req.topic, type="concept"))
    edges = [Edge(source="topic", target=slug(u), weight=0.8) for u in req.urls] if req.topic else []
    return GraphResponse(nodes=nodes, edges=edges, summary=f"{len(nodes)} nodes, {len(edges)} edges generated")

@app.post("/generate-graph", response_model=GraphResponse)
def generate_graph(req: GraphRequest):
    keywords = extract_keywords(req.text)
    nodes = [Node(id=slug(k), label=k, type="keyword") for k in keywords]
    edges = [Edge(source=slug(keywords[i]), target=slug(keywords[i+1]), weight=0.6)
             for i in range(len(keywords)-1)]
    return GraphResponse(nodes=nodes, edges=edges, summary=f"Extracted {len(keywords)} semantic nodes")

@app.get("/export")
def export():
    return {"format": "JSON", "status": "ready", "endpoint": "/generate-graph"}

@app.get("/health")
def health():
    return {"status": "ok", "service": "genlink-jarvis-agent"}
