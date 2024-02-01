import redis
import logging
from google.cloud import aiplatform
from google.cloud.aiplatform.matching_engine.matching_engine_index_endpoint import (
    MatchNeighbor,
)
import time

from .schema import Post, PostMatch


logger = logging.getLogger(__name__)

_FIRST_RESULT = 0


def retry(max_retries, wait_time):
    """Decorator for retrying a function in case of exceptions.

    Args:
        max_retries (int): Maximum number of retries.
        wait_time (float): Time to wait between retries in seconds.

    Returns:
        function: Decorated function.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            for retries in range(max_retries):
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    logger.info(f"Try #{retries} failed with {str(e)}: Retrying..:")
                    time.sleep(wait_time)
            raise Exception(f"Max retries of function {func} exceeded, Error: {str(e)}")

        return wrapper

    return decorator


class PostVectorSearch:
    def __init__(
        self,
        model_endpoint_resource: str,
        index_endpoint_resource: str,
        deployed_index_id: str,
        redis_host: str,
        redis_port: str,
    ) -> None:
        """Initialize client for Redis, Vertex AI model, and index endpoints.

        Args:
            model_endpoint_resource: A fully-qualified endpoint resource name or endpoint ID.
                                        Example: "projects/123/locations/us-central1/endpoints/456"
            index_endpoint_resource: A fully-qualified index endpoint resource name or a index ID.
                                        Example: "projects/123/locations/us-central1/index_endpoints/my_index_id"
            deployed_index_id: The user specified ID of the DeployedIndex.
                                specified when deploying index endpoint
            redis_host: redis server host
            redis_port: redis server port
        """
        self._model_endpoint = aiplatform.PrivateEndpoint(model_endpoint_resource)
        logger.info("Connected to vertex ai model endpoint")

        self._index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
            index_endpoint_resource
        )
        logger.info("Connected to vertex ai index endpoint")

        self._deployed_index_id = deployed_index_id

        self._redis_client = redis.Redis(
            host=redis_host, port=redis_port, decode_responses=True
        )

        logger.info(
            f"Initialize redis client on host {redis_host} and port {redis_port}"
        )

    def find_match(self, text: str, num_neighbors: int) -> list[MatchNeighbor]:
        """Convert text to embedding and perform vector search.

        Args:
            text (str): Text to be matched.
            num_neighbors (int): Number of nearest neighbors to retrieve.

        Returns:
            list[MatchNeighbor]: List of matched neighbors.
        """
        if not text:
            raise ValueError("Cannot match empty text!")
        if num_neighbors <= 0:
            raise ValueError("num_neigbhors cannot be less than or equal to 0")

        logger.info(f"trying to match {num_neighbors} neighbors to text {text}")

        embedding: list[float] = self._model_endpoint.predict([text]).predictions[
            _FIRST_RESULT
        ]  # extract single embedding from batch result

        if embedding is None or len(embedding) == 0:
            raise ValueError(f"there is a problem getting embedding for text {text}")

        logger.info(f"resulting embedding dimension: {len(embedding)}")

        logger.info("performing vector search")
        # perform queries on vertex ai vector search for n nearest neighbors
        match_neighbors: list[MatchNeighbor] = self._index_endpoint.match(
            deployed_index_id=self._deployed_index_id,
            queries=[embedding],
            num_neighbors=num_neighbors,
        )[
            _FIRST_RESULT
        ]  # extract a list of match neighbors from batch result
        logger.info(f"found {len(match_neighbors)} match neighbors")
        return match_neighbors

    def get_posts_from_matches(
        self, match_neighbors: list[MatchNeighbor]
    ) -> list[PostMatch]:
        """Query Redis to convert matched neighbors to Post.

        Args:
            match_neighbors (list[MatchNeighbor]): List of matched neighbors.

        Returns:
            list[PostMatch]: List of PostMatch objects.
        """
        logger.info("setting up redis pipeline")

        with self._redis_client.pipeline() as redis_pipeline:
            for match in match_neighbors:
                redis_pipeline.hgetall(match.id)

            logger.info("execute redis pipeline")

            posts_dict: list[dict[str:str]] = redis_pipeline.execute()

        return [
            PostMatch(
                id=match.id,
                distance=round(match.distance, 2),
                post=Post(
                    title=post["title"],
                    body=post["body"],
                    tags=post["tags"].split("|"),
                ),
            )
            for match, post in zip(match_neighbors, posts_dict)
        ]

    @retry(max_retries=5, wait_time=0)
    def search(self, text: str, num_neighbors: int) -> list[PostMatch]:
        """Convert text to embedding, perform vector search, and convert neighbors to PostMatch.

        Args:
            text (str): Search term.
            num_neighbors (int): Number of nearest neighbors.

        Returns:
            list[PostMatch]: List of PostMatch sorted with closest distance first.
        """
        match_neighbors = self.find_match(text, num_neighbors)

        return self.get_posts_from_matches(match_neighbors)
