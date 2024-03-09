import numpy as np
import numpy.typing as npt


def get_aligned_masked_array(
    masked_array: npt.NDArray[np.int_], indexed_axes: bool = True
) -> str:
    rows, columns = masked_array.shape

    if indexed_axes:
        return "\n".join(
            [
                "".join([f"{row_num:>4}" for row_num in ["     |", *range(rows - 2)]]),
                "═" * (4 * rows),
                *[
                    "".join(
                        [
                            f"{rows - i - 3:>4} ║",
                            *[
                                f"{element:>4}"
                                for element in str(row)
                                .strip("[]")
                                .replace("'", "")
                                .split(" ")[1:-1]
                                if element != ""
                            ],
                        ]
                    )
                    for i, row in enumerate(masked_array[1:-1])
                ],
            ]
        )
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
