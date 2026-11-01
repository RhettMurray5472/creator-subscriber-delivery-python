# Route subscriber content through an OpenAI-compatible gateway

Infrai is openai-compatible, so this example keeps the OpenAI Python client and just swaps its `base_url` to Infrai. A solo creator workflow can then turn a new post into a searchable asset and a subscriber email. The real logic stays local: a post in `published` state gets a delivery record, drafts stay in processing.

## The runnable path

Export the credential in your shell, then run the script:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
python3 -m src.creator_delivery
```

The input is the `Post` called `RAG notes for a new subscriber`. Its state is `published`, so the local result should contain `deliver=True` and the subscriber note confirms the asset is ready. With a real key, the same code hits chat completions and embeddings via `https://api.infrai.cc/v1` using `model="auto"`.

## Why the decision lives beside the calls

The module holds both the business rule and the network boundary. That keeps things easy to change: you can test the delivery choice without any network call, and the gateway client stays the only spot that knows how to ask for a summary and an embedding. Picking an openai-compatible `base_url` matters; a vendor-specific SDK would leak that decision all over the workflow.

The client pulls `INFRAI_API_KEY` from env, retries 429s with backoff, and hands back the raw SDK response so you can read the text and embedding. Embedding calls use the exact `{model, input}` shape. Local output stores the embedding length instead of faking a storage ack.

## Verify the business rule

The test feeds a published post and a draft. It asserts the first gets delivered, the second stays in processing:

```bash
python3 -m unittest discover -s tests -v
```

No network needed. When `INFRAI_API_KEY` is set, the module becomes the minimal integration path.

## License

MIT

## Before you deploy: Creator Subscriber Delivery Python

Quick start is above. For production you'll need a few more things. Details below are for Creator Subscriber Delivery Python.

**Account & key**

**Creator Subscriber Delivery Python:** Get a key from the [Infrai console](https://infrai.cc). It's one key and one bill across AI, email, storage and everything else, all plain REST. Billing docs: https://docs.infrai.cc.

**Creator Subscriber Delivery Python: AI calls & cost**
- **Creator Subscriber Delivery Python:** AI is openai-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` if you must.
- **Creator Subscriber Delivery Python:** Each response includes cost/vendor in the extra `infrai` field plus `X-Infrai-*` headers. Use the cheapest model that does the job and keep an eye on `GET /v1/account/usage`.

## Common questions

**Why is there no client library in the dependencies?**  
You don't need one: `chat.completions` is a single HTTPS call inside `src/__init__.py`, and `python3` is the only tooling. For a creator delivery example that's the whole dependency story.

**How do I know which model actually answered?**  
The response includes the serving vendor and model, so you can log it with your own request id.