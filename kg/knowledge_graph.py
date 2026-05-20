try:
    import networkx as nx
except Exception:  # pragma: no cover
    nx = None


class JEETopicKnowledgeGraph:
    """Lightweight JEE prerequisite graph for explainable dependency reasoning."""

    # Subject ownership for each topic node
    SUBJECT_MAP: dict[str, str] = {
        # Physics
        "Units and Dimensions": "Physics",
        "Vectors": "Physics",
        "Kinematics": "Physics",
        "NLM": "Physics",
        "Work Power Energy": "Physics",
        "Rotation": "Physics",
        "Electrostatics": "Physics",
        "Current Electricity": "Physics",
        "Modern Physics": "Physics",
        # Chemistry
        "Mole Concept": "Chemistry",
        "Chemical Bonding": "Chemistry",
        "Thermodynamics": "Chemistry",
        "Equilibrium": "Chemistry",
        "Organic Chemistry": "Chemistry",
        "Coordination Compounds": "Chemistry",
        # Mathematics
        "Sets": "Mathematics",
        "Functions": "Mathematics",
        "Limits": "Mathematics",
        "Differentiation": "Mathematics",
        "AOD": "Mathematics",
        "Integration": "Mathematics",
        "Differential Equations": "Mathematics",
        "Matrices": "Mathematics",
        "Probability": "Mathematics",
        "Quadratic Equations": "Mathematics",
        "Trigonometry": "Mathematics",
    }

    def __init__(self) -> None:
        self.edges: list[tuple[str, str]] = []
        self.graph = nx.DiGraph() if nx else None
        self._build()

    def _build(self) -> None:
        chains = [
            # Physics chains
            ["Units and Dimensions", "Vectors", "Kinematics", "NLM", "Work Power Energy", "Rotation"],
            ["Kinematics", "Work Power Energy"],
            ["NLM", "Work Power Energy", "Rotation"],
            ["Electrostatics", "Current Electricity", "Modern Physics"],
            # Chemistry chains
            ["Mole Concept", "Chemical Bonding", "Thermodynamics", "Equilibrium", "Organic Chemistry"],
            ["Chemical Bonding", "Coordination Compounds"],
            ["Thermodynamics", "Equilibrium"],
            ["Equilibrium", "Organic Chemistry"],
            # Mathematics chains
            ["Sets", "Functions", "Limits", "Differentiation", "AOD", "Integration", "Differential Equations"],
            ["Quadratic Equations", "Functions", "Limits"],
            ["Trigonometry", "Differentiation", "Integration"],
            ["Differentiation", "Matrices"],
            ["Matrices", "Probability"],
            ["Limits", "Differentiation"],
            ["Sets", "Probability"],
        ]
        seen = set()
        for chain in chains:
            for parent, child in zip(chain, chain[1:]):
                edge = (parent, child)
                if edge not in seen:
                    seen.add(edge)
                    self.edges.append(edge)
                    if self.graph is not None:
                        self.graph.add_edge(parent, child)

    def get_all_nodes(self) -> list[str]:
        if self.graph is not None:
            return list(self.graph.nodes())
        nodes: set[str] = set()
        for parent, child in self.edges:
            nodes.add(parent)
            nodes.add(child)
        return sorted(nodes)

    def analyze_weak_topics(self, weak_topics: list[str]) -> dict:
        prerequisite_gaps: dict[str, list[str]] = {}
        future_risk_topics: dict[str, list[str]] = {}
        foundational: set[str] = set()
        for topic in weak_topics:
            if not self._has_topic(topic):
                continue
            prereqs = self._ancestors(topic)
            downstream = self._descendants(topic)
            prerequisite_gaps[topic] = prereqs
            future_risk_topics[topic] = downstream
            foundational.update(prereqs[:3])
        return {
            "prerequisite_gaps": prerequisite_gaps,
            "future_risk_topics": future_risk_topics,
            "foundational_topics": sorted(foundational),
            "reasoning": (
                "Prerequisite ancestors explain concept gaps; "
                "descendants represent future risk if gaps remain."
            ),
        }

    def _has_topic(self, topic: str) -> bool:
        if self.graph is not None:
            return topic in self.graph
        return any(topic in edge for edge in self.edges)

    def _ancestors(self, topic: str) -> list[str]:
        if self.graph is not None:
            return list(nx.ancestors(self.graph, topic))
        parents = {child: parent for parent, child in self.edges}
        result: list[str] = []
        current = topic
        while current in parents:
            current = parents[current]
            result.append(current)
        return result

    def _descendants(self, topic: str) -> list[str]:
        if self.graph is not None:
            return list(nx.descendants(self.graph, topic))
        children = {parent: child for parent, child in self.edges}
        result: list[str] = []
        current = topic
        while current in children:
            current = children[current]
            result.append(current)
        return result
