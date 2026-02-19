def validate_results_against_memory(results, memory):

    mismatches = {}

    if not memory.attributes:
        return mismatches

    for attr, expected_value in memory.attributes.items():

        found_match = False

        for r in results:
            title = r.get("url", "").lower()

            if expected_value.lower() in title:
                found_match = True
                break

        if not found_match:
            mismatches[attr] = expected_value

    return mismatches
