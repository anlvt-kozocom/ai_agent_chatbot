import sys
import os

# Add project root to sys.path
sys.path.append(os.getcwd())

try:
    from app.graphs.qa_graph import build_graph

    graph = build_graph()
    print("Graph compiled successfully.")
except Exception as e:
    print(f"Graph compilation failed: {e}")
    sys.exit(1)
