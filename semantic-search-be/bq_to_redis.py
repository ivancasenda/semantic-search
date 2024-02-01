import sys
import math
from typing import Generator, Any
import pandas as pd
from google.cloud import bigquery
from tqdm.auto import tqdm


PROJECT_ID = "stackoverflow-semantic-search"
QUERY_TEMPLATE = "SELECT id, title, LEFT(body, 100) as body, tags FROM bigquery-public-data.stackoverflow.posts_questions WHERE creation_date BETWEEN '2018-01-01' AND '2022-06-01' AND score > 0 ORDER BY creation_date LIMIT {limit} OFFSET {offset}"
BQ_CHUNK_SIZE = 220167
BQ_TOTAL_ROWS = 3082338


def query_bigquery_chunks(
    client: bigquery.Client,
    query_template: str,
    max_rows: int,
    rows_per_chunk: int,
    start_chunk: int = 0,
) -> Generator[pd.DataFrame, Any, None]:
    """Query BigQuery in chunks and yield DataFrames.

    Args:
        client (bigquery.Client): BigQuery client.
        query_template (str): Template for the BigQuery SQL query.
        max_rows (int): Maximum number of rows to fetch.
        rows_per_chunk (int): Number of rows to fetch per chunk.
        start_chunk (int): Starting chunk index.

    Yields:
        pd.DataFrame: A DataFrame containing the query results for each chunk.
    """
    if start_chunk + rows_per_chunk > max_rows:
        raise ValueError(
            f"start_chunk + rows_per_chunk bigger than max_rows: {start_chunk} + {rows_per_chunk} > {max_rows}"
        )
    for offset in range(start_chunk, max_rows, rows_per_chunk):
        if offset + rows_per_chunk > max_rows:
            rows_per_chunk = max_rows - offset
        query = query_template.format(limit=rows_per_chunk, offset=offset)
        query_job = client.query(query)
        rows = query_job.result()
        df = rows.to_dataframe()
        yield df


def string_escape(arg):
    """Escape and convert argument to string."""
    return (
        str(arg).encode("unicode_escape").decode("utf-8")
    )  # to string and escape string


def gen_redis_proto(*cmd):
    """Generate a Redis protocol message."""
    proto = ""
    proto += "*" + str(len(cmd)) + "\r\n"
    for arg in cmd:
        proto += (
            "$" + str(len(string_escape(arg))) + "\r\n" + string_escape(arg) + "\r\n"
        )
    return proto


def run():
    """Main function to fetch data from BigQuery and store in Redis."""
    client = bigquery.Client(project=PROJECT_ID)
    for df in tqdm(
        query_bigquery_chunks(
            client=client,
            query_template=QUERY_TEMPLATE,
            max_rows=BQ_TOTAL_ROWS,
            rows_per_chunk=BQ_CHUNK_SIZE,
        ),
        total=math.ceil(BQ_TOTAL_ROWS / BQ_CHUNK_SIZE),
        position=0,
        desc="Chunk of rows from BigQuery",
    ):
        ids = df.id.tolist()
        titles = df.title.tolist()
        bodies = df.body.tolist()
        tags_list = df.tags.tolist()

        for id, title, body, tags in tqdm(
            zip(ids, titles, bodies, tags_list), total=len(ids), position=0
        ):
            sys.stdout.write(
                gen_redis_proto(
                    "HSET",
                    id,
                    "title",
                    title,
                    "body",
                    body,
                    "tags",
                    tags,
                )
            )


if __name__ == "__main__":
    run()
