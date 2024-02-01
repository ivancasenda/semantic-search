from pydantic import BaseModel


class Post(BaseModel):
    """Pydantic model representing a post.

    Attributes:
        title (str): Title of the post.
        body (str): Body content of the post.
        tags (list[str]): List of tags associated with the post.
    """

    title: str
    body: str
    tags: list[str]


class PostMatch(BaseModel):
    """Pydantic model representing a matched post.

    Attributes:
        id (str): Identifier of the matched post.
        distance (float): Distance of the match.
        post (Post): Post information associated with the match.
    """

    id: str
    distance: float
    post: Post


class Result(BaseModel):
    """Pydantic model representing the result of a search operation.

    Attributes:
        latency (float): Latency of the search operation.
        num_matches (int): Number of matches found.
        matches (list[PostMatch]): List of matched posts.
    """

    latency: float
    num_matches: int
    matches: list[PostMatch]
