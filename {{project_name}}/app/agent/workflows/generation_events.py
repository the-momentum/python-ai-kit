from dataclasses import dataclass
from app.schemas.agent import TaskType


@dataclass
class ErrorState:
    error_step: str
    error: Exception
    error_msg: str | None


@dataclass
class TextEvaluationState:
    message: str


@dataclass  
class TextGenerationState:
    message: str
    task_type: TaskType


@dataclass
class GuardrailsState:
    message: str
    task_type: TaskType


@dataclass
class TextRefusalState:
    message: str
    refusal_reason: str


@dataclass
class RefusalInfo:
    refusal_reason: str


@dataclass
class WorkflowState:
    current_message: str = ""
    task_type: TaskType | None = None
    generated_response: str = ""
    refusal_info: RefusalInfo | None = None
    
    def set_refusal(self, message: str, reason: str):
        self.refusal_info = RefusalInfo(refusal_reason=reason)