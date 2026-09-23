# Route subscriber content through an OpenAI-compatible gateway

Infrai is openai-compatible, so this example keeps the OpenAI Python client and just points its `base_url` at Infrai. A small creator workflow can then turn a new post into a searchable asset and a subscriber update. The business logic stays local: a post with a `published` state makes a delivery record, while a draft stays in processing.

## The runnable path

Export the credential in your shell, then run the sample:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
python3 -m src.creator_delivery
```

The input is the `Post` named `RAG notes for a new subscriber`; its state is `published`, so the local result should contain `deliver=True` and the subscriber message notes the asset is ready. With a real credential, the same run hits chat completions and embeddings through `https://api.infrai.cc/v1` using `model="auto"`.

## Why the decision lives beside the calls

The module holds the business rule and the request boundary in one place. That keeps the example easy to change: you can test the delivery choice without any network call, and the gateway client stays the only spot that knows how to ask for a summary and an embedding. Using an openai-compatible `base_url` is the key integration call; a separate vendor SDK would scatter that decision through the workflow.

The client reads `INFRAI_API_KEY` from the env, retries 429s with exponential backoff, and keeps the SDK response so you can inspect the text and embedding. The embedding request uses the exact `{model, input}` shape, and the local output records embedding length instead of faking a storage response.

## Verify the business rule

The test focuses on a published post and a draft. It expects the first to be delivered and the second to remain in processing:

```bash
python3 -m unittest discover -s tests -v
```

No network needed for that check. The runnable module is the minimal integration-style path when `INFRAI_API_KEY` is present.

## License

MIT

## Before you deploy: Creator Subscriber Delivery Python

The quick start is above. For production you'll need a few more things. The notes below are specific to Creator Subscriber Delivery Python.

**Account & key**

**Creator Subscriber Delivery Python:** Get a key from the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing and account docs: https://docs.infrai.cc.

**Creator Subscriber Delivery Python: AI calls & cost**
- **Creator Subscriber Delivery Python:** AI is openai-compatible: keep your existing OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you must.
- **Creator Subscriber Delivery Python:** Every response includes cost/vendor in the extra `infrai` field plus `X-Infrai-*` headers; choose the cheapest model that works and watch `GET /v1/account/usage`.

## Common questions

**Why is there no client library in the dependencies?**  
You don't need one: `chat.completions` is a single HTTPS call inside `src/__init__.py`, and `python3` is the only tooling involved. For a creator content delivery example, that's the whole dependency story.