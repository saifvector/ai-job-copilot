import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, model_validator


# --- Agent Schemas ---

class AgentInfoResponse(BaseModel):
    name: str = Field(..., description="Unique agent identifier name")
    description: str = Field(..., description="Agent domain role and capabilities")
    capabilities: List[str] = Field(default_factory=list, description="List of discrete tasks the agent can execute")
    default_model: str = Field(..., description="Default LLM model routed for this agent")
    status: str = Field(default="IDLE", description="Current operating status (IDLE, BUSY, READY)")


class AgentListResponse(BaseModel):
    items: List[AgentInfoResponse]
    total: int


class AgentExecuteRequest(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters and task directives")
    model_override: Optional[str] = Field(None, description="Optional override for model router selection")


class AgentExecuteResponse(BaseModel):
    agent: str
    status: str
    result: Dict[str, Any]
    model_used: str
    duration_ms: float
    task_id: Optional[uuid.UUID] = None


# --- Task Schemas ---

class AgentTaskCreate(BaseModel):
    agent: str = Field(..., description="Target specialized agent name")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input payload for the agent task")
    model_override: Optional[str] = Field(None, description="Optional LLM model override")


class AgentTaskResponse(BaseModel):
    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    agent: str
    workflow_execution_id: Optional[uuid.UUID] = None
    status: str
    payload: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    model_used: Optional[str] = None
    duration_ms: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @model_validator(mode="before")
    @classmethod
    def parse_json_fields(cls, data: Any) -> Any:
        if hasattr(data, "__tablename__"):
            raw_payload = getattr(data, "payload", "{}")
            raw_result = getattr(data, "result", None)

            def safe_parse(val: Any) -> Any:
                if isinstance(val, str):
                    try:
                        return json.loads(val)
                    except Exception:
                        return {"raw": val}
                return val or {}

            return {
                "id": data.id,
                "user_id": data.user_id,
                "agent": data.agent,
                "workflow_execution_id": data.workflow_execution_id,
                "status": data.status,
                "payload": safe_parse(raw_payload),
                "result": safe_parse(raw_result) if raw_result else None,
                "error_message": data.error_message,
                "model_used": data.model_used,
                "duration_ms": data.duration_ms,
                "retry_count": data.retry_count,
                "max_retries": data.max_retries,
                "created_at": data.created_at,
                "updated_at": data.updated_at,
                "completed_at": data.completed_at,
            }
        return data


class AgentTaskListResponse(BaseModel):
    items: List[AgentTaskResponse]
    total: int


# --- Memory Schemas ---

class AgentMemoryCreate(BaseModel):
    agent: str = Field(..., description="Agent name or '*' for shared memory")
    memory_type: str = Field(..., description="short_term, long_term, critique, preference, fact, working_context")
    content: Dict[str, Any] = Field(..., description="Structured memory content")
    relevance_score: Optional[float] = Field(default=1.0, ge=0.0, le=1.0)


class AgentMemoryResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    agent: str
    memory_type: str
    content: Dict[str, Any]
    relevance_score: float
    created_at: datetime

    class Config:
        from_attributes = True

    @model_validator(mode="before")
    @classmethod
    def parse_memory_content(cls, data: Any) -> Any:
        if hasattr(data, "__tablename__"):
            raw_content = getattr(data, "content", "{}")
            parsed = {}
            if isinstance(raw_content, str):
                try:
                    parsed = json.loads(raw_content)
                except Exception:
                    parsed = {"text": raw_content}
            elif isinstance(raw_content, dict):
                parsed = raw_content

            return {
                "id": data.id,
                "user_id": data.user_id,
                "agent": data.agent,
                "memory_type": data.memory_type,
                "content": parsed,
                "relevance_score": data.relevance_score,
                "created_at": data.created_at,
            }
        return data


class AgentMemoryListResponse(BaseModel):
    items: List[AgentMemoryResponse]
    total: int


# --- Workflow Schemas ---

class WorkflowStepDefinition(BaseModel):
    name: str = Field(..., description="Step identifier")
    agent: str = Field(..., description="Target executing agent")
    description: str = Field(..., description="Role and output of this step")
    dependencies: List[str] = Field(default_factory=list, description="Prior steps required before this step can run")


class WorkflowDefinitionResponse(BaseModel):
    id: str
    name: str
    description: str
    steps: List[WorkflowStepDefinition]


class WorkflowExecuteRequest(BaseModel):
    workflow_type: str = Field(..., description="Predefined workflow identifier (e.g. resume_to_match_pipeline)")
    initial_context: Dict[str, Any] = Field(default_factory=dict, description="Initial context parameters")


class WorkflowStepState(BaseModel):
    step_name: Optional[str] = None
    step_id: Optional[str] = None
    agent: str
    status: str  # PENDING, RUNNING, COMPLETED, FAILED, SKIPPED
    duration_ms: Optional[float] = None
    error: Optional[str] = None
    output: Optional[Dict[str, Any]] = None
    result_summary: Optional[str] = None
    model_used: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def populate_step_name(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get("step_name") and data.get("step_id"):
                data["step_name"] = data["step_id"]
            if not data.get("step_id") and data.get("step_name"):
                data["step_id"] = data["step_name"]
        return data


class WorkflowExecutionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    workflow_type: str
    status: str
    current_step: Optional[str] = None
    steps: List[WorkflowStepState]
    context: Dict[str, Any]
    duration_ms: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @model_validator(mode="before")
    @classmethod
    def parse_workflow_fields(cls, data: Any) -> Any:
        if hasattr(data, "__tablename__"):
            raw_steps = getattr(data, "steps", "[]")
            raw_ctx = getattr(data, "context", "{}")

            steps_list = []
            if isinstance(raw_steps, str):
                try:
                    steps_list = json.loads(raw_steps)
                except Exception:
                    steps_list = []
            elif isinstance(raw_steps, list):
                steps_list = raw_steps

            ctx_dict = {}
            if isinstance(raw_ctx, str):
                try:
                    ctx_dict = json.loads(raw_ctx)
                except Exception:
                    ctx_dict = {}
            elif isinstance(raw_ctx, dict):
                ctx_dict = raw_ctx

            return {
                "id": data.id,
                "user_id": data.user_id,
                "workflow_type": data.workflow_type,
                "status": data.status,
                "current_step": data.current_step,
                "steps": steps_list,
                "context": ctx_dict,
                "duration_ms": data.duration_ms,
                "created_at": data.created_at,
                "updated_at": data.updated_at,
                "completed_at": data.completed_at,
            }
        return data


class WorkflowExecutionListResponse(BaseModel):
    items: List[WorkflowExecutionResponse]
    total: int


# --- Model Router Schemas ---

class ModelRouteRequest(BaseModel):
    task_type: str = Field(..., description="Task classification (e.g. resume_analysis, matching, coaching, classification)")
    complexity: str = Field(default="MEDIUM", description="LOW, MEDIUM, HIGH")
    speed_preference: str = Field(default="BALANCED", description="FASTEST, BALANCED, QUALITY")
    cost_preference: str = Field(default="STANDARD", description="LOWEST_COST, STANDARD, MAX_ACCURACY")
    privacy_level: str = Field(default="CLOUD", description="CLOUD, LOCAL_ONLY")


class ModelRouteResponse(BaseModel):
    selected_model: str
    provider: str
    rationale: str
    estimated_cost_tier: str
    context_window: int
