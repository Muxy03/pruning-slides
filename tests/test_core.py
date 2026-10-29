from pruning_slides.core import intermediate_pages, parse_pages


def test_intermediate_pages_keep_the_final_page_of_a_run():
    texts = ["Plan\nfirst", "Plan\nfirst second", "Plan\ncomplete", "Conclusion"]
    assert intermediate_pages(texts) == {0, 1}


def test_distant_evolution_pages_are_grouped_by_their_header():
    texts = ["Plan\n3/131", "Plan\nmore", "Plan\ncomplete", "Next"]
    assert intermediate_pages(texts) == {0, 1}


def test_evolution_does_not_require_a_slide_counter():
    texts = ["Plan\nfirst", "Plan\nsecond", "Plan\ncomplete"]
    assert intermediate_pages(texts) == {0, 1}


def test_parse_pages_supports_numbers_ranges_and_deduplication():
    assert parse_pages("1, 3-5, 5", 6) == [0, 2, 3, 4]


def test_parse_pages_rejects_out_of_range_pages():
    try:
        parse_pages("0", 3)
    except ValueError:
        pass
    else:
        raise AssertionError("expected invalid page selection")
