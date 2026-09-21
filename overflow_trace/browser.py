"""
Browser discovery and Chrome DevTools Protocol (CDP) controller.
"""

import asyncio
import json
import os
import shutil
import socket
import subprocess
import time
import urllib.request
from typing import Dict, Any, Optional
import websockets

CANDIDATE_BROWSER_PATHS = [
    # Windows standard paths
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    # macOS standard paths
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    # Linux standard binaries
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
    "brave-browser",
]


def find_browser_executable() -> Optional[str]:
    """Find a local Chromium-based browser executable."""
    for path in CANDIDATE_BROWSER_PATHS:
        if os.path.isabs(path):
            if os.path.exists(path) and os.path.isfile(path):
                return path
        else:
            resolved = shutil.which(path)
            if resolved:
                return resolved
    return None


def find_free_port(start_port: int = 9450) -> int:
    """Find an unbound local port for Chrome remote debugging."""
    for port in range(start_port, start_port + 100):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return start_port


async def cdp_send(ws, method: str, params: Optional[Dict[str, Any]] = None, timeout: float = 15.0) -> Dict[str, Any]:
    """Send a CDP command and await its corresponding response matching message id."""
    import random
    msg_id = random.randint(1000, 999999)
    payload = {"id": msg_id, "method": method}
    if params:
        payload["params"] = params

    await ws.send(json.dumps(payload))

    start_time = time.time()
    while True:
        if time.time() - start_time > timeout:
            raise TimeoutError(f"CDP command '{method}' timed out after {timeout}s")
        raw = await asyncio.wait_for(ws.recv(), timeout=timeout)
        data = json.loads(raw)
        if data.get("id") == msg_id:
            return data


async def inspect_url_viewport(
    url: str,
    device: Dict[str, Any],
    eval_script: str,
    wait_ms: int = 3000,
    timeout_sec: int = 30
) -> Dict[str, Any]:
    """
    Launch headless Chromium, emulate target device viewport, navigate to URL,
    and execute evaluation script.
    """
    browser_bin = find_browser_executable()
    if not browser_bin:
        raise RuntimeError("No compatible Chromium or Chrome/Edge browser binary found on system.")

    port = find_free_port()
    cmd = [
        browser_bin,
        "--headless=new",
        f"--remote-debugging-port={port}",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-extensions",
        "--disable-software-rasterizer",
        "--disable-blink-features=AutomationControlled",
        "--disable-features=IsolateOrigins,site-per-process",
        "about:blank"
    ]

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        # Wait for debugging port readiness
        ready = False
        for _ in range(30):
            try:
                res = urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=1)
                ver = json.loads(res.read().decode())
                browser_ws_url = ver["webSocketDebuggerUrl"]
                ready = True
                break
            except Exception:
                await asyncio.sleep(0.1)

        if not ready:
            raise RuntimeError("Chromium failed to expose remote debugging WebSocket.")

        # Create isolated target page
        async with websockets.connect(browser_ws_url) as b_ws:
            t_res = await cdp_send(b_ws, "Target.createTarget", {"url": "about:blank"})
            target_id = t_res.get("result", {}).get("targetId")
            if not target_id:
                raise RuntimeError("Failed to create isolated target page in Chromium.")

        page_ws_url = f"ws://127.0.0.1:{port}/devtools/page/{target_id}"

        async with websockets.connect(page_ws_url) as p_ws:
            # Enable core domains
            await cdp_send(p_ws, "Page.enable")

            # Set user agent override
            await cdp_send(p_ws, "Emulation.setUserAgentOverride", {
                "userAgent": device["user_agent"]
            })

            # Set mobile viewport metrics override
            await cdp_send(p_ws, "Emulation.setDeviceMetricsOverride", {
                "width": device["width"],
                "height": device["height"],
                "deviceScaleFactor": device["device_scale_factor"],
                "mobile": device["mobile"]
            })

            if device.get("has_touch"):
                await cdp_send(p_ws, "Emulation.setTouchEmulationEnabled", {
                    "enabled": True,
                    "maxTouchPoints": 5
                })

            # Navigate to target
            nav_start = time.perf_counter()
            await cdp_send(p_ws, "Page.navigate", {"url": url})

            # Allow scripts and layouts to settle
            await asyncio.sleep(wait_ms / 1000.0)
            nav_duration_ms = (time.perf_counter() - nav_start) * 1000

            # Execute evaluation script
            eval_res = await cdp_send(p_ws, "Runtime.evaluate", {
                "expression": eval_script,
                "returnByValue": True
            })

            result_value = eval_res.get("result", {}).get("result", {}).get("value")
            if result_value is None:
                err_details = eval_res.get("result", {}).get("exceptionDetails", {})
                raise RuntimeError(f"JavaScript evaluation failed: {err_details.get('text', 'Unknown error')}")

            # Parse result if serialized as string
            if isinstance(result_value, str):
                try:
                    result_value = json.loads(result_value)
                except Exception:
                    pass

            result_value["load_time_ms"] = round(nav_duration_ms, 2)
            result_value["target_url"] = url
            result_value["device_name"] = device["name"]
            result_value["device_width"] = device["width"]
            result_value["device_height"] = device["height"]
            result_value["device_scale_factor"] = device["device_scale_factor"]

            return result_value

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except Exception:
            proc.kill()
