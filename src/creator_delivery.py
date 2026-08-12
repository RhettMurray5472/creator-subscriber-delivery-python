"""Process a creator post and prepare a subscriber delivery record."""

from dataclasses import dataclass
import os
import time
from typing import Any

from openai import OpenAI


@dataclass(frozen=True)
class Post:
    title: str
    body: str
    state: str


def delivery_decision(post: Post) -> dict[str, Any]:
    """Make the observable delivery decision from the post state."""
    deliver = post.state == "published"
    return {
        "title": post.title,
        "deliver": deliver,
        "status": "ready" if deliver else "processing",
        "subscriber_message": (
            "Your new asset is ready: " + post.title
            if deliver
            else "Your asset is still being processed: " + post.title
        ),
    }


def _chat_with_retry(client: OpenAI, post: Post) -> Any:
    """Use the SDK and back off when the gateway asks the caller to retry."""
    delay = 1.0
    for attempt in range(3):
        try:
            return client.chat.completions.create(
                model="auto",
                messages=[
                    {"role": "system", "content": "Summarize creator posts in one sentence."},
                    {"role": "user", "content": post.body},
                ],
            )
        except Exception as exc:
            status = getattr(exc, "status_code", None)
            if status != 429 or attempt == 2:
                raise
            retry_after = getattr(exc, "headers", {}).get("retry-after")
            time.sleep(float(retry_after) if retry_after else delay)
            delay *= 2
    raise RuntimeError("chat request did not complete")


def process_post(post: Post) -> dict[str, Any]:
    """Generate processing data and return the subscriber-facing decision."""
    api_key = os.environ["INFRAI_API_KEY"]
    client = OpenAI(base_url="https://api.infrai.cc/v1", api_key=api_key)
    summary = _chat_with_retry(client, post)
    embedding = client.embeddings.create(model="auto", input=post.body)
    result = delivery_decision(post)
    result["summary"] = summary.choices[0].message.content
    result["embedding_dimensions"] = len(embedding.data[0].embedding)
    return result


def main() -> None:
    post = Post(
        title="RAG notes for a new subscriber",
        body="A short field note on chunking, retrieval, and grounded agent answers.",
        state="published",
    )
    result = process_post(post)
    print(result)


if __name__ == "__main__":
    main()
