from context_core.retrieval import search_receipts, select_sources


def test_late_cited_primary_source_is_not_lost_to_first_eight_results():
    junk = [
        {"url": f"https://unknown.example/{i}", "title": "Unrelated"} for i in range(12)
    ]
    url = "https://www.nasa.gov/benchmark-methodology/"
    payload = {
        "output": [
            {
                "type": "web_search_call",
                "results": junk + [{"url": url, "title": "Benchmark methodology"}],
            },
            {
                "type": "message",
                "content": [{"annotations": [{"type": "url_citation", "url": url}]}],
            },
        ]
    }
    candidates, searched = search_receipts(payload)
    assert searched and len(candidates) == 13
    selected = select_sources(candidates, ["benchmark methodology"], limit=8)
    assert selected[0]["url"] == url and selected[0]["cited_by_provider"]


def test_primary_inspectable_documents_precede_pdf_and_out_of_coverage_pages():
    sources = [
        {"url": "https://unknown.example/weather", "title": "Weather"},
        {"url": "https://www.noaa.gov/weather.pdf", "title": "Weather"},
        {"url": "https://www.noaa.gov/weather", "title": "Weather"},
        {"url": "https://en.wikipedia.org/wiki/Weather", "title": "Weather"},
    ]
    selected = select_sources(sources, ["weather"], limit=2)
    assert [s["url"] for s in selected] == [sources[2]["url"], sources[3]["url"]]


def test_model_written_urls_without_search_receipts_are_excluded():
    candidates, searched = search_receipts(
        {
            "output": [
                {
                    "type": "message",
                    "content": [
                        {
                            "annotations": [
                                {"type": "url_citation", "url": "https://www.nasa.gov/"}
                            ]
                        }
                    ],
                }
            ]
        }
    )
    assert candidates == [] and not searched
