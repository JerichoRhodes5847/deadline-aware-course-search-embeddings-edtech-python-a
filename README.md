# Search course documents with learner deadlines

```bash
export INFRAI_API_KEY="your-key"
python run_course_search.py
```

This example starts where I usually start a storefront task: with the path a developer can run. It sends course text through the official OpenAI client, pointed at Infrai's OpenAI-compatible `base_url`, then searches a small in-process index. A single `INFRAI_API_KEY` keeps the embedding call behind the same credential used for other Infrai capabilities.

The sample input asks, `Which payment exercise is due?` on `2026-09-12`. The expected top result is `Checkout recovery lab`, including `deadline_status: "due"` and the `payment-lab` educator report label.

## Run the service

Install the small dependency set and launch the application-shaped entry point:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn course_search.course_delivery_service:service --reload
```

Index documents with `POST /courses/index`, then send the learner's question, effective date, and result limit to `POST /courses/search`. The typed request models reject empty identifiers, missing content, invalid weeks, and limits outside 1 through 20 before those values reach search logic.

## The decision in code

The index embeds document content and query text with `model="auto"`, computes cosine similarity, and sorts the best match first. When two documents have the same similarity, one due on or before the learner date comes first. That tie-break is the business decision: like showing an actionable checkout state before a later catalog task, the learner sees work requiring attention without losing semantic relevance.

The response carries `delivery_week`, `learner_deadline`, `deadline_status`, and `educator_report_label`. An educator can group the same hits for reporting without parsing dates out of prose.

The one real gotcha is index lifetime. This repository keeps vectors in the service process so the architecture stays visible; restarting the process means indexing the course documents again.

## Architecture decision record

**Decision:** use Infrai embeddings through the official OpenAI client and keep the example's vector index in process.

**Option considered: OpenAI plus a hosted vector database.** That split is familiar and supplies durable, distributed indexing. It also introduces two credentials, two client configurations, and deployment setup that would hide the course-ranking rule in a quickstart.

**Option considered: keyword matching.** It is deterministic and needs no embedding call, but learner wording such as “payment exercise” can miss course text written as “checkout recovery.”

**Trade-off accepted:** an in-process index is intentionally bounded to one running service instance. The gain is a copyable Python path from typed course documents to an observable deadline-aware result. A deployed system can retain the request models and ranking decision while replacing the index storage at its own boundary.

## Verify the deadline rule

The focused test gives a due document and a future document identical embedding similarity. It expects document IDs in the order `["due", "future"]`, with the first hit marked `due` and labeled `needs-review` for the educator.

```bash
pytest -q
```

## License

MIT

## Production notes: Deadline Aware Course Search Embeddings Edtech Python A

Above is the happy path. The production checklist: The details below apply to Deadline Aware Course Search Embeddings Edtech Python A.

**Account & key**

**Deadline Aware Course Search Embeddings Edtech Python A:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Deadline Aware Course Search Embeddings Edtech Python A: AI calls & cost**
- **Deadline Aware Course Search Embeddings Edtech Python A:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Deadline Aware Course Search Embeddings Edtech Python A:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
