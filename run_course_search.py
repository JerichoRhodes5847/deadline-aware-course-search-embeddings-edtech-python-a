"""Index a small course catalog and run a learner-deadline search."""

from datetime import date

from course_search.course_catalog import CourseDocument, CourseSearchIndex, SearchRequest
from course_search.course_delivery_service import InfraiEmbedder


def main() -> None:
    index = CourseSearchIndex(InfraiEmbedder())
    index.index(
        [
            CourseDocument(
                document_id="checkout-lab",
                course_id="commerce-201",
                title="Checkout recovery lab",
                content="Submit the checkout recovery exercise and explain payment retry behavior.",
                delivery_week=3,
                learner_deadline=date(2026, 9, 12),
                educator_report_label="payment-lab",
            ),
            CourseDocument(
                document_id="catalog-reading",
                course_id="commerce-201",
                title="Catalog modeling notes",
                content="Read the product catalog modeling notes before the storefront workshop.",
                delivery_week=4,
                learner_deadline=date(2026, 9, 19),
                educator_report_label="catalog-reading",
            ),
        ]
    )
    result = index.search(
        SearchRequest(query="Which payment exercise is due?", learner_date=date(2026, 9, 12), limit=1)
    )
    print(result[0].model_dump_json(indent=2))


if __name__ == "__main__":
    main()
