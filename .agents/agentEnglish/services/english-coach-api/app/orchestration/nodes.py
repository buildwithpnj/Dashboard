from typing import Dict, Any

class BaseOrchestrationNode:
    """Base execution block inside state machine DAG configurations."""

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Runs the node execution block and returns updated session states."""
        return state

class RouterNode(BaseOrchestrationNode):
    """Orchestration node performing route dispatch operations."""

    def __init__(self, router):
        self.router = router

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        input_text = state.get("input_text", "")
        routed_product = self.router.route_request(input_text)
        state["product_id"] = routed_product
        return state
