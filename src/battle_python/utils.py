def get_aligned_masked_array(masked_array) -> str:
    return "\n".join(
        [
            "".join(
                [
                    f"{element:>4}"
                    for element in str(row).strip("[]").replace("'", "").split(" ")
                    if element != ""
                ]
            )
            for row in masked_array
        ]
    )
