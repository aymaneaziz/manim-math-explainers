# Manim Setup Guide (Windows)

Everything you need installed and configured _before_ you render a single scene.
Written for PowerShell / VS Code on Windows

---

## 1. Install FFmpeg

Manim uses FFmpeg to stitch rendered frames into video.

**Easiest way (winget):**

```powershell
winget install ffmpeg
```

**Manual way:** download from https://www.gyan.dev/ffmpeg/builds/ (get the "essentials" build), extract it, and add its `bin` folder to your PATH (same process as step 4 below, just for FFmpeg's folder instead).

Verify:

```powershell
ffmpeg -version
```

---

## 2. Install Manim Community Edition

```powershell
pip install manim
```

This pulls in Manim's own dependencies (numpy, Pillow, Pycairo, etc.) automatically. If `pycairo` fails to build on Windows, install the prebuilt wheel instead:

```powershell
pip install pycairo --only-binary :all:
pip install manim
```

Verify:

```powershell
manim --version
```

---

## 3. Install MiKTeX (LaTeX — required for `MathTex`/`Tex`)

Plain `Text()` works without this. The moment you use `MathTex()` or `Tex()` for real math typesetting, you need a LaTeX distribution.

1. Download the installer from https://miktex.org/download
2. Run it, choosing **"Install missing packages on-the-fly: Yes"** when asked (this avoids most future errors)
3. Finish the install
   s

### 4a. Make sure MiKTeX is on your PATH

Open a **new** PowerShell window and check:

```powershell
where.exe latex
```

If that returns nothing, MiKTeX's `bin` folder isn't on PATH yet. Find it (usually one of these):

```
C:\Users\<you>\AppData\Local\Programs\MiKTeX\miktex\bin\x64\
C:\Program Files\MiKTeX\miktex\bin\x64\
```

Add it:

```powershell
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Users\<you>\AppData\Local\Programs\MiKTeX\miktex\bin\x64\", "User")
```

**Close every open terminal and VS Code window completely, then reopen.** PATH changes never apply to terminals that were already open — this is the #1 cause of "it says it's installed but nothing works."

Verify:

```powershell
latex --version
```

### 4b. Turn on auto-install for missing LaTeX packages

You'll hit `File 'xyz.sty' not found` errors the first time you use certain LaTeX features (this is normal — MiKTeX installs packages lazily, only when needed).

1. Open **MiKTeX Console** (search it in the Start Menu)
2. Go to **Settings**
3. Set **"Install missing packages on-the-fly"** to **Always**
4. While you're in there: go to **Updates** → **Check for updates** → **Update now** (an outdated MiKTeX install causes a lot of avoidable missing-package errors)

If you ever hit a stubborn missing package, install it directly:

```powershell
mpm --install=<package-name>
```

or use MiKTeX Console → Packages → search → Install.

Two packages worth pre-installing now since Manim's default templates lean on them:

```powershell
mpm --install=preview
mpm --install=cm-super
mpm --install=type1cm
```

---

## 5. Sanity-check the full pipeline

Create a test file `test_scene.py`:

```python
from manim import *

class Test(Scene):
    def construct(self):
        formula = MathTex(r"e^{i\pi} + 1 = 0", font_size=72)
        self.play(Write(formula))
        self.wait(1)
```

Run it:

```powershell
manim -pql test_scene.py Test
```

If a preview window pops up showing the equation being written, **you're fully set up.**

---

## 6. Project folder structure (recommended)

```
Code/
├── my_scene.py          ← your scene script
└── media/                ← auto-created by manim
    ├── videos/           ← rendered output
    ├── images/
    └── Tex/               ← cached LaTeX renders
```

You don't need to create `media/` yourself — manim makes it on first render.

---

## 7. Rendering — quality flags cheat sheet

```powershell
manim -pql  math_scene.py MathExplanation   # low quality, fast — use while iterating
manim -pqm  math_scene.py MathExplanation   # medium quality
manim -pqh  math_scene.py MathExplanation   # 1080p60 (Full HD) — good final render
manim -pqk  math_scene.py MathExplanation   # 4K — slow, final export only
```

Flags: `-p` = preview (auto-opens the video when done), `-q` = quality, `l/m/h/k` = low/medium/high/4K.

---
