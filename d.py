"""
Encoding Techniques - Section 5.4: Analog Data, Analog Signals
Reference: Stallings, Data and Computer Communications, 8th Edition

AM (5.12): s(t) = [1 + na * x(t)] * cos(2*pi*fc*t)
Angle (5.13): s(t) = Ac * cos[2*pi*fc*t + phi(t)]
PM (5.14): phi(t) = np * m(t)
FM (5.15): phi'(t) = nf * m(t)
FM peak deviation: dF = nf * Am / (2*pi)
Carson's rule: BT = 2(beta + 1)B, with beta = np*Am (PM), dF/B (FM)
AM bandwidth: BT = 2B

Language: Python 3
Libraries: numpy, matplotlib

Live demo: type the message and carrier frequency in the boxes at the
bottom of the graph window, press Enter, and the graphs update directly.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons, Slider, TextBox

DEFAULT_SHAPE = "sine"
DEFAULT_MESSAGE_FREQ = 100
DEFAULT_CARRIER_FREQ = 1000
DEFAULT_AM_INDEX = 0.8
DEFAULT_PM_INDEX = 2.0
DEFAULT_FM_RATIO = 0.3
MIN_MESSAGE_FREQ = 1
MAX_CARRIER_FREQ = 20000
SHAPES = ["Sine", "Square", "Triangle"]


def message_signal(t, freq, shape):
    wave = np.sin(2 * np.pi * freq * t)
    if shape == "square":
        return np.sign(wave)
    if shape == "triangle":
        return (2 / np.pi) * np.arcsin(wave)
    return wave


def carrier_signal(t, fc):
    return np.cos(2 * np.pi * fc * t)


def amplitude_modulation(m, t, fc, na):
    return (1 + na * m) * carrier_signal(t, fc)


def phase_modulation(m, t, fc, n_p):
    return np.cos(2 * np.pi * fc * t + n_p * m)


def frequency_modulation(m, t, fc, n_f, fs):
    phase = n_f * np.cumsum(m) / fs
    return np.cos(2 * np.pi * fc * t + phase)


def spectrum(signal, window, fs):
    magnitude = np.abs(np.fft.rfft(signal * window)) / (window.sum() / 2)
    frequencies = np.fft.rfftfreq(len(signal), 1 / fs)
    return frequencies, magnitude


def bandwidth_summary(m_peak, band, na, n_p, n_f):
    delta_f = n_f * m_peak / (2 * np.pi)
    beta_pm = n_p * m_peak
    beta_fm = delta_f / band
    power_ratio = 1 + na ** 2 / 2

    am_text = f"AM: BT = 2B = {2 * band:g} Hz | Pt/Pc = {power_ratio:.2f}"
    pm_text = (f"PM: beta = {beta_pm:.2f} | "
               f"BT = 2(beta+1)B = {2 * (beta_pm + 1) * band:g} Hz")
    fm_text = (f"FM: dF = {delta_f:.0f} Hz | beta = {beta_fm:.2f} | "
               f"BT = 2dF + 2B = {2 * delta_f + 2 * band:g} Hz")
    return f"{am_text}\n{pm_text}\n{fm_text}"


def build_signals(shape, message_freq, carrier_freq):
    fs = 20 * carrier_freq
    t = np.arange(0, 5 / message_freq, 1 / fs)
    m = message_signal(t, message_freq, shape)
    return {
        "t": t,
        "time_ms": t * 1000,
        "m": m,
        "fs": fs,
        "window": np.hanning(len(t)),
        "m_peak": np.max(np.abs(m)),
    }


def parse_positive(text):
    try:
        value = float(text)
    except ValueError:
        return None
    return value if value > 0 else None


def validate_frequencies(message_freq, carrier_freq):
    if message_freq < MIN_MESSAGE_FREQ:
        return f"Message frequency must be at least {MIN_MESSAGE_FREQ} Hz."
    if carrier_freq > MAX_CARRIER_FREQ:
        return f"Carrier frequency must be at most {MAX_CARRIER_FREQ} Hz."
    if carrier_freq <= message_freq:
        return "Carrier must be higher than the message."
    return None


def set_text_quietly(box, text):
    box.eventson = False
    box.set_val(text)
    box.eventson = True


def create_signal_figure():
    fig, axes = plt.subplots(5, 1, figsize=(11, 9), sharex=True)
    title = fig.suptitle("", fontsize=13, fontweight="bold", y=0.99)
    fig.subplots_adjust(left=0.08, right=0.97, top=0.85, bottom=0.19, hspace=0.6)

    for ax in axes:
        ax.set_ylim(-2.3, 2.3)
        ax.set_ylabel("Amplitude")
        ax.grid(alpha=0.3)
    axes[-1].set_xlabel("Time (ms)")

    return fig, axes, title


def create_spectrum_figure():
    fig, axes = plt.subplots(3, 1, figsize=(9, 7), sharex=True)
    fig.suptitle("Spectrum of the Modulated Signals", fontsize=13, fontweight="bold")
    fig.subplots_adjust(left=0.09, right=0.97, top=0.88, bottom=0.09, hspace=0.45)

    for ax in axes:
        ax.set_ylim(0, 1.3)
        ax.set_ylabel("Magnitude")
        ax.grid(alpha=0.3)
    axes[-1].set_xlabel("Frequency (Hz)")

    return fig, axes


def create_slider(fig, position, label, low, high, start):
    ax = fig.add_axes(position)
    return Slider(ax, label, low, high, valinit=start)


def create_text_box(fig, position, label, initial):
    ax = fig.add_axes(position)
    return TextBox(ax, label, initial=str(initial))


def create_app():
    fig, axes, title = create_signal_figure()
    ax_msg, ax_car, ax_am, ax_pm, ax_fm = axes
    info = fig.text(0.08, 0.875, "", fontsize=9, family="monospace", va="bottom")
    status = fig.text(0.97, 0.875, "", fontsize=10, color="red", ha="right", va="bottom")

    spec_fig, spec_axes = create_spectrum_figure()
    spec_am, spec_pm, spec_fm = spec_axes

    (line_msg,) = ax_msg.plot([], [], color="tab:blue")
    ax_msg.set_title("Message signal m(t)  (input signal)")

    (line_car,) = ax_car.plot([], [], color="tab:gray")
    ax_car.set_title("Carrier signal")

    (line_am,) = ax_am.plot([], [], color="tab:red")
    (env_top,) = ax_am.plot([], [], "k--", linewidth=0.8)
    (env_bottom,) = ax_am.plot([], [], "k--", linewidth=0.8)
    ax_am.set_title("Amplitude Modulation (AM)")

    (line_pm,) = ax_pm.plot([], [], color="tab:green")
    ax_pm.set_title("Phase Modulation (PM)")

    (line_fm,) = ax_fm.plot([], [], color="tab:purple")
    ax_fm.set_title("Frequency Modulation (FM)")

    (spec_line_am,) = spec_am.plot([], [], color="tab:red")
    (spec_line_pm,) = spec_pm.plot([], [], color="tab:green")
    (spec_line_fm,) = spec_fm.plot([], [], color="tab:purple")
    spec_am.set_title("AM: carrier + upper and lower sidebands")
    spec_pm.set_title("PM")
    spec_fm.set_title("FM")

    nf_start = 2 * np.pi * DEFAULT_CARRIER_FREQ * DEFAULT_FM_RATIO
    slider_na = create_slider(
        fig, [0.20, 0.09, 0.28, 0.02], "AM index (na)", 0.0, 1.5, DEFAULT_AM_INDEX
    )
    slider_np = create_slider(
        fig, [0.20, 0.055, 0.28, 0.02], "PM index (np)", 0.0, 5.0, DEFAULT_PM_INDEX
    )
    slider_nf = create_slider(
        fig, [0.20, 0.02, 0.28, 0.02], "FM index (nf, rad/s)",
        0, 2 * np.pi * DEFAULT_CARRIER_FREQ, nf_start,
    )

    box_message = create_text_box(
        fig, [0.74, 0.085, 0.09, 0.03], "Message freq (Hz)  ", DEFAULT_MESSAGE_FREQ
    )
    box_carrier = create_text_box(
        fig, [0.74, 0.040, 0.09, 0.03], "Carrier freq (Hz)  ", DEFAULT_CARRIER_FREQ
    )

    ax_radio = fig.add_axes([0.86, 0.015, 0.12, 0.115])
    ax_radio.set_title("Message shape", fontsize=9)
    radio = RadioButtons(ax_radio, SHAPES, active=0)
    for label in radio.labels:
        label.set_fontsize(9)

    state = {"shape": None, "message_freq": None, "carrier_freq": None, "signals": None}

    def refresh(_=None):
        signals = state["signals"]
        if signals is None:
            return

        t, m = signals["t"], signals["m"]
        time_ms, fs, window = signals["time_ms"], signals["fs"], signals["window"]
        fc, fm = state["carrier_freq"], state["message_freq"]
        na, n_p, n_f = slider_na.val, slider_np.val, slider_nf.val

        s_am = amplitude_modulation(m, t, fc, na)
        s_pm = phase_modulation(m, t, fc, n_p)
        s_fm = frequency_modulation(m, t, fc, n_f, fs)

        line_msg.set_data(time_ms, m)
        line_car.set_data(time_ms, carrier_signal(t, fc))
        line_am.set_data(time_ms, s_am)
        env_top.set_data(time_ms, 1 + na * m)
        env_bottom.set_data(time_ms, -(1 + na * m))
        line_pm.set_data(time_ms, s_pm)
        line_fm.set_data(time_ms, s_fm)

        spec_lines = (spec_line_am, spec_line_pm, spec_line_fm)
        for line, signal in zip(spec_lines, (s_am, s_pm, s_fm)):
            line.set_data(*spectrum(signal, window, fs))

        info.set_text(bandwidth_summary(signals["m_peak"], fm, na, n_p, n_f))
        fig.canvas.draw_idle()
        spec_fig.canvas.draw_idle()

    def apply_settings(shape, message_freq, carrier_freq):
        error = validate_frequencies(message_freq, carrier_freq)
        status.set_text(error or "")
        if error:
            fig.canvas.draw_idle()
            return error

        carrier_changed = carrier_freq != state["carrier_freq"]
        state.update(shape=shape, message_freq=message_freq, carrier_freq=carrier_freq)
        state["signals"] = build_signals(shape, message_freq, carrier_freq)
        time_ms = state["signals"]["time_ms"]

        title.set_text(
            f"Analog Data -> Analog Signals   "
            f"(message: {shape}, {message_freq:g} Hz | carrier: {carrier_freq:g} Hz)"
        )
        ax_msg.set_xlim(0, time_ms[-1])
        spec_am.set_xlim(max(0, carrier_freq - 8 * message_freq),
                         carrier_freq + 8 * message_freq)

        nf_max = 2 * np.pi * carrier_freq
        slider_nf.valmax = nf_max
        slider_nf.ax.set_xlim(0, nf_max)
        if carrier_changed:
            slider_nf.eventson = False
            slider_nf.set_val(nf_max * DEFAULT_FM_RATIO)
            slider_nf.eventson = True

        refresh()
        return None

    def change_frequency(key, text):
        value = parse_positive(text)
        settings = {
            "shape": state["shape"],
            "message_freq": state["message_freq"],
            "carrier_freq": state["carrier_freq"],
        }
        if value is None:
            status.set_text("Enter a positive number.")
            error = "invalid"
        else:
            settings[key] = value
            error = apply_settings(**settings)

        if error:
            box = box_message if key == "message_freq" else box_carrier
            set_text_quietly(box, f"{state[key]:g}")
            fig.canvas.draw_idle()

    def change_shape(label):
        apply_settings(label.lower(), state["message_freq"], state["carrier_freq"])

    box_message.on_submit(lambda text: change_frequency("message_freq", text))
    box_carrier.on_submit(lambda text: change_frequency("carrier_freq", text))
    radio.on_clicked(change_shape)
    for slider in (slider_na, slider_np, slider_nf):
        slider.on_changed(refresh)

    apply_settings(DEFAULT_SHAPE, DEFAULT_MESSAGE_FREQ, DEFAULT_CARRIER_FREQ)

    return {
        "fig": fig,
        "spec_fig": spec_fig,
        "state": state,
        "status": status,
        "box_message": box_message,
        "box_carrier": box_carrier,
        "radio": radio,
        "sliders": (slider_na, slider_np, slider_nf),
    }


def main():
    app = create_app()

    print("ANALOG DATA, ANALOG SIGNALS - MODULATION DEMO")
    print("Type the message and carrier frequency in the boxes at the")
    print("bottom of the graph window, then press Enter.")
    print("Two windows opened: the signals and the spectrum.")
    print("Close both windows to exit.")

    plt.show()
    return app


if __name__ == "__main__":
    main()
    