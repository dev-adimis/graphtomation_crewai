from fastapi import FastAPI
from graphtomation_crewai import CrewRouter

from tests.example import example_crew

app = FastAPI()


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

app.include_router(crew_router.router, prefix="/crew")
