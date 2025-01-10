from enum import Enum
from fastapi import APIRouter
from crewai import Crew, Task, Agent
from typing_extensions import TypedDict
from fastapi.responses import JSONResponse
from starlette.types import ASGIApp, Lifespan
from fastapi.routing import BaseRoute, APIRoute
from typing import List, Dict, Any, Sequence, Callable, Optional, Union, Literal, Type


class CrewSchema(TypedDict, total=False):
    name: str
    crew: Crew
    metadata: Optional[dict] = None


class CrewRouter:
    def __init__(
        self,
        crews: List[CrewSchema],
        dependencies: Optional[
            Dict[
                Literal[
                    "list_crews",
                    "train",
                    "kickoff",
                    "kickoff_for_each",
                    "kickoff_for_each_async",
                    "replay",
                    "query_knowledge",
                    "copy",
                    "calculate_usage_metrics",
                    "test",
                ],
                Callable,
            ]
        ] = None,
        global_dependencies: Optional[List[Callable]] = None,
        prefix: str = "",
        tags: Optional[List[Union[str, Enum]]] = None,
        default_response_class: Type[JSONResponse] = JSONResponse,
        responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
        callbacks: Optional[List[BaseRoute]] = None,
        routes: Optional[List[BaseRoute]] = None,
        redirect_slashes: bool = True,
        default: Optional[ASGIApp] = None,
        dependency_overrides_provider: Optional[Any] = None,
        route_class: Type[APIRoute] = APIRoute,
        on_startup: Optional[Sequence[Callable[[], Any]]] = None,
        on_shutdown: Optional[Sequence[Callable[[], Any]]] = None,
        lifespan: Optional[Lifespan[Any]] = None,
        deprecated: Optional[bool] = None,
        include_in_schema: bool = True,
    ):
        """
        Initialize the CrewRouter.

        :param crews: A list of crews to register.
        :param dependencies: A dictionary mapping route names to their dependencies.
        :param global_dependencies: A list of global dependencies applied to all routes.
        :param prefix: API route prefix for this router.
        :param tags: Tags applied to all routes.
        :param default_response_class: Default response class for routes.
        :param responses: Custom responses for routes.
        :param callbacks: Callbacks for routes.
        :param routes: Routes to include in the router.
        :param redirect_slashes: Redirect slashes setting.
        :param default: Default ASGIApp instance.
        :param dependency_overrides_provider: Dependency override provider.
        :param route_class: Route class to use for all routes.
        :param on_startup: List of startup event handlers.
        :param on_shutdown: List of shutdown event handlers.
        :param lifespan: Lifespan context manager for the router.
        :param deprecated: Deprecation status for the router.
        :param include_in_schema: Whether to include this router in OpenAPI schema.
        """
        self.crews = crews
        self.router = APIRouter(
            prefix=prefix,
            tags=tags or ["Crew Endpoints"],
            dependencies=global_dependencies or [],
            default_response_class=default_response_class,
            responses=responses,
            callbacks=callbacks,
            routes=routes,
            redirect_slashes=redirect_slashes,
            default=default,
            dependency_overrides_provider=dependency_overrides_provider,
            route_class=route_class,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            lifespan=lifespan,
            deprecated=deprecated,
            include_in_schema=include_in_schema,
        )
        self.dependencies = dependencies or {}
        self._add_routes()

    def _add_routes(self):
        self.router.add_api_route(
            "",
            self.list_crews,
            methods=["GET"],
            dependencies=self.dependencies.get("list_crews", None),
        )

        self.router.add_api_route(
            "/{name}/train",
            self.train,
            methods=["POST"],
            dependencies=self.dependencies.get("train", None),
        )
        self.router.add_api_route(
            "/{name}/kickoff",
            self.kickoff,
            methods=["POST"],
            dependencies=self.dependencies.get("kickoff", None),
        )
        self.router.add_api_route(
            "/{name}/kickoff_for_each",
            self.kickoff_for_each,
            methods=["POST"],
            dependencies=self.dependencies.get("kickoff_for_each", None),
        )
        self.router.add_api_route(
            "/{name}/kickoff_for_each_async",
            self.kickoff_for_each_async,
            methods=["POST"],
            dependencies=self.dependencies.get("kickoff_for_each_async", None),
        )
        self.router.add_api_route(
            "/{name}/replay",
            self.replay,
            methods=["POST"],
            dependencies=self.dependencies.get("replay", None),
        )
        self.router.add_api_route(
            "/{name}/query_knowledge",
            self.query_knowledge,
            methods=["POST"],
            dependencies=self.dependencies.get("query_knowledge", None),
        )
        self.router.add_api_route(
            "/{name}/copy",
            self.copy,
            methods=["GET"],
            dependencies=self.dependencies.get("copy", None),
        )
        self.router.add_api_route(
            "/{name}/calculate_usage_metrics",
            self.calculate_usage_metrics,
            methods=["GET"],
            dependencies=self.dependencies.get("calculate_usage_metrics", None),
        )
        self.router.add_api_route(
            "/{name}/test",
            self.test,
            methods=["POST"],
            dependencies=self.dependencies.get("test", None),
        )

    async def train(
        self,
        name: str,
        n_iterations: int,
        filename: str,
        inputs: Optional[Dict[str, Any]] = {},
    ):
        crew = self._get_crew(name)
        crew.crew.train(n_iterations, filename, inputs)
        return {"message": f"Training for crew '{name}' completed successfully."}

    async def kickoff(self, name: str, inputs: Dict[str, Any]):
        crew = self._get_crew(name)
        result = crew.crew.kickoff(inputs)
        return result

    async def kickoff_for_each(self, name: str, inputs: List[Dict[str, Any]]):
        crew = self._get_crew(name)
        results = crew.crew.kickoff_for_each(inputs)
        return results

    async def kickoff_for_each_async(self, name: str, inputs: List[Dict[str, Any]]):
        crew = self._get_crew(name)
        results = await crew.crew.kickoff_for_each_async(inputs)
        return results

    async def replay(
        self, name: str, task_id: str, inputs: Optional[Dict[str, Any]] = {}
    ):
        crew = self._get_crew(name)
        result = crew.crew.replay(task_id, inputs)
        return result

    async def query_knowledge(self, name: str, query: List[str]):
        crew = self._get_crew(name)
        results = crew.crew.query_knowledge(query)
        return results

    async def copy(self, name: str):
        crew = self._get_crew(name)
        copied_crew = crew.crew.copy()
        return {
            "message": f"Crew '{name}' copied successfully.",
            "crew_id": str(copied_crew.id),
        }

    async def calculate_usage_metrics(self, name: str):
        crew = self._get_crew(name)
        metrics = crew.crew.calculate_usage_metrics()
        return metrics

    async def test(
        self,
        name: str,
        n_iterations: int,
        openai_model_name: Optional[str] = None,
        inputs: Optional[Dict[str, Any]] = None,
    ):
        crew = self._get_crew(name)
        crew.crew.test(n_iterations, openai_model_name, inputs)
        return {"message": f"Testing for crew '{name}' completed successfully."}

    def _get_crew(self, name: str) -> CrewSchema:
        crew = self.crews.get(name)
        if not crew:
            raise ValueError(f"Crew '{name}' not found.")
        return crew

    async def list_crews(self):
        def serialize_agent(agent: Agent):
            return {
                "id": str(agent.id),
                "role": agent.role,
                "goal": agent.goal,
                "backstory": agent.backstory,
                "cache": agent.cache,
                "verbose": agent.verbose,
                "max_rpm": agent.max_rpm,
                "allow_delegation": agent.allow_delegation,
                "tools": [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "result_as_answer": tool.result_as_answer,
                        "args_schema": tool.args_schema.model_json_schema(),
                    }
                    for tool in agent.tools or []
                ],
                "formatting_errors": agent.formatting_errors,
                "max_iter": agent.max_iter,
                "max_tokens": agent.max_tokens,
                "config": agent.config,
                "crew": str(agent.crew.id) if agent.crew else None,
            }

        def serialize_task(task: Task):
            return {
                "id": str(task.id),
                "name": task.name,
                "description": task.description,
                "expected_output": task.expected_output,
                "tools": [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "result_as_answer": tool.result_as_answer,
                        "args_schema": tool.args_schema.model_json_schema(),
                    }
                    for tool in task.tools or []
                ],
                "agent": serialize_agent(task.agent) if task.agent else None,
                "async_execution": task.async_execution,
                "output_file": task.output_file,
                "human_input": task.human_input,
                "start_time": task.start_time.isoformat() if task.start_time else None,
                "end_time": task.end_time.isoformat() if task.end_time else None,
                "execution_duration": task.execution_duration,
                "used_tools": task.used_tools,
                "tools_errors": task.tools_errors,
                "delegations": task.delegations,
                "processed_by_agents": list(task.processed_by_agents),
                "config": task.config,
                "callback": str(task.callback) if task.callback else None,
                "context": [
                    serialize_task(context_task) for context_task in task.context or []
                ],
                "output_json": (
                    task.output_json.model_json_schema() if task.output_json else None
                ),
                "output_pydantic": (
                    task.output_pydantic.model_json_schema()
                    if task.output_pydantic
                    else None
                ),
                "retry_count": task.retry_count,
                "max_retries": task.max_retries,
                "guardrail": str(task.guardrail) if task.guardrail else None,
                "converter_cls": (
                    task.converter_cls.__name__ if task.converter_cls else None
                ),
            }

        serialized_crews = [
            {
                "name": crew["name"],
                "metadata": crew.get("metadata"),
                "crew": {
                    "id": str(crew["crew"].id),
                    "tasks": [serialize_task(task) for task in crew["crew"].tasks],
                    "agents": [serialize_agent(agent) for agent in crew["crew"].agents],
                },
            }
            for crew in self.crews
        ]
        return serialized_crews
