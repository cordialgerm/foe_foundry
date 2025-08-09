import dotenv

from .build_graph import build_graph
from .visualize import visualize_graph_sampled


def main():
    G, issues = build_graph()

    print(
        f"Graph constructed with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges."
    )

    print(f"{len(issues)} issues found")
    for issue in issues:
        print(issue)

    visualize_graph_sampled(G)


if __name__ == "__main__":
    dotenv.load_dotenv()
    main()
