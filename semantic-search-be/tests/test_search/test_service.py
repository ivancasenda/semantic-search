import pytest

from google.cloud import aiplatform
from google.cloud.aiplatform.matching_engine.matching_engine_index_endpoint import (
    MatchNeighbor,
)
from google.cloud.aiplatform import models
from app.search.schema import Post, PostMatch
from app.search.service import PostVectorSearch
import redis


def test_find_match(monkeypatch: pytest.MonkeyPatch):
    # Mocking the constructor and setting up mock objects
    def mock_constructor(*args, **kwargs):
        return None

    monkeypatch.setattr(PostVectorSearch, "__init__", mock_constructor)

    search_service = PostVectorSearch()
    search_service._model_endpoint = aiplatform.Endpoint
    search_service._index_endpoint = aiplatform.MatchingEngineIndexEndpoint
    search_service._deployed_index_id = "test_index_id"

    # Mocking the predict method of model endpoint
    def mock_model_endpoint_predict(text: str):
        return models.Prediction(
            predictions=[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]],
            deployed_model_id="test_index_id",
        )

    monkeypatch.setattr(aiplatform.Endpoint, "predict", mock_model_endpoint_predict)

    expected_matches = [MatchNeighbor(id="1", distance=0.8)]

    # Mocking the match method of index endpoint
    def mock_index_endpoint_match(
        deployed_index_id: str, queries: list[list[float]], num_neighbors: int
    ):
        return [expected_matches]

    monkeypatch.setattr(
        aiplatform.MatchingEngineIndexEndpoint, "match", mock_index_endpoint_match
    )

    # Testing the find_match method
    matches = search_service.find_match(text="test", num_neighbors=1)

    assert matches == expected_matches


def test_get_posts_from_matches(monkeypatch: pytest.MonkeyPatch):
    # Mocking the Redis pipeline
    class MockRedisPipeline:
        def __enter__(self):
            return MockRedisPipeline()

        def __exit__(self, type, value, traceback):
            pass

        def hgetall(self, name: str):
            return None

        def execute(self):
            return [
                {"title": "test_title", "body": "test_body", "tags": "redis|python"}
            ]

    monkeypatch.setattr(redis.Redis, "pipeline", MockRedisPipeline)

    # Mocking the constructor and setting up mock objects
    def mock_constructor(*args, **kwargs):
        return None

    monkeypatch.setattr(PostVectorSearch, "__init__", mock_constructor)

    search_service = PostVectorSearch()
    search_service._redis_client = redis.Redis

    # Testing the get_posts_from_matches method
    result = search_service.get_posts_from_matches(
        [MatchNeighbor(id="1", distance=0.8)]
    )

    expected = [
        PostMatch(
            id="1",
            distance=0.8,
            post=Post(title="test_title", body="test_body", tags=["redis", "python"]),
        )
    ]

    assert result == expected
