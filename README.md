# Multilingual Love Heart ❤️

A generative typographic art experiment in Python that renders a heart silhouette composed of "I love you" in 20 different languages, with a name written in the middle as a dedication. Smooth floating animation and a subtle shimmering effect.

<img width="1302" height="752" alt="Multilingual Love Heart" src="https://github.com/user-attachments/assets/6c2ccffe-f46d-4b2f-9430-36a6a5739beb" />

## Features
- **Parametric Heart Boundary:** Uses a parametric heart curve to calculate exact scanline boundaries and text placement.
- **Multilingual Typography:** Cycles through love phrases in 20 languages with proportional font scaling.
- **Dedication:** A name is written in the center of the heart (default: **Havya**). The phrases are laid out around it, and it fades in with a glow once the heart is complete.
- **Smooth Animation:** Eased vertical float-in transitions (`cubic ease-out`) with color grading from deep crimson to glowing edges.
- **Post-Render Shimmer:** Continuous ambient glimmers on random phrases once drawing completes.
- **Zero External Dependencies:** Built entirely with Python's standard library (`turtle`, `tkinter`, `math`, `random`).

## How to Run

```bash
python love.py            # dedicates the heart to "Havya"
python love.py "Maria"    # dedicates it to any other name
```

> Requires Python 3 with Tk (`tkinter`). On Debian/Ubuntu: `sudo apt install python3-tk`.

## Customize
All the settings are constants at the top of `love.py`:

| Constant | What it does |
|---|---|
| `NAME` | Dedication name (also set via command line) |
| `DURATION` | Seconds to draw the whole heart |
| `SIZES` | Font sizes used for the phrases |
| `BG` | Background color |
| `PHRASES` | The list of languages |

## Notes
- The font is picked automatically (Arial, Segoe UI, Helvetica, Noto Sans or DejaVu Sans, in that order). Scripts such as Thai, Hindi, Korean and Japanese depend on the fonts installed on your system.
- This is a desktop app (`turtle`/`tkinter`). It does not run in a browser.
