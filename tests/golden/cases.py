"""Golden-master case matrix.

Each case carries the legacy-shaped inputs: the profile dict exactly as the
GUI's create-program screen writes it, plus the run-screen parameters. The
recorder feeds these to the frozen legacy code; the parity tests feed the
same inputs to ``sheetcut.core``.

Pattern types: 1 side-limb yoke, 3 spear-horizontal, 4 symmetric fish,
5 asymmetric fish. (2, split yoke, was broken in the prototype.)
"""


def _tool(name, steplap_type=0, steplap_count=1, open_code=0, is_skewed=False):
    return {
        "name": name,
        "steplap_type": steplap_type,
        "steplap_count": steplap_count,
        "open_code": open_code,
        "is_skewed": is_skewed,
        "_steplap_distance": 0,
    }


def _profile(*tools):
    return {str(i): t for i, t in enumerate(tools)}


def _sly_profile(count, end_open=1, v_open=1, v_type=2):
    """The canonical 5-tool side-limb yoke: f+45, hole, v-notch, hole, f-45."""
    return _profile(
        _tool("fp45", steplap_type=1, steplap_count=count, open_code=end_open),
        _tool("h"),
        _tool("v", steplap_type=v_type, steplap_count=count, open_code=v_open),
        _tool("h"),
        _tool("fm45", steplap_type=1, steplap_count=count, open_code=2),
    )


def _case(case_id, ptype, profile, l_list, d_list, layers=1, s_no=1, scrap=0.0):
    return {
        "id": case_id,
        "ptype": ptype,
        "profile": profile,
        "l_list": [float(v) for v in l_list],
        "d_list": [float(v) for v in d_list],
        "layers": layers,
        "s_no": s_no,
        "scrap_length": scrap,
    }


CASES = [
    # --- pattern type 1: side-limb yoke (legacy step_lap_v4.ToolList) ---
    _case(
        "sly_c5_open_l1",
        1,
        _sly_profile(5),
        [985.5, 1200.25, 1200.25, 985.5],
        [2.0, 1.5, 2.0],
    ),
    _case(
        "sly_c5_open_l2_s3",
        1,
        _sly_profile(5),
        [985.5, 1200.25, 1200.25, 985.5],
        [2.0, 1.5, 2.0],
        layers=2,
        s_no=3,
    ),
    _case(
        "sly_c3_closed_l1",
        1,
        _sly_profile(3, end_open=2, v_open=2),
        [800.0, 1000.5, 1000.5, 800.0],
        [3.5, 2.5, 3.5],
    ),
    _case(
        "sly_c4_even_l1",
        1,
        _sly_profile(4),
        [900.0, 1100.0, 1100.0, 900.0],
        [2.0, 2.0, 2.0],
    ),
    _case(
        "sly_c7_l3_s7",
        1,
        _sly_profile(7),
        [750.5, 950.0, 950.0, 750.5],
        [1.5, 1.5, 1.5],
        layers=3,
        s_no=7,
    ),
    _case(
        "sly_neo8_f0mid",
        1,
        _profile(
            _tool("fp45", steplap_type=1, steplap_count=5, open_code=1),
            _tool("h"),
            _tool("v", steplap_type=2, steplap_count=5, open_code=1),
            _tool("h"),
            _tool("f0", steplap_type=1, steplap_count=5, open_code=4),
            _tool("h"),
            _tool("v", steplap_type=2, steplap_count=5, open_code=2),
            _tool("fm45", steplap_type=1, steplap_count=5, open_code=2),
        ),
        [500.0] * 7,
        [5.0, 5.0, 5.0, 5.0, 5.0],
        layers=2,
    ),
    _case(
        "sly_no_steplap",
        1,
        _profile(
            _tool("fp45"),
            _tool("h"),
            _tool("v"),
            _tool("h"),
            _tool("fm45"),
        ),
        [600.0, 850.0, 850.0, 600.0],
        [],
    ),
    _case(
        "sly_hole_steplap",
        1,
        _profile(
            _tool("fp45", steplap_type=1, steplap_count=3, open_code=1),
            _tool("h", steplap_type=1, steplap_count=3, open_code=1),
            _tool("v", steplap_type=2, steplap_count=3, open_code=1),
            _tool("h"),
            _tool("fm45", steplap_type=1, steplap_count=3, open_code=2),
        ),
        [700.0, 900.5, 900.5, 700.0],
        [2.0, 1.0, 1.5, 2.0],
    ),
    _case(
        "sly_mid_rear_open",
        1,
        _profile(
            _tool("fp45", steplap_type=1, steplap_count=5, open_code=1),
            _tool("h"),
            _tool("fp45", steplap_type=1, steplap_count=5, open_code=9),
            _tool("h"),
            _tool("fm45", steplap_type=1, steplap_count=5, open_code=2),
        ),
        [650.0, 720.5, 720.5, 650.0],
        [2.0, 1.5, 2.0],
    ),
    # --- pattern type 3: spear horizontal (legacy SpearH) ---
    _case(
        "sph_c3_open",
        3,
        _profile(
            _tool("s", steplap_type=1, steplap_count=3, open_code=1),
            _tool("h"),
            _tool("f0"),
        ),
        [400.5, 350.25],
        [2.0],
        scrap=5.0,
    ),
    _case(
        "sph_c5_closed_noholes",
        3,
        _profile(
            _tool("s", steplap_type=1, steplap_count=5, open_code=2),
            _tool("h"),
        ),
        [500.0],
        [2.5],
        scrap=6.0,
    ),
    _case(
        "sph_c5_closed_layers2",
        3,
        _profile(
            _tool("s", steplap_type=1, steplap_count=5, open_code=2),
            _tool("h"),
        ),
        [500.0],
        [2.5],
        layers=2,
        scrap=6.0,
    ),
    _case(
        "sph_c4_even",
        3,
        _profile(
            _tool("s", steplap_type=1, steplap_count=4, open_code=1),
            _tool("h"),
            _tool("f0"),
        ),
        [300.0, 300.0],
        [1.5],
        scrap=3.5,
    ),
    _case(
        "sph_c5_3seg",
        3,
        _profile(
            _tool("s", steplap_type=1, steplap_count=5, open_code=1),
            _tool("h"),
            _tool("h"),
            _tool("f0"),
        ),
        [250.5, 300.0, 250.5],
        [2.0],
        scrap=4.0,
    ),
    _case(
        "sph_scrap_zero",
        3,
        _profile(
            _tool("s", steplap_type=1, steplap_count=3, open_code=1),
            _tool("h"),
        ),
        [450.0],
        [2.0],
        scrap=0.0,
    ),
    # --- pattern type 4: symmetric fish (legacy SpearV) ---
    _case(
        "fish4_c5_hole",
        4,
        _profile(
            _tool("s", steplap_type=2, steplap_count=5, open_code=1),
            _tool("h"),
            _tool("v"),
        ),
        [300.0, 300.0],
        [2.0],
    ),
    _case(
        "fish4_c5_hole_layers2",
        4,
        _profile(
            _tool("s", steplap_type=2, steplap_count=5, open_code=1),
            _tool("h"),
            _tool("v"),
        ),
        [300.0, 300.0],
        [2.0],
        layers=2,
    ),
    _case(
        "fish4_c4_even_nohole",
        4,
        _profile(
            _tool("s", steplap_type=2, steplap_count=4, open_code=1),
            _tool("v"),
        ),
        [600.0],
        [1.5],
    ),
    _case(
        "fish4_c3_single",
        4,
        _profile(
            _tool("s", steplap_type=2, steplap_count=3, open_code=1),
            _tool("v"),
        ),
        [450.75],
        [2.5],
    ),
    # --- pattern type 5: asymmetric / skewed fish (legacy SpearV) ---
    _case(
        "fish5_c4_skewflag",
        5,
        _profile(
            _tool("s", steplap_type=2, steplap_count=4, open_code=1, is_skewed=True),
            _tool("h"),
            _tool("v"),
        ),
        [300.0, 300.0],
        [2.0],
    ),
    _case(
        "fish5_c3_type3_layers2",
        5,
        _profile(
            _tool("s", steplap_type=3, steplap_count=3, open_code=1),
            _tool("h"),
            _tool("h"),
            _tool("v"),
        ),
        [250.0, 250.0, 250.0],
        [1.5],
        layers=2,
    ),
]
