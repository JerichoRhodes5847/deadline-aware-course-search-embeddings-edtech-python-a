"""Domain models and the in-memory course document search decision."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date
from typing import Protocol, Sequence

from pydantic import BaseModel, Field


class CourseDocument(BaseModel):
    document_id: str = Field(min_length=1)
    course_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)
    delivery_week: int = Field(ge=1)
    learner_deadline: date
    educator_report_label: str = Field(min_length=1)


class IndexRequest(BaseModel):
    documents: list[CourseDocument] = Field(min_length=1)


class IndexResult(BaseModel):
    indexed: int


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    learner_date: date
    limit: int = Field(default=5, ge=1, le=20)


class SearchHit(BaseModel):
    document_id: str
    course_id: str
    title: str
    delivery_week: int
    learner_deadline: date
    educator_report_label: str
    similarity: float
    deadline_status: str


class SearchResult(BaseModel):
    hits: list[SearchHit]


class Embedder(Protocol):
    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        raise AssertionError("Protocol method called directly")


@dataclass(frozen=True)
class _IndexedDocument:
    document: CourseDocument
    embedding: list[float]


def _cosine(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right) or not left:
        raise ValueError("Embeddings must have the same non-zero dimension")
    denominator = math.sqrt(sum(x * x for x in left)) * math.sqrt(sum(x * x for x in right))
    return sum(x * y for x, y in zip(left, right)) / denominator if denominator else 0.0


class CourseSearchIndex:
    """Small process-local index for a runnable architecture example."""

    def __init__(self, embedder: Embedder) -> None:
        self._embedder = embedder
        self._documents: dict[str, _IndexedDocument] = {}

    def index(self, documents: Sequence[CourseDocument]) -> int:
        vectors = self._embedder.embed([document.content for document in documents])
        if len(vectors) != len(documents):
            raise ValueError("Embedding count must match document count")
        for document, embedding in zip(documents, vectors):
            self._documents[document.document_id] = _IndexedDocument(document, embedding)
        return len(documents)

    def search(self, request: SearchRequest) -> list[SearchHit]:
        query_vector = self._embedder.embed([request.query])[0]
        ranked = sorted(
            self._documents.values(),
            key=lambda item: (
                _cosine(query_vector, item.embedding),
                item.document.learner_deadline <= request.learner_date,
            ),
            reverse=True,
        )
        return [
            SearchHit(
                document_id=item.document.document_id,
                course_id=item.document.course_id,
                title=item.document.title,
                delivery_week=item.document.delivery_week,
                learner_deadline=item.document.learner_deadline,
                educator_report_label=item.document.educator_report_label,
                similarity=round(_cosine(query_vector, item.embedding), 6),
                deadline_status=(
                    "due" if item.document.learner_deadline <= request.learner_date else "upcoming"
                ),
            )
            for item in ranked[: request.limit]
        ]
