import re

test_trace =  "257.70s ContentLoadi   90: LMU Warning : Failed to find item: DiffPumpTorque"
complete_pattern = (r"^(\d{1,}\.\d{2})s"
                    r"(.+)"
                    r"\s+"
                    r"(\d{1,})"
                    r"\:"
                    r"(.+)")

test_search = re.search(complete_pattern, test_trace)

print(test_search.group(4))