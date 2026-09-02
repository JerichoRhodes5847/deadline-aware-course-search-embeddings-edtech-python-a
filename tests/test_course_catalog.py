from datetime import date
from typing import Sequence

from course_search.course_catalog import CourseDocument, CourseSearchIndex, SearchRequest


class FixedEmbedder:
    vectors = {
        "payment exercise": [1.0, 0.0],
        "due payment lab": [1.0, 0.0],
        "future payment lab": [1.0, 0.0],
    }

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        return [self.vectors[text] for text in texts]


def test_due_document_wins_similarity_tie_and_exposes_reporting_context() -> None:
    index = CourseSearchIndex(FixedEmbedder())
    index.index(
        [
            CourseDocument(
                document_id="future",
                course_id="commerce-201",
                title="Next payment lab",
                content="future payment lab",
                delivery_week=4,
                learner_deadline=date(2026, 9, 20),
                educator_report_label="future-work",
            ),
            CourseDocument(
                document_id="due",
                course_id="commerce-201",
                title="Due payment lab",
                content="due payment lab",
                delivery_week=3,
                learner_deadline=date(2026, 9, 12),
                educator_report_label="needs-review",
            ),
        ]
    )

    hits = index.search(
        SearchRequest(query="payment exercise", learner_date=date(2026, 9, 12), limit=2)
    )

    assert [hit.document_id for hit in hits] == ["due", "future"]
    assert hits[0].deadline_status == "due"
    assert hits[0].educator_report_label == "needs-review"
