from crewai import Agent
from crewai import Crew
from crewai import Process
from crewai import Task
from crewai.project import CrewBase
from crewai.project import agent
from crewai.project import crew
from crewai.project import task
from crewai import LLM

import boto3
from botocore.config import Config

# ---------------------------------------------------
# Bedrock client config
# ---------------------------------------------------

bedrock_config = Config(
    region_name="us-east-1",
    retries={
        "max_attempts": 15,
        "mode": "adaptive"
    },
    connect_timeout=300,
    read_timeout=300
)

bedrock_client = boto3.client(
    service_name="bedrock-runtime",
    config=bedrock_config
)

# ---------------------------------------------------
# LLM
# ---------------------------------------------------

llm = LLM(
    model="bedrock/us.anthropic.claude-sonnet-4-20250514-v1:0",
    temperature=0.2,
    max_tokens=1500
)

# ---------------------------------------------------
# Crew
# ---------------------------------------------------

@CrewBase
class ResearchCrew():

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # ---------------------------------------------------
    # Agents
    # ---------------------------------------------------

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["researcher"],
            llm=llm,
            verbose=True,
            memory=False,
            max_iter=1,
            max_rpm=2,
            allow_delegation=False
        )

    @agent
    def analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["analyst"],
            llm=llm,
            verbose=True,
            memory=False,
            max_iter=1,
            max_rpm=2,
            allow_delegation=False
        )

    # ---------------------------------------------------
    # Tasks
    # ---------------------------------------------------

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_task"]
        )

    @task
    def analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config["analysis_task"]
        )

    # ---------------------------------------------------
    # Crew
    # ---------------------------------------------------

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=False,
            planning=False,
            max_rpm=2
        )