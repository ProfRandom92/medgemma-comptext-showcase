"""Google Colab setup script for MedGemma CompText Showcase.

Run this cell first in a Colab notebook to install dependencies,
verify GPU availability, and download a sample X-ray image.

Usage (in a Colab cell)::

    !python setup_colab.py
"""

from __future__ import annotations

import subprocess
import sys


def install_packages() -> None:
    """Install required ML packages."""
    packages = [
        "torch",
        "transformers",
        "accelerate",
        "bitsandbytes",
        "pillow",
    ]
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "--quiet", *packages],
    )
    print("[✓] ML packages installed.")


def check_gpu() -> bool:
    """Check for CUDA GPU availability."""
    try:
        import torch

        if torch.cuda.is_available():
            name = torch.cuda.get_device_name(0)
            print(f"[✓] GPU detected: {name}")
            return True
        print("[⚠] No GPU detected — model will run in Edge Simulation Mode.")
        return False
    except ImportError:
        print("[✗] torch not installed.")
        return False


def download_sample_xray() -> None:
    """Download a sample chest X-ray image for testing."""
    import urllib.request

    url = (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/"
        "c/c8/Chest_Xray_PA_3-8-2010.png/"
        "220px-Chest_Xray_PA_3-8-2010.png"
    )
    dest = "sample_xray.jpg"
    try:
        urllib.request.urlretrieve(url, dest)
        print(f"[✓] Sample X-ray saved to {dest}")
    except Exception as exc:  # noqa: BLE001
        print(f"[⚠] Could not download sample X-ray: {exc}")
        print("    You can manually place an image at ./sample_xray.jpg")


if __name__ == "__main__":
    print("=== MedGemma CompText — Colab Setup ===\n")
    install_packages()
    check_gpu()
    download_sample_xray()
    print("\n=== Setup complete ===")
