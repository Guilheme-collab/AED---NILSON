import numpy as np
import pytest
from scipy import signal

from nyquist_toolkit import (
    TransferFunction, benchmark_systems, bode_data, closed_loop_denominator,
    frequency_response, nyquist_analysis, pade_delay, root_locus, routh_table,
    routh_stability, stability_margins, with_pade,
)


@pytest.mark.parametrize("omega", [0.01, 0.1, 0.5, 1.0, 3.0, 10.0, 100.0, 1000.0])
def test_first_order_frequency_response_against_closed_form(omega):
    tf = TransferFunction([1.0], [0.5, 1.0])
    actual = frequency_response(tf, np.array([omega]))[0]
    expected = 1.0 / (1.0 + 0.5j * omega)
    assert actual == pytest.approx(expected, rel=1e-12, abs=1e-12)


@pytest.mark.parametrize("system", ["A", "B", "C"])
def test_frequency_response_matches_scipy(system):
    tf = benchmark_systems()[system]["tf"]
    omega = np.geomspace(1e-3, 1e3, 200)
    actual = frequency_response(tf, omega)
    _, expected = signal.freqresp((tf.numerator, tf.denominator), w=omega)
    assert np.max(np.abs(actual - expected)) < 1e-9


@pytest.mark.parametrize("coefficients", [
    [1, 2], [1, 3, 2], [1, 6, 11, 6], [1, 10, 35, 50, 24],
    [1, 15, 85, 225, 274, 120], [1, 21, 175, 735, 1624, 1764, 720],
])
def test_routh_stable_polynomials(coefficients):
    assert routh_stability(coefficients)
    assert routh_table(coefficients)["sign_changes"] == 0


@pytest.mark.parametrize("coefficients", [
    [1, -1], [1, 0, -1], [1, 1, -2], [1, -2, 1],
    [1, 0, 1, 1], [1, -1, -1, 1],
])
def test_routh_unstable_polynomials(coefficients):
    roots = np.roots(coefficients)
    expected = int(np.count_nonzero(np.real(roots) > 1e-7))
    assert expected > 0
    assert routh_table(coefficients)["sign_changes"] == expected


def test_routh_all_zero_row_case_is_reported():
    result = routh_table([1, 0, 2, 0, 1])
    assert result["special_all_zero_rows"]
    assert np.all(np.isfinite(result["table"]))


def test_routh_first_column_zero_case_is_reported():
    result = routh_table([1, 1, 2, 2, 1])
    assert result["special_first_column_zero_rows"]
    assert np.all(np.isfinite(result["table"]))


@pytest.mark.parametrize("order", [1, 2, 3, 4, 5, 6])
def test_pade_delay_is_real_and_approximates_exact_delay(order):
    tau = 0.35
    num, den = pade_delay(tau, order)
    w = 0.25
    approx = np.polyval(num, 1j * w) / np.polyval(den, 1j * w)
    exact = np.exp(-1j * w * tau)
    assert abs(approx - exact) < 0.02
    assert np.all(np.isfinite(num)) and np.all(np.isfinite(den))


@pytest.mark.parametrize("gain", [0.0, 0.5, 1.0, 5.0])
def test_root_locus_matches_direct_characteristic_roots(gain):
    num, den = [1.0], [1.0, 2.0, 1.0]
    _, branches = root_locus(num, den, [gain])
    expected = np.roots(closed_loop_denominator(TransferFunction(num, den), gain))
    assert np.allclose(np.sort_complex(branches[0]), np.sort_complex(expected), atol=1e-10)


@pytest.mark.parametrize("name", ["A", "B", "C", "D"])
def test_benchmarks_have_valid_nyquist_analysis(name):
    item = benchmark_systems()[name]
    result = nyquist_analysis(item["tf"], item["gain"], samples_axis=3001, samples_arc=401)
    assert result["closed_loop_rhp_poles_Z"] == 0
    assert result["encirclements_clockwise_N"] == -result["winding_ccw"]
    assert result["open_loop_rhp_poles_P"] >= 0


def test_benchmark_B_nyquist_accounts_for_open_loop_instability():
    result = nyquist_analysis(benchmark_systems()["B"]["tf"], 3.0, samples_axis=6001, samples_arc=801)
    assert result["open_loop_rhp_poles_P"] == 1
    assert result["encirclements_clockwise_N"] == -1
    assert result["closed_loop_rhp_poles_Z"] == 0


@pytest.mark.parametrize("order", [1, 2, 3, 4, 5])
def test_pade_model_keeps_expected_polynomial_degree(order):
    tf = TransferFunction([1.0], [0.5, 1.0], delay=0.35)
    rational = with_pade(tf, order)
    assert rational.delay == 0.0
    assert len(rational.numerator) == order + 1
    assert len(rational.denominator) == order + 2


def test_pi_rc_delay_margin_reproduces_theoretical_reference():
    tf = TransferFunction([1.4, 1.0], [0.47, 1.0, 0.0])
    margins = stability_margins(tf, np.geomspace(1e-5, 1e5, 120000))
    assert margins["gain_crossover_rad_s"] == pytest.approx(2.283434, rel=2e-4)
    assert margins["delay_margin_s"] == pytest.approx(0.883636, rel=2e-4)


def test_filtered_pid_rc_delay_margin_reproduces_theoretical_reference():
    # C(s)=1.4 + 1/s + 0.08*s/(0.05*s+1); G(s)=1/(0.47*s+1)
    tf = TransferFunction([0.15, 1.45, 1.0], [0.0235, 0.52, 1.0, 0.0])
    margins = stability_margins(tf, np.geomspace(1e-5, 1e5, 120000))
    assert margins["gain_crossover_rad_s"] == pytest.approx(2.221707, rel=2e-4)
    assert margins["delay_margin_s"] == pytest.approx(0.964813, rel=2e-4)


def test_frequency_response_applies_exact_delay():
    tf = TransferFunction([1.0], [1.0, 1.0], delay=0.7)
    w = np.array([0.5, 1.0, 3.0])
    actual = frequency_response(tf, w)
    expected = np.exp(-1j * w * 0.7) / (1.0 + 1j * w)
    assert np.allclose(actual, expected, rtol=1e-12, atol=1e-12)


def test_closed_loop_denominator_pads_numerator():
    tf = TransferFunction([1.0], [1.0, 2.0, 1.0])
    assert np.allclose(closed_loop_denominator(tf, 2.0), [1.0, 2.0, 3.0])


def test_nyquist_contour_indents_integrator_pole_on_imaginary_axis():
    tf = TransferFunction([1.0], [1.0, 0.0])
    result = nyquist_analysis(tf, samples_axis=3001, samples_arc=401)
    assert result["open_loop_imaginary_axis_poles"] == 1
    assert result["open_loop_rhp_poles_P"] == 0
    assert result["closed_loop_rhp_poles_Z"] == 0
    assert np.all(np.isfinite(result["mapped_curve"]))
    assert result["boundary_pole_treatment"].startswith("polos no eixo")


def test_nyquist_contour_indents_conjugate_imaginary_axis_poles():
    tf = TransferFunction([1.0], [1.0, 0.0, 1.0])
    result = nyquist_analysis(tf, samples_axis=3001, samples_arc=401)
    assert result["open_loop_imaginary_axis_poles"] == 2
    assert np.all(np.isfinite(result["mapped_curve"]))


def test_bode_returns_monotone_frequency_grid_and_finite_values():
    tf = benchmark_systems()["A"]["tf"]
    w = np.geomspace(1e-3, 1e3, 500)
    wf, mag, phase = bode_data(tf, w)
    assert np.all(np.diff(wf) > 0)
    assert np.all(np.isfinite(mag)) and np.all(np.isfinite(phase))


def test_routh_does_not_classify_imaginary_axis_roots_as_strictly_stable():
    result = routh_table([1.0, 0.0, 1.0])  # s^2 + 1
    assert result["imaginary_axis_pole_count"] == 2
    assert result["strictly_stable"] is False
    assert routh_stability([1.0, 0.0, 1.0]) is False


def test_routh_detects_integrator_as_imaginary_axis_pole():
    result = routh_table([1.0, 1.0, 0.0])  # s(s+1)
    assert result["imaginary_axis_pole_count"] == 1
    assert routh_stability([1.0, 1.0, 0.0]) is False


def test_exact_delay_cannot_be_silently_converted_to_polynomial_closed_loop():
    delayed = TransferFunction([1.0], [0.5, 1.0], delay=0.35)
    with pytest.raises(ValueError, match="Pad[eé]"):
        closed_loop_denominator(delayed, 2.0)
