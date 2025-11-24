# UxPlay Streamlit Controller

This is a simple Streamlit-based UI to start and stop multiple UxPlay instances on macOS.
It is designed for demos where you want to mirror an iPad and an iPhone to your Mac at the same time,
then share them in Zoom/Teams.

## What this does

- Provides a small web UI (running locally via Streamlit) to:
  - Start a UxPlay instance for an iPad (with its own AirPlay name and port).
  - Start a UxPlay instance for an iPhone (with its own AirPlay name and port).
  - Stop each instance individually.
  - Stop all instances at once.
- Each instance runs `uxplay` as a separate background process on your Mac.

> Important: This project **does not install UxPlay for you**.
> You must install and test `uxplay` on your Mac separately first.

---

## Prerequisites

1. **macOS** with:
   - Xcode command line tools installed.
   - UxPlay installed and available on your PATH (or note its full path).

2. **Python 3.9+** (recommended 3.10+).

3. **Pip** to install Python dependencies.

4. **Streamlit** and other Python deps (from `requirements.txt`).

5. **Same network**:
   - Your Mac, iPad, and iPhone must be on the **same Wi-Fi/network** for AirPlay.

---

## Quickstart

1. **Clone or unzip this project**

If you’re reading this from a zip, just extract it somewhere, e.g.:

```bash
cd /path/to/uxplay_streamlit
```

2. **Create and activate a virtual environment (optional but recommended)**

```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS / Linux
# On Windows (if you ever use it): .venv\Scripts\activate
```

3. **Install Python dependencies**

```bash
pip install -r requirements.txt
```

4. **Verify `uxplay` works on your Mac**

Open a normal Terminal and run:

```bash
uxplay -vsync no
```

On your iPad or iPhone, open **Control Center → Screen Mirroring** and verify you see
an entry like `uxplay@your-mac`. If mirroring appears in a window on your Mac, UxPlay is working.

Stop it (Ctrl+C in the Terminal) before using the Streamlit UI.

5. **Run the Streamlit UI**

From the project folder:

```bash
streamlit run streamlit_app.py
```

This will start a local web server and open a browser window with the UI.
If the browser doesn’t open automatically, navigate to:

- http://localhost:8501

6. **Use in PyCharm**

- Open **PyCharm**.
- Use **File → Open...** and select the `uxplay_streamlit` folder.
- Set up a Run Configuration:
  - Script path: the path to your `streamlit` executable in your venv (or use `python -m streamlit`).
  - Parameters: `run streamlit_app.py`
  - Working directory: this project folder.
- Run that configuration; PyCharm’s run console will show Streamlit logs.

---

## Using the UI

### 1. Configure UxPlay path (if needed)

At the top of the UI you’ll see an input for:

- **UxPlay binary path**

If `uxplay` is on your PATH, leave it as `uxplay`.  
Otherwise, put the **full path**, for example:

```text
/usr/local/bin/uxplay
```

### 2. Start the iPad instance

- Set:
  - **AirPlay name** (e.g. `iPadMirror`)
  - **Base port** (e.g. `7000`)
- Click **Start iPad instance**.
- On the iPad:
  - Control Center → Screen Mirroring → choose `iPadMirror`.

A new UxPlay window should appear on your Mac.

### 3. Start the iPhone instance

- Set:
  - **AirPlay name** (e.g. `iPhoneMirror`)
  - **Base port** (e.g. `7100`)
- Click **Start iPhone instance**.
- On the iPhone:
  - Control Center → Screen Mirroring → choose `iPhoneMirror`.

You’ll now have **two UxPlay windows** (one for iPad, one for iPhone)
which you can arrange side by side and share in Zoom/Teams.

### 4. Stopping instances

- Use the **Stop iPad instance** or **Stop iPhone instance** button
  to terminate each instance gracefully.
- Use **Stop ALL instances** to kill everything this UI started.

---

## Notes / Limitations

- This UI doesn’t give you control over what appears on the iOS screens.
  It only starts/stops the mirroring receivers.
- It assumes:
  - UxPlay’s CLI flags:
    - `-n` for AirPlay name.
    - `-p` for base port (uses `p, p+1, p+2`).
    - `-vsync no` is safe on macOS to avoid frame sync issues.
- Processes are tracked in memory inside the Python process. If you kill
  Streamlit via `Ctrl+C`, the UxPlay processes might keep running. In that case:
  - Either use **Stop ALL instances** first, or
  - Manually kill `uxplay` from Activity Monitor or Terminal (`pkill uxplay`).
- This is a minimal, local tool for **demo helpers**, not a production daemon.
# screenmirror
