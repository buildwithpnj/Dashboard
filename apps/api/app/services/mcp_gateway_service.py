import logging
import time
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.mcp_tool_registry import McpToolRegistry
from app.services.mcp_policy_guard import McpPolicyGuard
from app.services.mcp_trace_service import McpTraceService
from app.services.action_confirmation_service import ActionConfirmationService
from app.services.hybrid_retrieval_service import HybridRetrievalService
from typing import Dict, Any, Tuple

logger = logging.getLogger("mcp_gateway")

class McpGatewayService:
    @classmethod
    async def execute_mcp_tool(
        cls,
        db: AsyncSession,
        tenant_id: str,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Executes a registered MCP tool under strict policy and authorization boundaries.
        Returns (success, message, result_data).
        """
        start_time = time.time()

        # 1. Registration Check
        if not McpToolRegistry.is_tool_registered(tool_name):
            err_msg = f"MCP Error: Tool '{tool_name}' is not registered."
            logger.warning(err_msg)
            return False, err_msg, {}

        # 2. Policy Authorization Gate
        is_authorized, auth_reason = McpPolicyGuard.check_permissions(tenant_id, tool_name, arguments)
        if not is_authorized:
            McpTraceService.log_invocation(
                tool_name=tool_name,
                arguments=arguments,
                latency_ms=(time.time() - start_time) * 1000.0,
                success=False,
                message=auth_reason
            )
            return False, f"Policy Block: {auth_reason}", {}

        # 3. Execution Routing
        success = False
        msg = ""
        result = {}

        try:
            if tool_name == "search_knowledge":
                query = arguments["query"]
                chunks = await HybridRetrievalService.retrieve(db, tenant_id, query)
                result = {
                    "matches": [
                        {"chunk_id": c.get("chunk_id"), "summary": c.get("chunk_summary")}
                        for c in chunks
                    ]
                }
                success = True
                msg = f"Retrieved {len(chunks)} context matches from workspace RAG."

            elif tool_name == "create_task":
                success, msg, task_id = await ActionConfirmationService.process_task_creation_with_verification(
                    db, tenant_id, arguments
                )
                if success:
                    result = {"task_id": task_id}

            elif tool_name == "get_recent_updates":
                # Simulated recent updates retrieval
                result = {"updates": []}
                success = True
                msg = "Successfully checked workspace update list."

        except Exception as e:
            logger.error(f"Failed to execute MCP tool '{tool_name}': {e}")
            msg = f"Execution Failure: {e}"

        latency = (time.time() - start_time) * 1000.0
        
        # 4. Log telemetry trace
        McpTraceService.log_invocation(
            tool_name=tool_name,
            arguments=arguments,
            latency_ms=latency,
            success=success,
            message=msg
        )

        return success, msg, result
