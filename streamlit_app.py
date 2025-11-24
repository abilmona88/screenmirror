import os
import shutil

import streamlit as st

from ux_manager import (
    start_instance,
    stop_instance,
    stop_all,
    is_running,
    get_pid,
)


st.set_page_config(
    page_title="Device Mirroring (UxPlay)",
    page_icon="📱",
    layout="centered",
)


def auto_detect_uxplay() -> str:
    """
    Try to find the uxplay binary automatically.

    Order:
    1. PATH (shutil.which)
    2. /usr/local/bin/uxplay
    3. /opt/homebrew/bin/uxplay

    Returns the first executable it finds, or just "uxplay" as a last resort.
    """
    candidates = [
        shutil.which("uxplay"),
        "/usr/local/bin/uxplay",
        "/opt/homebrew/bin/uxplay",
    ]
    for c in candidates:
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    # Fallback: let the manager try "uxplay" and raise a clear error if it fails
    return "uxplay"


# --- Defaults ---
DEFAULT_IPAD_NAME = "iPadMirror"
DEFAULT_IPAD_PORT = 7000
DEFAULT_IPHONE_NAME = "iPhoneMirror"
DEFAULT_IPHONE_PORT = 7100

if "binary_path" not in st.session_state:
    st.session_state["binary_path"] = auto_detect_uxplay()
if "ipad_name" not in st.session_state:
    st.session_state["ipad_name"] = DEFAULT_IPAD_NAME
if "ipad_port" not in st.session_state:
    st.session_state["ipad_port"] = DEFAULT_IPAD_PORT
if "iphone_name" not in st.session_state:
    st.session_state["iphone_name"] = DEFAULT_IPHONE_NAME
if "iphone_port" not in st.session_state:
    st.session_state["iphone_port"] = DEFAULT_IPHONE_PORT

binary_path = st.session_state["binary_path"]

# --- Header ---
st.title("📱 Device Mirroring via UxPlay")

st.markdown(
    """
This app starts **two UxPlay receivers** on your Mac (e.g. one for iPad, one for iPhone).

**Host (you) does:**
1. Click **Start Receiver 1** and/or **Start Receiver 2**.
2. Arrange the UxPlay windows on your screen.
3. Share your screen in Zoom/Teams.

**Guests do on their devices:**
1. On iPhone/iPad, open **Control Center**.
2. Tap **Screen Mirroring**.
3. Tap the name you tell them (e.g. `iPadMirror` or `iPhoneMirror`).
"""
)

with st.expander("Advanced: UxPlay binary path", expanded=False):
    st.write(
        """
The app tries to auto-detect the **uxplay** binary.

If `uxplay -h` works in Terminal, you usually don't need to touch this.

Only change this if you installed UxPlay to a non-standard location.
"""
    )
    binary_path = st.text_input(
        "UxPlay binary path",
        value=binary_path,
        key="binary_path",
    )

st.divider()

# --- Receiver 1 (e.g. iPad) ---
st.subheader("🧊 Receiver 1 (e.g. iPad)")

col1, col2 = st.columns(2)
with col1:
    ipad_name = st.text_input(
        "AirPlay name (what guests see)",
        value=st.session_state["ipad_name"],
        key="ipad_name",
    )
with col2:
    ipad_port = st.number_input(
        "Base port",
        min_value=1000,
        max_value=65535,
        step=1,
        value=int(st.session_state["ipad_port"]),
        key="ipad_port",
    )

ipad_running = is_running("ipad")
ipad_pid = get_pid("ipad")

c1, c2, c3 = st.columns([1, 1, 2])

with c1:
    if st.button("▶️ Start Receiver 1", type="primary", key="start_ipad"):
        if ipad_running:
            st.warning(f"Receiver 1 is already running (PID={ipad_pid}).")
        else:
            try:
                pid = start_instance(
                    label="ipad",
                    binary_path=st.session_state["binary_path"],
                    airplay_name=ipad_name,
                    base_port=int(ipad_port),
                )
                st.success(f"Started Receiver 1 (PID={pid}).")
            except FileNotFoundError as e:
                st.error(
                    f"Couldn't find UxPlay executable.\n\n"
                    f"Tried: `{st.session_state['binary_path']}`\n\n"
                    "Make sure UxPlay is installed and accessible.\n"
                    "You can also manually set the full path above "
                    "(for example `/usr/local/bin/uxplay`)."
                )
            except Exception as e:
                st.error(f"Failed to start Receiver 1: {e}")

with c2:
    if st.button("⏹ Stop Receiver 1", key="stop_ipad"):
        if not ipad_running:
            st.info("Receiver 1 is not running.")
        else:
            stopped = stop_instance("ipad")
            if stopped:
                st.success("Stopped Receiver 1.")
            else:
                st.warning("Receiver 1 was already stopped.")

with c3:
    if ipad_running:
        st.success(f"Status: RUNNING (PID={ipad_pid})")
    else:
        st.info("Status: not running")

st.markdown(
    f"""
**Instructions for guests (Receiver 1):**

1. Make sure their device is on the **same Wi-Fi** as this Mac.
2. On their iPhone/iPad:
   * Swipe **down from the top-right** to open **Control Center**.
   * Tap **Screen Mirroring**.
   * Tap **`{ipad_name}`**.

Their screen will appear in a UxPlay window on your Mac.
"""
)

st.divider()

# --- Receiver 2 (e.g. iPhone) ---
st.subheader("📱 Receiver 2 (e.g. iPhone)")

col1, col2 = st.columns(2)
with col1:
    iphone_name = st.text_input(
        "AirPlay name (what guests see)",
        value=st.session_state["iphone_name"],
        key="iphone_name",
    )
with col2:
    iphone_port = st.number_input(
        "Base port",
        min_value=1000,
        max_value=65535,
        step=1,
        value=int(st.session_state["iphone_port"]),
        key="iphone_port",
    )

iphone_running = is_running("iphone")
iphone_pid = get_pid("iphone")

c1, c2, c3 = st.columns([1, 1, 2])

with c1:
    if st.button("▶️ Start Receiver 2", type="primary", key="start_iphone"):
        if iphone_running:
            st.warning(f"Receiver 2 is already running (PID={iphone_pid}).")
        else:
            try:
                pid = start_instance(
                    label="iphone",
                    binary_path=st.session_state["binary_path"],
                    airplay_name=iphone_name,
                    base_port=int(iphone_port),
                )
                st.success(f"Started Receiver 2 (PID={pid}).")
            except FileNotFoundError:
                st.error(
                    f"Couldn't find UxPlay executable.\n\n"
                    f"Tried: `{st.session_state['binary_path']}`\n\n"
                    "Make sure UxPlay is installed and accessible.\n"
                    "You can also manually set the full path above "
                    "(for example `/usr/local/bin/uxplay`)."
                )
            except Exception as e:
                st.error(f"Failed to start Receiver 2: {e}")

with c2:
    if st.button("⏹ Stop Receiver 2", key="stop_iphone"):
        if not iphone_running:
            st.info("Receiver 2 is not running.")
        else:
            stopped = stop_instance("iphone")
            if stopped:
                st.success("Stopped Receiver 2.")
            else:
                st.warning("Receiver 2 was already stopped.")

with c3:
    if iphone_running:
        st.success(f"Status: RUNNING (PID={iphone_pid})")
    else:
        st.info("Status: not running")

st.markdown(
    f"""
**Instructions for guests (Receiver 2):**

1. Make sure their device is on the **same Wi-Fi** as this Mac.
2. On their iPhone/iPad:
   * Swipe **down from the top-right** to open **Control Center**.
   * Tap **Screen Mirroring**.
   * Tap **`{iphone_name}`**.

Their screen will appear in another UxPlay window on your Mac.
"""
)

st.divider()

st.subheader("Global controls")

if st.button("🛑 Stop ALL receivers", key="stop_all"):
    stopped = stop_all()
    if stopped == 0:
        st.info("No running UxPlay instances were found.")
    else:
        st.success(f"Stopped {stopped} UxPlay instance(s).")

st.caption(
    "Once both receivers are running and connected, arrange the two windows "
    "side by side and share your screen in Zoom/Teams."
)
