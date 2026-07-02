import unittest
from app.agents.router_agent import router_agent
from app.orchestrator.router import route_next_node

class TestAgentRouting(unittest.TestCase):
    def test_math_calculation_heuristics(self):
        # Queries containing math keywords must be routed to planner
        res = router_agent("Calculate 35 * 48")
        self.assertEqual(res["route"], "planner")
        self.assertIn("planner", res["reasoning"].lower() or "heuristically")

    def test_database_query_heuristics(self):
        # Queries containing database keywords must be routed to planner
        res = router_agent("Query the database user table")
        self.assertEqual(res["route"], "planner")
        
    def test_document_manual_heuristics(self):
        # Queries about internal system manual must be routed to rag
        res = router_agent("What is Aether Orchestrator manual?")
        self.assertEqual(res["route"], "rag")

    def test_next_node_router(self):
        # State transitions based on routing state
        state_llm = {"route": "llm"}
        self.assertEqual(route_next_node(state_llm), "llm")
        
        state_invalid = {"route": "unknown_value"}
        self.assertEqual(route_next_node(state_invalid), "llm")

if __name__ == "__main__":
    unittest.main()
