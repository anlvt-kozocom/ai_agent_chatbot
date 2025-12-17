import sys
from app.graphs.qa_graph import build_graph

def generate_graph_image():
    try:
        graph = build_graph()
        print("Generating graph image...")
        # Try to generate PNG
        png_data = graph.get_graph().draw_mermaid_png()
        with open("graph.png", "wb") as f:
            f.write(png_data)
        print("Success! Graph saved to graph.png")
    except Exception as e:
        print(f"Could not save PNG: {e}")
        print("Attempting to save Mermaid definition...")
        try:
            graph = build_graph()
            # Fallback to mermaid text
            mermaid_txt = graph.get_graph().draw_mermaid()
            print("\nMermaid definition:")
            print(mermaid_txt)
            with open("graph.mermaid", "w") as f:
                f.write(mermaid_txt)
            print("\nMermaid definition saved to graph.mermaid")
        except Exception as e2:
            print(f"Could not generate graph: {e2}")

if __name__ == "__main__":
    generate_graph_image()

