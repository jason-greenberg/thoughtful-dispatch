from math import prod

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from thoughtful_dispatch.sorter import DIMENSION_LIMIT_CM, MASS_LIMIT_KG, VOLUME_LIMIT_CM, sort

# --- Helper Constants ---
SMALL_DELTA = 1e-9
JUST_BELOW_DIM = DIMENSION_LIMIT_CM - SMALL_DELTA
JUST_ABOVE_DIM = DIMENSION_LIMIT_CM + SMALL_DELTA
JUST_BELOW_MASS = MASS_LIMIT_KG - SMALL_DELTA
JUST_ABOVE_MASS = MASS_LIMIT_KG + SMALL_DELTA

SAFE_DIM = 10.0  # Well below dim limit
SAFE_MASS = 1.0  # Well below mass limit

DIMS_AT_VOLUME_LIMIT = (100.0, 100.0, 100.0)  # Volume = 1,000,000
DIMS_JUST_BELOW_VOLUME_LIMIT = (100.0, 100.0, 100.0 - SMALL_DELTA * 10)  # Ensure Vol < LIMIT
DIMS_JUST_ABOVE_VOLUME_LIMIT = (100.0, 100.0, 100.0 + SMALL_DELTA * 10)  # Ensure Vol > LIMIT


# Volume Calculation Helper
def calc_volume(*dims):
    try:
        return prod(dims)
    except OverflowError:
        return float("inf")  # Treat overflow as definitely bulky


# --- Tests for 'STANDARD' cases ---
class TestStandardCases:
    """Tests scenarios resulting in 'STANDARD' classification."""

    def test_standard_when_all_well_below_limits(self):
        """Package should be STANDARD if all dims, volume, and mass are clearly below limits."""
        assert sort(SAFE_DIM, SAFE_DIM, SAFE_DIM, SAFE_MASS) == "STANDARD"

    def test_standard_when_dims_and_mass_just_below_limits(self):
        """Package should be STANDARD when dimensions and mass approach but don't reach limits."""
        # Ensure volume is also below limit
        vol_dims = (JUST_BELOW_DIM, SAFE_DIM, SAFE_DIM)
        assert calc_volume(*vol_dims) < VOLUME_LIMIT_CM
        assert sort(*vol_dims, JUST_BELOW_MASS) == "STANDARD"

    def test_standard_when_volume_just_below_limit(self):
        """Package should be STANDARD when volume approaches but doesn't reach the limit."""
        assert calc_volume(*DIMS_JUST_BELOW_VOLUME_LIMIT) < VOLUME_LIMIT_CM
        assert sort(*DIMS_JUST_BELOW_VOLUME_LIMIT, JUST_BELOW_MASS) == "STANDARD"

    def test_standard_when_mass_just_below_limit(self):
        """Package should be STANDARD when mass approaches but doesn't reach the limit."""
        assert sort(SAFE_DIM, SAFE_DIM, SAFE_DIM, JUST_BELOW_MASS) == "STANDARD"


# --- Tests for 'SPECIAL' cases ---
class TestSpecialCases:
    """Tests scenarios resulting in 'SPECIAL' classification (Bulky OR Heavy)."""

    @pytest.mark.parametrize("dim_at_or_above", [DIMENSION_LIMIT_CM, JUST_ABOVE_DIM])
    def test_special_when_one_dimension_at_or_over_limit(self, dim_at_or_above):
        """SPECIAL if any single dimension hits or exceeds the limit, mass okay."""
        assert sort(dim_at_or_above, SAFE_DIM, SAFE_DIM, SAFE_MASS) == "SPECIAL"
        assert sort(SAFE_DIM, dim_at_or_above, SAFE_DIM, SAFE_MASS) == "SPECIAL"
        assert sort(SAFE_DIM, SAFE_DIM, dim_at_or_above, SAFE_MASS) == "SPECIAL"

    @pytest.mark.parametrize("dims_at_or_above_vol", [DIMS_AT_VOLUME_LIMIT, DIMS_JUST_ABOVE_VOLUME_LIMIT])
    def test_special_when_volume_at_or_over_limit(self, dims_at_or_above_vol):
        """SPECIAL if volume hits or exceeds the limit, dimensions individually okay, mass okay."""
        assert all(d < DIMENSION_LIMIT_CM for d in dims_at_or_above_vol)
        assert calc_volume(*dims_at_or_above_vol) >= VOLUME_LIMIT_CM
        assert sort(*dims_at_or_above_vol, SAFE_MASS) == "SPECIAL"

    @pytest.mark.parametrize("mass_at_or_above", [MASS_LIMIT_KG, JUST_ABOVE_MASS])
    def test_special_when_mass_at_or_over_limit(self, mass_at_or_above):
        """SPECIAL if mass hits or exceeds the limit, dimensions/volume okay."""
        assert sort(SAFE_DIM, SAFE_DIM, SAFE_DIM, mass_at_or_above) == "SPECIAL"

    def test_special_when_dimension_over_limit_and_mass_ok(self):
        """Explicitly test bulky by dimension only."""
        assert sort(DIMENSION_LIMIT_CM, SAFE_DIM, SAFE_DIM, SAFE_MASS) == "SPECIAL"

    def test_special_when_volume_over_limit_and_mass_ok(self):
        """Explicitly test bulky by volume only."""
        assert sort(*DIMS_AT_VOLUME_LIMIT, SAFE_MASS) == "SPECIAL"

    def test_special_when_mass_over_limit_and_dims_volume_ok(self):
        """Explicitly test heavy only."""
        assert sort(SAFE_DIM, SAFE_DIM, SAFE_DIM, MASS_LIMIT_KG) == "SPECIAL"


# --- Tests for 'REJECTED' cases ---
class TestRejectedCases:
    """Tests scenarios resulting in 'REJECTED' classification (Bulky AND Heavy)."""

    @pytest.mark.parametrize("dim_at_or_above", [DIMENSION_LIMIT_CM, JUST_ABOVE_DIM])
    @pytest.mark.parametrize("mass_at_or_above", [MASS_LIMIT_KG, JUST_ABOVE_MASS])
    def test_rejected_when_dimension_at_or_over_and_mass_at_or_over(self, dim_at_or_above, mass_at_or_above):
        """REJECTED if bulky (by dimension) AND heavy."""
        assert sort(dim_at_or_above, SAFE_DIM, SAFE_DIM, mass_at_or_above) == "REJECTED"
        assert sort(SAFE_DIM, dim_at_or_above, SAFE_DIM, mass_at_or_above) == "REJECTED"
        assert sort(SAFE_DIM, SAFE_DIM, dim_at_or_above, mass_at_or_above) == "REJECTED"

    @pytest.mark.parametrize("dims_at_or_above_vol", [DIMS_AT_VOLUME_LIMIT, DIMS_JUST_ABOVE_VOLUME_LIMIT])
    @pytest.mark.parametrize("mass_at_or_above", [MASS_LIMIT_KG, JUST_ABOVE_MASS])
    def test_rejected_when_volume_at_or_over_and_mass_at_or_over(self, dims_at_or_above_vol, mass_at_or_above):
        """REJECTED if bulky (by volume) AND heavy."""
        # Ensure individual dims are okay for this specific volume test
        assert all(d < DIMENSION_LIMIT_CM for d in dims_at_or_above_vol)
        assert calc_volume(*dims_at_or_above_vol) >= VOLUME_LIMIT_CM
        assert sort(*dims_at_or_above_vol, mass_at_or_above) == "REJECTED"

    def test_rejected_when_bulky_by_dimension_and_volume_and_heavy(self):
        """REJECTED if heavy and bulky by both dimension and volume criteria."""
        # Example: One dim >= limit, AND volume >= limit, AND mass >= limit
        bulky_dims = (DIMENSION_LIMIT_CM, 100.0, 100.0)  # Exceeds dim limit, also exceeds vol limit
        assert calc_volume(*bulky_dims) >= VOLUME_LIMIT_CM
        assert sort(*bulky_dims, MASS_LIMIT_KG) == "REJECTED"
        assert sort(*bulky_dims, JUST_ABOVE_MASS) == "REJECTED"


# --- Invalid Input Tests ---
class TestSortInvalidInput:
    """Tests handling of invalid inputs."""

    @pytest.mark.parametrize("invalid_value", [0, -1.0, -SMALL_DELTA])
    @pytest.mark.parametrize("position", [0, 1, 2, 3])  # Test invalid value in each arg position
    def test_non_positive_inputs_raise_value_error(self, invalid_value, position):
        """Verifies non-positive dimensions or mass raise ValueError."""
        args = [SAFE_DIM] * 3 + [SAFE_MASS]
        args[position] = invalid_value
        with pytest.raises(ValueError, match="Dimensions and mass must be positive"):
            sort(*args)

    @pytest.mark.parametrize("invalid_value", ["10", None, [10], {"a": 1}, float("nan")])
    @pytest.mark.parametrize("position", [0, 1, 2, 3])  # Test invalid value in each arg position
    def test_non_numeric_inputs_raise_type_error(self, invalid_value, position):
        """Verifies non-numeric inputs raise TypeError."""
        args = [SAFE_DIM] * 3 + [SAFE_MASS]
        args[position] = invalid_value
        # Match the more specific error message from the updated function
        expected_msg = f"All inputs must be numeric, received type {type(invalid_value)}"
        with pytest.raises(TypeError, match=expected_msg):
            sort(*args)


# --- Property-Based Fuzzy Tests ---
positive_float = st.floats(min_value=1e-9, max_value=1e12, allow_nan=False, allow_infinity=False)
dims_tuple = st.tuples(positive_float, positive_float, positive_float)
mass_val = positive_float

dim_clearly_below_limit = st.floats(
    min_value=1e-9, max_value=DIMENSION_LIMIT_CM - 1, allow_nan=False, allow_infinity=False
)
mass_clearly_below_limit = st.floats(min_value=1e-9, max_value=MASS_LIMIT_KG - 1, allow_nan=False, allow_infinity=False)
mass_at_or_above_limit = st.floats(min_value=MASS_LIMIT_KG, max_value=1e12, allow_nan=False, allow_infinity=False)
dim_at_or_above_limit = st.floats(min_value=DIMENSION_LIMIT_CM, max_value=1e12, allow_nan=False, allow_infinity=False)


class TestSortProperties:
    """Core property tests using Hypothesis."""

    @given(w=dim_clearly_below_limit, h=dim_clearly_below_limit, l=dim_clearly_below_limit, m=mass_clearly_below_limit)
    def test_property_standard_when_clearly_within_limits(self, w, h, l, m):
        """Property: Packages clearly within all limits should be STANDARD."""
        # Assume volume is also below the limit (highly likely with these dim limits)
        assume(calc_volume(w, h, l) < VOLUME_LIMIT_CM)
        assert sort(w, h, l, m) == "STANDARD"

    @given(dims=dims_tuple, mass=mass_at_or_above_limit)
    def test_property_rejected_when_heavy_and_known_bulky(self, dims, mass):
        """Property: Heavy packages that are also definitely bulky are REJECTED."""
        w, h, l = dims
        try:
            is_bulky_volume = calc_volume(w, h, l) >= VOLUME_LIMIT_CM
            is_bulky_dimension = w >= DIMENSION_LIMIT_CM or h >= DIMENSION_LIMIT_CM or l >= DIMENSION_LIMIT_CM
            is_bulky = is_bulky_volume or is_bulky_dimension
        except (OverflowError, ValueError):
            # Treat calculation errors as bulky
            is_bulky = True

        # This property specifically tests the REJECTED case, so assume bulky.
        assume(is_bulky)
        assert sort(w, h, l, mass) == "REJECTED"

    @given(dims=dims_tuple, mass=mass_val)
    def test_property_output_is_always_valid_string(self, dims, mass):
        """Property: The output is always one of the valid classification strings."""
        # Protect against potential calculation errors in sort for very large numbers
        try:
            result = sort(*dims, mass)
            assert result in ["STANDARD", "SPECIAL", "REJECTED"]
        except (OverflowError, ValueError):
            pass

    @given(w=dim_at_or_above_limit, h=positive_float, l=positive_float, m=mass_clearly_below_limit)
    def test_property_special_if_heavy_dimension_and_not_heavy(self, w, h, l, m):
        """Property: If at least one dim is bulky and mass is not heavy, should be SPECIAL."""
        # Avoid accidental rejection by making other dims small
        h = min(h, DIMENSION_LIMIT_CM / 2)
        l = min(l, DIMENSION_LIMIT_CM / 2)
        # Ensure volume isn't the cause of bulkiness unless the single dim forces it
        assume(calc_volume(w, h, l) < VOLUME_LIMIT_CM or w >= DIMENSION_LIMIT_CM)
        assert m < MASS_LIMIT_KG
        assert sort(w, h, l, m) == "SPECIAL"
