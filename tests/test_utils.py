import pytest
import math
from datetime import datetime, timezone, timedelta

from vrmapi_async.utils import (
    to_snake_case,
    datetime_to_epoch,
    snake_case_to_camel_case,
)


class TestDateTimeToEpoch:

    @pytest.mark.parametrize(
        "naive_dt_input, expected_epoch",
        [
            (datetime(2023, 1, 1, 12, 0, 0), 1672574400),
            (datetime(2023, 1, 1, 12, 0, 0, 1), 1672574401),
            (datetime(1970, 1, 1, 0, 0, 0), 0),
            (datetime(1970, 1, 1, 0, 0, 0, 1), 1),
        ],
    )
    def test_naive_datetime_conversion(self, naive_dt_input, expected_epoch):
        """Tests conversion of naive datetime objects (assumed as UTC)."""
        assert datetime_to_epoch(naive_dt_input) == expected_epoch

    @pytest.mark.parametrize(
        "aware_dt_input_utc, expected_epoch",
        [
            (datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc), 0),
            (datetime(2023, 5, 15, 10, 30, 45, tzinfo=timezone.utc), 1684146645),
            (
                datetime(2023, 5, 15, 10, 30, 45, 123456, tzinfo=timezone.utc),
                1684146646,
            ),
            (datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc), 1704067200),
        ],
    )
    def test_aware_datetime_conversion_utc(self, aware_dt_input_utc, expected_epoch):
        """Tests conversion of timezone-aware datetime objects already in UTC."""
        assert datetime_to_epoch(aware_dt_input_utc) == expected_epoch

    @pytest.mark.parametrize(
        "year, month, day, hour, minute, second, microsecond, tz_offset_hours, expected_epoch_from_utc_calc",
        [
            (2023, 7, 15, 12, 0, 0, 0, 2, 1689415200),  # UTC: 2023-07-15 10:00:00
            (2023, 7, 15, 5, 0, 0, 0, -5, 1689415200),  # UTC: 2023-07-15 10:00:00
            (
                2023,
                7,
                15,
                12,
                0,
                0,
                1,
                2,
                1689415201,
            ),  # UTC: 2023-07-15 10:00:00.000001
            (
                2023,
                7,
                15,
                5,
                0,
                0,
                999999,
                -5,
                1689415201,
            ),  # UTC: 2023-07-15 10:00:00.999999
        ],
    )
    def test_aware_datetime_conversion_other_timezones(
        self,
        year,
        month,
        day,
        hour,
        minute,
        second,
        microsecond,
        tz_offset_hours,
        expected_epoch_from_utc_calc,
    ):
        """Tests conversion of aware datetimes from various timezones."""
        custom_tz = timezone(timedelta(hours=tz_offset_hours))
        aware_dt = datetime(
            year, month, day, hour, minute, second, microsecond, tzinfo=custom_tz
        )

        utc_equivalent = aware_dt.astimezone(timezone.utc)
        expected_epoch_verified = int(math.ceil(utc_equivalent.timestamp()))
        assert (
            expected_epoch_verified == expected_epoch_from_utc_calc
        ), "Mismatch in test data pre-calculation"

        assert datetime_to_epoch(aware_dt) == expected_epoch_from_utc_calc

    @pytest.mark.parametrize(
        "year, month, day, hour, minute, second, microsecond, expected_epoch",
        [
            (2025, 5, 30, 0, 0, 0, 0, 1748563200),
            (2025, 5, 30, 0, 0, 0, 1, 1748563201),
            (2025, 5, 30, 0, 0, 0, 500000, 1748563201),
            (2025, 5, 30, 0, 0, 0, 999999, 1748563201),
            # Standard rounding case for epoch
            (1970, 1, 1, 0, 0, 0, 999999, 1),  # Rounds 0.999999 up to 1
        ],
    )
    def test_rounding_behavior(
        self, year, month, day, hour, minute, second, microsecond, expected_epoch
    ):
        """Specifically tests the math.ceil rounding behavior."""
        dt_input = datetime(
            year, month, day, hour, minute, second, microsecond, tzinfo=timezone.utc
        )
        assert datetime_to_epoch(dt_input) == expected_epoch

    @pytest.mark.parametrize(
        "naive_dt_input, expected_epoch",
        [
            (datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc), 0),
            (datetime(2021, 9, 1, 12, 30, 15, tzinfo=timezone.utc), 1630499415),
            (datetime(2021, 9, 1, 12, 30, 15, 500), 1630499416),
            (
                datetime(2025, 1, 18, 22, 10, 30, 987654, tzinfo=timezone.utc),
                1737238231,
            ),
        ],
    )
    def test_some_specific_known_timestamps(self, naive_dt_input, expected_epoch):
        assert datetime_to_epoch(naive_dt_input) == expected_epoch


class TestToSnakeCase:

    @pytest.mark.parametrize(
        "input_str, expected_output",
        [
            ("someVariableName", "some_variable_name"),
            ("SomeVariableName", "some_variable_name"),
            ("Value", "value"),
            ("Single", "single"),
            ("A", "a"),
            ("CapWord", "cap_word"),
        ],
    )
    def test_camel_and_pascal_case_conversion(self, input_str, expected_output):
        """Test conversion of CamelCase and PascalCase strings."""
        assert to_snake_case(input_str) == expected_output

    @pytest.mark.parametrize(
        "input_str, expected_output",
        [
            ("my-kebab-string", "my_kebab_string"),
            ("A String With Spaces", "a_string_with_spaces"),
            ("  leading and trailing spaces  ", "leading_and_trailing_spaces"),
            ("word  multiple   spaces", "word_multiple_spaces"),
        ],
    )
    def test_kebab_and_space_case_conversion(self, input_str, expected_output):
        """Test conversion of kebab-case and space-separated strings."""
        assert to_snake_case(input_str) == expected_output

    @pytest.mark.parametrize(
        "input_str, expected_output",
        [
            ("SGViolationRate", "sg_violation_rate"),
            ("HTTPRequest", "http_request"),
            ("MyURLAddress", "my_url_address"),
            ("Ver1Value", "ver1_value"),
            ("Version2Update", "version2_update"),
            ("ANHTMLAbbreviation", "anhtml_abbreviation"),
            ("ABCCode", "abc_code"),
            ("CAMELValue", "camel_value"),
        ],
    )
    def test_acronyms_and_alphanumeric_conversion(self, input_str, expected_output):
        """Test conversion of strings with acronyms and alphanumeric parts."""
        assert to_snake_case(input_str) == expected_output

    @pytest.mark.parametrize(
        "input_str, expected_output",
        [
            ("ALLCAPS", "allcaps"),
            ("ALLCAPSWord", "allcaps_word"),
        ],
    )
    def test_all_caps_conversion(self, input_str, expected_output):
        """Test conversion of all-caps strings."""
        assert to_snake_case(input_str) == expected_output

    @pytest.mark.parametrize(
        "input_str, expected_output",
        [
            ("already_snake_case", "already_snake_case"),
            ("already_snake_case_with_UPPER", "already_snake_case_with_upper"),
            ("ALL_CAPS_SNAKE", "all_caps_snake"),
        ],
    )
    def test_already_snake_or_similar_conversion(self, input_str, expected_output):
        """Test strings that are already snake_case or close to it."""
        assert to_snake_case(input_str) == expected_output

    @pytest.mark.parametrize(
        "input_str, expected_output",
        [
            ("endsWithSeparator-", "ends_with_separator"),
            ("__DoubleUnderscorePascal__", "double_underscore_pascal"),
            ("_leadingUnderscore", "leading_underscore"),
            ("trailingUnderscore_", "trailing_underscore"),
            ("word__WithDoubleUnderscores", "word_with_double_underscores"),
            ("hyphenated-word_with_underscore", "hyphenated_word_with_underscore"),
        ],
    )
    def test_leading_trailing_and_mixed_separators_conversion(
        self, input_str, expected_output
    ):
        """Test strings with leading/trailing/multiple separators."""
        assert to_snake_case(input_str) == expected_output

    @pytest.mark.parametrize(
        "input_str, expected_output",
        [
            ("SpecialHTTPRequest", "special_http_request"),
            ("anACRONYMNext", "an_acronym_next"),
            ("stringWITHAcronymI𝐧𝐬𝐢𝐝𝐞", "string_with_acronym_i𝐧𝐬𝐢𝐝𝐞"),
        ],
    )
    def test_mixed_patterns_conversion(self, input_str, expected_output):
        """Test complex mixed patterns."""
        assert to_snake_case(input_str) == expected_output

    @pytest.mark.parametrize(
        "input_str, expected_output",
        [
            ("", ""),
            ("a", "a"),
            (" ", ""),
        ],
    )
    def test_edge_cases_conversion(self, input_str, expected_output):
        """Test edge cases like empty strings or single characters."""
        assert to_snake_case(input_str) == expected_output

    @pytest.mark.parametrize(
        "input_str, expected_output",
        [
            ("idSite", "id_site"),
            ("userId", "user_id"),
            (
                "invalidVRMAuthTokenUsedInLogRequest",
                "invalid_vrm_auth_token_used_in_log_request",
            ),
            ("inverterChargerControl", "inverter_charger_control"),
            ("idAccessToken", "id_access_token"),
            ("Pc", "pc"),
            ("Gc", "gc"),
            ("users", "users"),
            ("accessLevel", "access_level"),
            ("receivesAlarmNotifications", "receives_alarm_notifications"),
            ("siteId", "site_id"),
        ],
    )
    def test_common_vrmapi_field_names(self, input_str, expected_output):
        """Test common field names used in VRM API responses."""
        assert to_snake_case(input_str) == expected_output


class TestSnakeCaseToCamelCase:

    @pytest.mark.parametrize(
        "input_str, expected_output",
        [
            ("", ""),
            ("word", "word"),
            ("WORD", "WORD"),
            ("AnotherWord", "AnotherWord"),
            ("alreadyCamel", "alreadyCamel"),
        ],
    )
    def test_empty_and_single_word_cases(self, input_str, expected_output):
        """Tests empty strings and single words (which should remain unchanged)."""
        assert snake_case_to_camel_case(input_str) == expected_output

    @pytest.mark.parametrize(
        "input_str, expected_output",
        [
            ("snake_case", "snakeCase"),
            ("a_simple_example", "aSimpleExample"),
            ("id_currency", "idCurrency"),
            ("user_profile_image_url", "userProfileImageUrl"),
            ("first_name", "firstName"),
            ("is_active", "isActive"),
            ("http_response_code", "httpResponseCode"),
            ("a_b_c_d", "aBCD"),
        ],
    )
    def test_standard_snake_case_conversion(self, input_str, expected_output):
        """Tests standard snake_case strings with multiple parts."""
        assert snake_case_to_camel_case(input_str) == expected_output

    @pytest.mark.parametrize(
        "input_str, expected_output",
        [
            ("field_1", "field1"),
            ("version_2_update", "version2Update"),
            ("item_name_v10", "itemNameV10"),
            ("section_007_agent", "section007Agent"),
            ("q1_report", "q1Report"),
        ],
    )
    def test_snake_case_with_numbers(self, input_str, expected_output):
        """Tests snake_case strings containing numbers."""
        assert snake_case_to_camel_case(input_str) == expected_output

    @pytest.mark.parametrize(
        "input_str, expected_output",
        [
            ("_leading_underscore", "LeadingUnderscore"),
            ("trailing_underscore_", "trailingUnderscore"),
            ("__double_leading", "DoubleLeading"),
            ("double__underscore", "doubleUnderscore"),
            ("a___b", "aB"),
            ("_", ""),
            ("__", ""),
            ("___", ""),
        ],
    )
    def test_edge_cases_with_underscores(self, input_str, expected_output):
        """
        Tests snake_case strings with leading, trailing, or multiple consecutive underscores.
        The output reflects the behavior of string.split('_') and string.title().
        Note: For Pydantic field names, these inputs are atypical.
        """
        assert snake_case_to_camel_case(input_str) == expected_output

    @pytest.mark.parametrize(
        "input_str, expected_output",
        [
            ("word", "word"),
            ("another_word", "anotherWord"),
            ("YetAnother_word_With_Capitals", "YetAnotherWordWithCapitals"),
        ],
    )
    def test_mixed_and_no_change_cases(self, input_str, expected_output):
        """Tests inputs that might have mixed casing or shouldn't change much."""
        assert snake_case_to_camel_case(input_str) == expected_output
