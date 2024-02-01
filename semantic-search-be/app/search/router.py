import json
import random
import time

from typing import Annotated
from fastapi import APIRouter, Query

from .service import PostVectorSearch
from . import config
from .schema import Result


router = APIRouter(prefix="/search", tags=["search"])

# Initialize PostVectorSearch instance
post_vector_search = PostVectorSearch(
    model_endpoint_resource=config.VERTEX_AI_MODEL_ENDPOINT_RESOURCE,
    index_endpoint_resource=config.VERTEX_AI_INDEX_ENDPOINT_RESOURCE,
    deployed_index_id=config.DEPLOYED_INDEX_ID,
    redis_host=config.REDIS_HOST,
    redis_port=config.REDIS_PORT,
)
NUM_NEIGHBORS = 40

# Load sample questions from a JSON file
with open("search_suggestion.json") as data:
    sample_questions = json.load(data)


@router.get("")
def search(query: Annotated[str, Query(min_length=3)]) -> Result:
    """Endpoint for performing a semantic search based on the given query.

    Args:
        query (str): Search query.

    Returns:
        Result: Result object containing latency, number of matches, and matched posts.
    """
    start = time.perf_counter()
    matches = post_vector_search.search(text=query, num_neighbors=NUM_NEIGHBORS)
    stop = time.perf_counter()
    latency = round((stop - start) * 1000, 2)  # to milliseconds
    return Result(latency=latency, num_matches=len(matches), matches=matches)


@router.get("/suggestions")
def get_suggestion() -> list[str]:
    """Endpoint for retrieving search suggestions.

    Returns:
        list[str]: List of search suggestions.
    """
    suggestions = random.choices(sample_questions, k=3)
    return [suggestion["question"] for suggestion in suggestions]
