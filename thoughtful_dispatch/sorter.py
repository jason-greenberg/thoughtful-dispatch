from math import isnan
from numbers import Number

# Constants
VOLUME_LIMIT_CM = 1_000_000
DIMENSION_LIMIT_CM = 150
MASS_LIMIT_KG = 20


def sort(width: float, height: float, length: float, mass: float) -> str:
    """
    Decide dispatch stack for a package.

    Returns:
        'STANDARD', 'SPECIAL', or 'REJECTED'
    """
    # input validation
    all_values = [width, height, length, mass]

    def is_valid_number(val):
        return isinstance(val, Number) and not (isinstance(val, float) and isnan(val))

    # check if all inputs are numbers
    if not all(is_valid_number(val) for val in all_values):
        first_bad_type = next(filter(lambda v: not is_valid_number(v), all_values))
        msg = f"All inputs must be numeric, received type {type(first_bad_type)}"
        raise TypeError(msg)

    # check for non-positive values
    if not all(val > 0 for val in all_values):
        first_bad_value = next(filter(lambda v: v <= 0, all_values))
        msg = f"Dimensions and mass must be positive, received {first_bad_value}"
        raise ValueError(msg)

    # bulkiness check
    volume = width * height * length
    is_bulky_volume = volume >= VOLUME_LIMIT_CM
    is_bulky_dimension = width >= DIMENSION_LIMIT_CM or height >= DIMENSION_LIMIT_CM or length >= DIMENSION_LIMIT_CM
    is_bulky = is_bulky_volume or is_bulky_dimension

    # heaviness check
    is_heavy = mass >= MASS_LIMIT_KG

    # stack decision
    if is_bulky and is_heavy:
        return "REJECTED"
    if is_bulky or is_heavy:
        return "SPECIAL"
    return "STANDARD"


# Example calls
if __name__ == "__main__":
    print("Running package sorting examples:")

    def print_sort_result(w, h, l, m, description):
        result = sort(w, h, l, m)
        print(f"\n{description}:")
        print(f"Inputs: w={w}, h={h}, l={l}, m={m} -> Result: {result}")

    # Ex 1: Standard package
    print_sort_result(50, 50, 50, 10, "Standard package")  # STANDARD

    # Ex 2: Heavy package
    print_sort_result(50, 50, 50, 25, "Heavy package")  # SPECIAL

    # Ex 3: Bulky package (large dimension)
    print_sort_result(160, 50, 50, 10, "Bulky package (large dimension)")  # SPECIAL

    # Ex 4: Bulky package (large volume)
    print_sort_result(100, 100, 100, 10, "Bulky package (large volume)")  # SPECIAL

    # Ex 5: Rejected package (bulky and heavy)
    print_sort_result(100, 100, 100, 25, "Rejected package (bulky and heavy)")  # REJECTED

    # Ex 6: Rejected package (large dimension and heavy)
    print_sort_result(160, 50, 50, 21, "Rejected package (large dimension and heavy)")  # REJECTED

    # Ex 7: Edge case - exactly at volume limit
    print_sort_result(100, 100, 100, 19.9, "Edge case - exactly at volume limit")  # SPECIAL

    # Ex 8: Edge case - exactly at dimension limit
    print_sort_result(150, 50, 50, 19.9, "Edge case - exactly at dimension limit")  # SPECIAL

    # Ex 9: Edge case - exactly at mass limit
    print_sort_result(50, 50, 50, 20, "Edge case - exactly at mass limit")  # SPECIAL

    print("\nTesting invalid inputs:")
    # Ex 10: Non-positive dimension
    try:
        sort(0, 50, 50, 10)
    except ValueError as e:
        print(f"Caught expected error for non-positive input: {e}")

    # Ex 11: Non-numeric input
    try:
        sort(50, 50, "abc", 10)
    except TypeError as e:
        print(f"Caught expected error for non-numeric input: {e}")
