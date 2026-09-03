"""Reference values for dew_point(). Run with: python3 logger/test_dewpoint.py"""

from dewpoint import dew_point

TOLERANCE = 0.05

CASES = [
    # temp_c, humidity_pct, expected_td, note
    (20.0, 50.0, 9.26, "typical indoor"),
    (25.0, 60.0, 16.69, "warm and damp"),
    (30.0, 90.0, 28.18, "close to saturation"),
    (0.0, 100.0, 0.00, "saturated: Td must equal T exactly"),
    (15.0, 100.0, 15.00, "saturated again, different temperature"),
    (10.0, 30.0, -6.81, "cold and dry, Td goes negative"),
    (-5.0, 80.0, -7.92, "below freezing"),
]


def main() -> int:
    failures = 0
    print(f"{'T':>7} {'RH':>7} {'expected':>10} {'got':>10}   result")
    print("-" * 52)

    for temp_c, humidity_pct, expected, note in CASES:
        try:
            got = dew_point(temp_c, humidity_pct)
        except NotImplementedError:
            print("dew_point() is not written yet.")
            return 1
        except Exception as exc:
            print(f"{temp_c:>7} {humidity_pct:>7} {expected:>10} "
                  f"{'-':>10}   raised {type(exc).__name__}: {exc}")
            failures += 1
            continue

        ok = abs(got - expected) <= TOLERANCE
        failures += not ok
        print(f"{temp_c:>7} {humidity_pct:>7} {expected:>10.2f} "
              f"{got:>10.2f}   {'ok' if ok else 'FAIL'}   {note}")

    print("-" * 52)
    if failures:
        print(f"{failures} of {len(CASES)} failed")
        return 1
    print(f"all {len(CASES)} passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
