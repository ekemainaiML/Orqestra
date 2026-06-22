import os
from typing import Any

import yaml

from app.agents.base import BaseAgent
from app.agents.registry import get_agent_class
from app.workflows.schema import WorkflowConfig

WORKFLOWS_DIR = os.path.dirname(__file__)


def load_workflow_config(workflow_type: str) -> WorkflowConfig:
    yaml_path = os.path.join(WORKFLOWS_DIR, f"{workflow_type}.yaml")
    if not os.path.isfile(yaml_path):
        raise ValueError(f"Unknown workflow type: {workflow_type} (no {yaml_path})")
    with open(yaml_path) as f:
        data = yaml.safe_load(f)
    return WorkflowConfig(**data)


def list_workflow_types() -> list[str]:
    configs: list[str] = []
    for fname in os.listdir(WORKFLOWS_DIR):
        if fname.endswith(".yaml") and fname != "__init__.yaml":
            configs.append(fname.removesuffix(".yaml"))
    return sorted(configs)


def instantiate_agents(config: WorkflowConfig) -> list[BaseAgent]:
    agents: list[BaseAgent] = []
    for dept in config.departments:
        cls = get_agent_class(dept.id)
        agent = cls()
        agent.role = dept.role
        agent.model_tier = dept.model_tier
        agent.objectives = list(dept.objectives)
        agent.policies = list(dept.policies)
        agent.tools = list(dept.tools)
        agents.append(agent)
    return agents


def get_workflow_agent_ids(config: WorkflowConfig) -> list[str]:
    return [d.id for d in config.departments]


def get_operational_workflow_agents(config: WorkflowConfig) -> list[BaseAgent]:
    agents = instantiate_agents(config)
    executive_id = config.approval.required_role
    return [a for i, a in enumerate(agents) if config.departments[i].id != executive_id]


def get_executive_workflow_agent(config: WorkflowConfig) -> BaseAgent:
    executive_id = config.approval.required_role
    agents = instantiate_agents(config)
    for i, a in enumerate(agents):
        if config.departments[i].id == executive_id:
            return a
    raise ValueError(f"Executive agent '{executive_id}' not found in workflow config")
