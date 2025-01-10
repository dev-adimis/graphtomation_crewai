# Graphtomation Crewai Documentation

## Overview

**Graphtomation Crewai** is a FastAPI-based utility designed to easily integrate and deploy CrewAI functionalities. This package simplifies the process of exposing CrewAI agents, tasks, and workflows as API endpoints, making them accessible over the web.

---

## Installation

Install the required dependencies for Graphtomation Crewai using the following command:

```bash
pip install crewai crewai[tools] fastapi[standard]
```

---

## Implementation

This section provides an example implementation showcasing how to define a custom tool, create a CrewAI agent and task, and expose them as API endpoints using FastAPI.

---

### Example Custom Tool: `DuckDuckGoSearchTool`

The `DuckDuckGoSearchTool` is a custom tool that performs web searches using the DuckDuckGo API and retrieves the top results.

#### **Code: `tests/example.py`**

```python
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import requests

# Define the input schema for the tool
class DuckDuckGoSearchInput(BaseModel):
    """Input schema for DuckDuckGoSearchTool."""
    query: str = Field(..., description="Search query to look up on DuckDuckGo.")

# Create the custom tool by subclassing BaseTool
class DuckDuckGoSearchTool(BaseTool):
    name: str = "DuckDuckGoSearch"
    description: str = (
        "This tool performs web searches using DuckDuckGo and retrieves the top results. "
        "Provide a query string to get relevant information."
    )
    args_schema: Type[BaseModel] = DuckDuckGoSearchInput

    def _run(self, query: str) -> str:
        """
        Perform a search using the DuckDuckGo API and return the top results.
        """
        url = "https://api.duckduckgo.com/"
        params = {
            "q": query,
            "format": "json",
            "no_redirect": "1",
            "no_html": "1",
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            # Extract the top result or fallback to AbstractText
            if "RelatedTopics" in data and data["RelatedTopics"]:
                results = [
                    topic.get("Text", "No description available")
                    for topic in data["RelatedTopics"]
                    if "Text" in topic
                ]
                return "\n".join(results[:3])  # Return the top 3 results
            else:
                return "No results found for the given query."

        except requests.RequestException as e:
            return f"An error occurred while performing the search: {e}"
```

---

### CrewAI Agent and Task Example

We now define a **CrewAI Agent** with a goal to perform web searches and a corresponding task to search for the latest advancements in AI.

#### **Code (continued): `tests/example.py`**

```python
from crewai import Agent, Task, Crew

# Create an instance of the DuckDuckGoSearchTool
ddg_search_tool = DuckDuckGoSearchTool()

# Define the researcher agent
researcher = Agent(
    role="Web Researcher",
    goal="Perform searches to gather relevant information for tasks.",
    backstory="An experienced researcher with expertise in online information gathering.",
    tools=[ddg_search_tool],
    verbose=True,
)

# Define a research task
research_task = Task(
    description="Search for the latest advancements in AI technology.",
    expected_output="A summary of the top 3 advancements in AI technology from recent searches.",
    agent=researcher,
)

# Create a crew with the researcher and task
example_crew = Crew(
    agents=[researcher],
    tasks=[research_task],
    verbose=True,
    planning=True,
)
```

---

### FastAPI Integration

We use **Graphtomation Crewai** to expose the `example_crew` as an API endpoint.

#### **Code: `main.py`**

```python
from fastapi import FastAPI
from graphtomation_crewai.router import CrewRouter
from tests.example import example_crew

app = FastAPI()

# Create the CrewRouter instance with metadata
crew_router = CrewRouter(
    crews=[
        {
            "name": "example-crew",
            "crew": example_crew,
            "metadata": {
                "description": "An example crew ai implementation",
                "version": "1.0.0",
            },
        }
    ]
)

# Include the CrewRouter in the FastAPI app
app.include_router(crew_router.router, prefix="/crew")
```

---

## Running the Application

```bash
fastapi dev main.py
```
