# Analog Data to Analog Signals

**Group Name:** JEOLEE

**Course:** Data and Digital Communications

**Subject Code:** CPE331

**Section:** H2

## Group Members

- John Norbert Tamares
- Evonie Batiller
- Richelle Mae Deniega
- Edrianne Babatuan
- Dashiell Reed Dinoy

This Python application demonstrates analog modulation techniques: **Amplitude Modulation (AM)**, **Phase Modulation (PM)**, and **Frequency Modulation (FM)**.

It is based on the encoding concepts in Section 5.4 of Stallings, *Data and Computer Communications*, 8th Edition.

## Features

- Displays the message, carrier, AM, PM, and FM signals in the time domain
- Shows the frequency spectrum of each modulated signal
- Supports sine, square, and triangle message waveforms
- Allows live changes to message frequency, carrier frequency, AM index, PM index, and FM index
- Displays modulation bandwidth estimates and modulation parameters

## Requirements

- Python 3
- NumPy
- Matplotlib

## Installation

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install numpy matplotlib
```

## Run the Demo

```powershell
python d.py
```

Two windows will open: one for the signals and one for their spectra.

## Controls

1. Select a message shape.
2. Enter a message frequency and carrier frequency in the text boxes.
3. Press **Enter** to apply the frequencies.
4. Adjust the AM, PM, or FM sliders to see the modulation change live.
5. Close both plot windows to exit.

The carrier frequency must be greater than the message frequency. The message frequency must be at least 1 Hz, and the carrier frequency must not exceed 20,000 Hz.

## Demonstrated Formulas

For message signal `m(t)` and carrier frequency `fc`:

- **AM:** `s(t) = [1 + na * m(t)] * cos(2 * pi * fc * t)`
- **PM:** `s(t) = cos(2 * pi * fc * t + np * m(t))`
- **FM:** `s(t) = cos(2 * pi * fc * t + integral(nf * m(t)))`
