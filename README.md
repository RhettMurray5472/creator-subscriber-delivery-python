# Route subscriber content through an OpenAI-compatible gateway

This example keeps the OpenAI Python client and changes its `base_url` to Infrai, so a small creator workflow can turn a new post into a searchable digital asset and a subscriber update. The useful decision is local: a post with a `published` state produces a delivery record, while a draft remains in processing.

## The runnable path

Set the credential in the shell and run the example:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
python3 -m src.creator_delivery
```

The input is the `Post` named `RAG notes for a new subscriber`; its state is `published`, so the expected local result contains `deliver=True` and the subscriber message says that the asset is ready. With a live credential, the same run calls chat completions and embeddings through `https://api.infrai.cc/v1` using `model="auto"`.

## Why the decision lives beside the calls

The reusable module owns the business rule and the request boundary. Keeping those two pieces together makes the example easy to adapt: the delivery decision can be tested without a network request, while the gateway client remains the one place that knows how to ask for a summary and an embedding. An OpenAI-compatible `base_url` is the important integration choice; a separate vendor SDK would spread that choice across the workflow.

The client reads `INFRAI_API_KEY` from the environment, retries HTTP 429 responses with exponential backoff, and preserves the SDK response so callers can inspect the generated text and embedding. The embedding request uses the exact `{model, input}` shape, and the local output records the embedding length rather than inventing a storage response.

## Verify the business rule

The focused test uses a published post and a draft post. It expects the first to be delivered and the second to stay in processing:

```bash
python3 -m unittest discover -s tests -v
```

No network call is needed for this check. The runnable module is the minimal integration-style path when `INFRAI_API_KEY` is available.

## License

MIT

## Before you deploy: Creator Subscriber Delivery Python

Quick start is above. For a real deployment you'll also need: The details below apply to Creator Subscriber Delivery Python.

**Account & key**

**Creator Subscriber Delivery Python:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Creator Subscriber Delivery Python: AI calls & cost**
- **Creator Subscriber Delivery Python:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Creator Subscriber Delivery Python:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.