from module_utils.aci_diff import ACIDiff
import json
import pytest

params = {
    "mode": "only_changed",
    "current_inventory": "./tests/unit/modules/files/current",
    "previous_inventory": "./tests/unit/modules/files/previous",
}


def test_validate_successful():
    try:
        ACIDiff(params)
    except Exception as e:
        pytest.fail("Unexpected Error: {}".format(e))


def test_get_states_only_changed():
    try:
        diff_aci = ACIDiff(params)
        diff_aci.load_configurations()

        states = diff_aci.get_states()
        assert 0 == len(states)

    except Exception as e:
        pytest.fail("Unexpected Error: {}".format(e))


def test_get_states_all():
    try:
        p = params.copy()
        p["mode"] = "all"
        diff_aci = ACIDiff(p)
        diff_aci.load_configurations()

        states = diff_aci.get_states()
        assert 0 == len(states)

    except Exception as e:
        pytest.fail("Unexpected Error: {}".format(e))


def test_get_states_only_provided():
    with open("./tests/unit/modules/files/cx-auto-blue-1-expected-result.json") as jf:
        try:
            expected_result = json.load(jf)
            p = params.copy()
            p["mode"] = "only_provided"
            diff_aci = ACIDiff(p)
            diff_aci.load_configurations()

            states = diff_aci.get_states()
            assert len(expected_result) == len(states)
            assert json.dumps(expected_result, sort_keys=True) == json.dumps(
                states, sort_keys=True
            )
        except Exception as e:
            pytest.fail("Unexpected Error: {}".format(e))


def test_validate_no_previous_inventory():
    p = params.copy()
    p["previous_inventory"] = ""
    with pytest.raises(Exception) as excinfo:
        ACIDiff(p)
        assert (
            "Previous inventory (previous_inventory) required when using mode 'only_changed'."
            == str(excinfo.value)
        )


def test_validate_previous_not_a_dir():
    p = params.copy()
    p["previous_inventory"] = "/this/path/does/not/exist"
    with pytest.raises(Exception) as excinfo:
        ACIDiff(p)
        assert (
            "The provided directory (previous_inventory) '/this/path/does/not/exist' does not appear to exist.Is it a directory?"
            == str(excinfo.value)
        )


def test_validate_no_current_inventory():
    p = params.copy()
    p["current_inventory"] = ""
    with pytest.raises(Exception) as excinfo:
        ACIDiff(p)
        assert "Current inventory (current_inventory) is a required parameter." == str(
            excinfo.value
        )


def test_validate_current_not_a_dir():
    p = params.copy()
    p["current_inventory"] = "/this/path/does/not/exist"
    with pytest.raises(Exception) as excinfo:
        ACIDiff(p)
        assert (
            "The provided directory (current_inventory) '/this/path/does/not/exist' does not appear to exist.Is it a directory?"
            == str(excinfo.value)
        )
