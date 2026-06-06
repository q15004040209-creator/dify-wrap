"""
Dify Wrapper - Python Interface
A Pythonic wrapper for Dify LLM app development platform.

Usage:
    from dify import DifyClient

    client = DifyClient(base_url="http://localhost/install", api_key="app-xxx")
    apps = client.apps.list()
    result = client.apps.load("my-app").chat("Hello!")
"""

import urllib.request
import urllib.error
import json
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


__version__ = "0.1.0"
__all__ = ["DifyClient", "App", "Workflow", "Agent", "Dataset"]


@dataclass
class AppInfo:
    id: str
    name: str
    description: str
    type: str  # chat / completion / agent / workflow
    icon: str
    tags: List[str] = field(default_factory=list)


@dataclass
class ChatResponse:
    message: str
    conversation_id: str
    message_id: str
    usage: Dict[str, int]
    traces: List[Dict] = field(default_factory=list)


@dataclass
class WorkflowResult:
    status: str
    output: Dict[str, Any]
    duration_ms: int
    steps: int = 0


@dataclass
class DatasetQueryResult:
    content: str
    score: float
    metadata: Dict[str, Any]


class DifyClient:
    """Python client for Dify LLM app platform."""

    def __init__(
        self,
        base_url: str = "http://localhost/install",
        api_key: Optional[str] = None,
        timeout: int = 120,
        verify_ssl: bool = True
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self._apps = AppsInterface(self)
        self._workflows = WorkflowsInterface(self)
        self._agents = AgentsInterface(self)
        self._datasets = DatasetsInterface(self)
        self._llmops = LlmOpsInterface(self)

    def _request(
        self,
        method: str,
        path: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ):
        """Make an HTTP request."""
        url = f"{self.base_url}{path}"
        if params:
            query = "&".join(f"{k}={v}" for k, v in params.items())
            url = f"{url}?{query}"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        req = urllib.request.Request(url, headers=headers, method=method)
        if data:
            req.data = json.dumps(data).encode()

        try:
            resp = urllib.request.urlopen(req, timeout=self.timeout)
            content = resp.read()
            return json.loads(content) if content else {}
        except urllib.error.HTTPError as e:
            return {"error": f"HTTP {e.code}", "detail": e.read().decode()}
        except Exception as e:
            return {"error": str(e)}

    @property
    def apps(self):
        return self._apps

    @property
    def workflows(self):
        return self._workflows

    @property
    def agents(self):
        return self._agents

    @property
    def datasets(self):
        return self._datasets

    @property
    def llmops(self):
        return self._llmops


class AppsInterface:
    def __init__(self, client: DifyClient):
        self._client = client

    def list(self, tags: Optional[List[str]] = None) -> List[AppInfo]:
        params = {}
        if tags:
            params["tags"] = ",".join(tags)

        result = self._client._request("GET", "/console/api/apps", params=params)
        apps = result.get("data", result.get("error", []))
        if isinstance(apps, str):
            return []
        return [
            AppInfo(
                id=a.get("id", ""),
                name=a.get("name", ""),
                description=a.get("description", ""),
                type=a.get("type", ""),
                icon=a.get("icon", ""),
                tags=a.get("tags", []),
            )
            for a in apps
        ]

    def load(self, app_id: str) -> "App":
        return App(self._client, app_id)


class App:
    """A Dify application."""

    def __init__(self, client: DifyClient, app_id: str):
        self._client = client
        self.app_id = app_id

    def chat(
        self,
        query: str,
        conversation_id: Optional[str] = None,
        user: str = "anonymous",
        **kwargs
    ) -> ChatResponse:
        data = {
            "query": query,
            "user": user,
            "response_mode": "blocking",
            **kwargs
        }
        if conversation_id:
            data["conversation_id"] = conversation_id

        result = self._client._request(
            "POST",
            f"/console/api/apps/{self.app_id}/chat-messages",
            data=data
        )

        if "error" in result:
            return ChatResponse(
                message=f"Error: {result['error']}",
                conversation_id="",
                message_id="",
                usage={},
            )

        return ChatResponse(
            message=result.get("answer", result.get("message", "")),
            conversation_id=result.get("conversation_id", ""),
            message_id=result.get("message_id", ""),
            usage=result.get("usage", {}),
            traces=result.get("traces", []),
        )

    def chat_stream(
        self,
        query: str,
        conversation_id: Optional[str] = None,
        user: str = "anonymous",
        **kwargs
    ):
        """Streaming chat response (yields chunks)."""
        data = {
            "query": query,
            "user": user,
            "response_mode": "streaming",
            **kwargs
        }
        if conversation_id:
            data["conversation_id"] = conversation_id

        result = self._client._request(
            "POST",
            f"/console/api/apps/{self.app_id}/chat-messages",
            data=data
        )

        if "error" in result:
            yield f"Error: {result['error']}"
            return

        message = result.get("answer", result.get("message", ""))
        yield message


class WorkflowsInterface:
    def __init__(self, client: DifyClient):
        self._client = client

    def list(self) -> List[AppInfo]:
        result = self._client._request("GET", "/console/api/apps?type=workflow")
        apps = result.get("data", result.get("error", []))
        if isinstance(apps, str):
            return []
        return [
            AppInfo(
                id=a.get("id", ""),
                name=a.get("name", ""),
                description=a.get("description", ""),
                type="workflow",
                icon=a.get("icon", ""),
                tags=a.get("tags", []),
            )
            for a in apps
        ]

    def load(self, workflow_id: str) -> "Workflow":
        return Workflow(self._client, workflow_id)


class Workflow:
    """A Dify workflow."""

    def __init__(self, client: DifyClient, workflow_id: str):
        self._client = client
        self.workflow_id = workflow_id

    def run(
        self,
        input: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None
    ) -> WorkflowResult:
        data = {
            "inputs": input,
            "response_mode": "blocking",
        }
        if config:
            data["config"] = config

        result = self._client._request(
            "POST",
            f"/console/api/workflows/{self.workflow_id}/run",
            data=data
        )

        if "error" in result:
            return WorkflowResult(
                status="error",
                output={"error": result["error"]},
                duration_ms=0,
            )

        return WorkflowResult(
            status=result.get("status", "succeeded"),
            output=result.get("outputs", {}),
            duration_ms=result.get("duration", 0),
            steps=result.get("steps", 1),
        )


class AgentsInterface:
    def __init__(self, client: DifyClient):
        self._client = client

    def create(
        self,
        name: str,
        model: str = "gpt-4o",
        prompt: str = "You are a helpful AI assistant.",
        tools: Optional[List[str]] = None,
    ) -> "Agent":
        data = {
            "name": name,
            "model": model,
            "prompt": prompt,
            "tools": tools or [],
        }
        result = self._client._request("POST", "/console/api/agents", data=data)
        return Agent(self._client, result.get("id", ""))

    def list(self) -> List[Dict]:
        result = self._client._request("GET", "/console/api/agents")
        return result.get("data", [])


class Agent:
    def __init__(self, client: DifyClient, agent_id: str):
        self._client = client
        self.agent_id = agent_id

    def run(self, query: str, user: str = "anonymous") -> ChatResponse:
        data = {"query": query, "user": user}
        result = self._client._request(
            "POST",
            f"/console/api/agents/{self.agent_id}/run",
            data=data
        )
        return ChatResponse(
            message=result.get("message", result.get("error", "")),
            conversation_id=result.get("conversation_id", ""),
            message_id=result.get("message_id", ""),
            usage=result.get("usage", {}),
        )


class DatasetsInterface:
    def __init__(self, client: DifyClient):
        self._client = client

    def list(self) -> List[Dict]:
        result = self._client._request("GET", "/console/api/datasets")
        return result.get("data", result.get("error", []))

    def create(
        self,
        name: str,
        description: str = "",
        index_engine: str = "pgvector"
    ) -> Dict:
        data = {
            "name": name,
            "description": description,
            "indexing_technique": "high_quality",
            "embedding_model": "text-embedding-3-small",
        }
        return self._client._request("POST", "/console/api/datasets", data=data)

    def load(self, dataset_id: str) -> "Dataset":
        return Dataset(self._client, dataset_id)


class Dataset:
    def __init__(self, client: DifyClient, dataset_id: str):
        self._client = client
        self.dataset_id = dataset_id

    def upload(
        self,
        files: List[str],
        batch_size: int = 100,
        process_settings: Optional[Dict] = None
    ):
        data = {
            "files": files,
            "batch_size": batch_size,
            "process_settings": process_settings or {"chunk_size": 500},
        }
        return self._client._request(
            "POST",
            f"/console/api/datasets/{self.dataset_id}/documents",
            data=data
        )

    def query(
        self,
        query: str,
        top_k: int = 5
    ) -> List[DatasetQueryResult]:
        data = {"query": query, "top_k": top_k}
        result = self._client._request(
            "POST",
            f"/console/api/datasets/{self.dataset_id}/query",
            data=data
        )
        records = result.get("records", result.get("error", []))
        if isinstance(records, str):
            return []
        return [
            DatasetQueryResult(
                content=r.get("content", ""),
                score=r.get("score", 0.0),
                metadata=r.get("metadata", {}),
            )
            for r in records
        ]


class LlmOpsInterface:
    def __init__(self, client: DifyClient):
        self._client = client

    def list_logs(
        self,
        app_id: str,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[Dict]:
        params = {"app_id": app_id, "limit": limit}
        if status:
            params["status"] = status

        result = self._client._request("GET", "/console/api/logs", params=params)
        return result.get("data", [])

    def suggest_improvements(self, app_id: str) -> List[Dict]:
        result = self._client._request(
            "GET",
            f"/console/api/apps/{app_id}/suggest-improve"
        )
        return result.get("data", [])