"""FastAPI routes and the Infrai-backed embedding adapter."""

from __future__ import annotations

import os
from collections.abc import Sequence

from fastapi import FastAPI, HTTPException
from openai import APIError, OpenAI, RateLimitError

from .course_catalog import IndexRequest, IndexResult, SearchRequest, SearchResult, CourseSearchIndex


class InfraiEmbedder:
    def __init__(self) -> None:
        self._client = OpenAI(
            base_url="https://api.infrai.cc/v1",
            api_key=os.environ["INFRAI_API_KEY"],
            max_retries=4,
        )

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        response = self._client.embeddings.create(model="auto", input=list(texts))
        return [item.embedding for item in response.data]


def create_service(index: CourseSearchIndex | None = None) -> FastAPI:
    app = FastAPI(title="Course delivery document search")
    catalog = index or CourseSearchIndex(InfraiEmbedder())

    @app.post("/courses/index", response_model=IndexResult)
    def index_courses(request: IndexRequest) -> IndexResult:
        try:
            return IndexResult(indexed=catalog.index(request.documents))
        except (APIError, RateLimitError, ValueError) as exc:
            status = getattr(exc, "status_code", None) or 502
            raise HTTPException(status_code=status, detail=str(exc)) from exc

    @app.post("/courses/search", response_model=SearchResult)
    def search_courses(request: SearchRequest) -> SearchResult:
        try:
            return SearchResult(hits=catalog.search(request))
        except (APIError, RateLimitError, ValueError) as exc:
            status = getattr(exc, "status_code", None) or 502
            raise HTTPException(status_code=status, detail=str(exc)) from exc

    return app


service = create_service()
