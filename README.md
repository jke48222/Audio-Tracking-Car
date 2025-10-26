# Audio Tracking Car

A Raspberry Pi–powered car that **localizes sound** with a dual‑channel analog front end and **tracks toward the desired source**. The system reads level‑decoded ADC signals from two band‑pass filtered microphone chains, computes left/right dominance, and drives two DC motors via an H‑bridge. Modes are selected with a 4‑bit **DIP switch** (audio tracking vs. figure‑drawing demos).

---

## Features

- **Audio localization & tracking** (single‑source and multi‑source strategies)
- **Closed‑loop drive** with wheel RPM sensing (optical end‑stops)
- **Figure‑drawing demos** (straight, curves, figure‑8) for validation
- **Emergency bump switch** to halt motion
- Modular Python code (`gpiozero`) with clear hardware abstraction

---

## Hardware

- **Controller:** Raspberry Pi (GPIO via `gpiozero`)
- **Microphones:** 2× electret mic + analog chain (preamp → band‑pass → envelope/peak → level decode to GPIO)
- **Motor Driver:** H‑bridge (e.g., L293) or discrete MOSFET stage
- **Motors:** 2× DC gear motors, optical end‑stop disks for RPM
- **Switches:** 4‑bit DIP for mode select, bump switch for e‑stop
- **Power:** Isolated motor supply recommended

### GPIO Map (BCM)

| Function | Pin(s) | Notes |
|---|---|---|
| **Left Motor** | 27 (forward), 17 (back) | `gpiozero.Motor(27, 17)` |
| **Right Motor** | 15 (forward), 14 (back) | `gpiozero.Motor(15, 14)` |
| **Left Encoder** | 22 | `DigitalInputDevice(22)` |
| **Right Encoder** | 18 | `DigitalInputDevice(18)` |
| **Left ADC Levels** | 5, 11, 9, 10 | 4‑bit level from left audio chain |
| **Right ADC Levels** | 7, 8, 25, 23 | 4‑bit level from right audio chain |
| **Bump Switch** | 4 | Active‑HIGH with pull‑up |
| **DIP Switch** | 26 (MSB), 19, 13, 6 (LSB) | Mode select (see below) |

> Source: `Python/adc_logic.py`, `Python/rpm_motor_controller.py`, `Python/main.py`

---

## Modes (DIP Switch)

The 4 DIP inputs form a bit‑field used in `Python/main.py` to select behaviors:

- **Bit 3 (GPIO 26):** Stop/Run master enable  
- **Bit 2 (GPIO 19):** **Audio** tracking vs **Drawing** demos  
- **Bits 1–0 (GPIO 13, 6):** Sub‑mode selection (e.g., single vs multi‑source tracking; straight/curve/figure‑8)

> Flip the DIP switch while the program is running; changes are handled by callbacks that update the current behavior in real time.

---

## Software Layout

```
Audio-Tracking-Car/
├─ Python/
│  ├─ main.py                 # Mode control via DIP; ties modules together
│  ├─ audio_tracking.py       # Single & multi‑source tracking strategies
│  ├─ adc_logic.py            # GPIO readers for 4‑bit “ADC” levels + bump switch
│  ├─ rpm_motor_controller.py # Motor + encoder + RPM control helpers
│  └─ figure_drawing.py       # Straight, curves, figure‑8 demos
├─ CAD/                       # Car plate & switch holder models (STEP/SLDPRT)
├─ Wiring_Diagrams/           # ADC, Band‑Pass, H‑Bridge, UI schematics + PNGs
├─ Datasheets/                # Motors, L293, MOSFETs, optical end‑stop
└─ README.md                  # Project notes
```

---

## Setup

> Raspberry Pi OS (Bookworm/Bullseye), Python 3.9+

```bash
sudo apt update && sudo apt install -y python3 python3-pip
pip3 install gpiozero
```

If using GPIO as non‑root on newer Pi OS, enable interfaces:
```bash
sudo raspi-config  # Interfacing Options → enable as needed
```

---

## Run

From the repository root:
```bash
cd Python
python3 main.py
```

- Set the **DIP switch** to choose mode (see table above).  
- Use the **bump switch** (GPIO 4) as an emergency stop.  
- Ensure motor power is available and the H‑bridge is wired per `Wiring_Diagrams/H-Bridge.png`.

### Module Tests (manual)

```bash
python3 adc_logic.py            # Level decode sanity check
python3 rpm_motor_controller.py # Prints wheel RPM while motors spin
python3 audio_tracking.py       # Runs single-source demo by default
```

---

## Notes & Tips

- Balance microphone gains and ensure filters are **matched** across channels.  
- Use the **figure‑drawing** patterns to validate drivetrain before enabling audio tracking.  
- If wheel RPM is noisy, add debouncing or averaging in `rpm_motor_controller.py`.  
- Consider current limiting and flyback protection on the H‑bridge supply.