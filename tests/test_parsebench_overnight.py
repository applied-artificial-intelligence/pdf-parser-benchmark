from datetime import datetime, timezone

from pdf_bench.parsebench_overnight import allocations, window_end


def test_daytime_and_both_sides_of_midnight_obey_new_york_window():
    assert window_end(datetime(2026, 10, 18, 1, 59, tzinfo=timezone.utc)) is None
    assert window_end(datetime(2026, 10, 18, 11, tzinfo=timezone.utc)) is None
    for hour in (2, 6, 10):
        end = window_end(datetime(2026, 10, 18, hour, tzinfo=timezone.utc))
        assert end.astimezone(timezone.utc) == datetime(2026, 10, 18, 11, tzinfo=timezone.utc)
    # The autumn clock change creates a ten-hour window, still ending at local 07:00.
    end = window_end(datetime(2026, 11, 1, 2, tzinfo=timezone.utc))
    assert end.astimezone(timezone.utc) == datetime(2026, 11, 1, 12, tzinfo=timezone.utc)


def test_parallel_queue_shares_a_global_budget_instead_of_multiplying_it_per_parser():
    jobs = [
        {"backend": name, "priority": priority, "workers": workers}
        for name, priority, workers in [
            ("docling", 0, 1),
            ("marker", 1, 2),
            ("unstructured", 2, 1),
            ("pymupdf4llm", 3, 2),
            ("pypdf", 4, 2),
            ("pdfminer", 4, 2),
        ]
    ]
    selected = allocations(jobs, 8)
    assert sum(count for _, count in selected) == 8
    assert len(selected) == 5
    assert next(count for job, count in selected if job["backend"] == "docling") == 1
    assert all(count <= job["workers"] for job, count in selected)
    # Existing active calls consume capacity before admitting any further parser.
    assert sum(count for _, count in allocations(jobs, 1)) == 1
