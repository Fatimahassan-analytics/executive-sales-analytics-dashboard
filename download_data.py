"""Download script for the Superstore sample dataset.

Usage:
    python download_data.py             # tries direct URLs, falls back to bundled sample
    python download_data.py --kaggle    # requires kaggle.json
"""
from __future__ import annotations
import argparse
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

RAW_DIR = Path(__file__).parent / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

KAGGLE_DATASET = "bravehart101/sample-supermarket-dataset"
TARGET_FILENAME = "superstore.csv"

DIRECT_URLS = [
    "https://raw.githubusercontent.com/Plotly/dash-sample-apps/main/apps/dash-manufacture-spare-parts/assets/superstore.csv",
    "https://raw.githubusercontent.com/m Galarnyk/Python_Tutorials/master/Kaggle/Superstore.csv",
]


def ensure_sample() -> None:
    sample_path = RAW_DIR / "superstore_sample.csv"
    if sample_path.exists():
        return
    sys.path.insert(0, str(Path(__file__).parent / "src"))
    from data import generate_sample_data
    df = generate_sample_data()
    df.to_csv(sample_path, index=False)
    print(f"[OK] Wrote synthetic sample → {sample_path} ({len(df)} rows)")


def try_kaggle() -> bool:
    if not shutil.which("kaggle"):
        print("[INFO] kaggle CLI not installed. Skipping Kaggle route.")
        return False
    print(f"[INFO] Attempting Kaggle download of {KAGGLE_DATASET} ...")
    try:
        subprocess.run(
            ["kaggle", "datasets", "download", "-d", KAGGLE_DATASET,
             "-p", str(RAW_DIR), "--unzip"],
            check=True,
        )
        # Find the downloaded CSV (name varies by dataset)
        candidates = list(RAW_DIR.glob("*.csv"))
        candidates = [c for c in candidates if "sample" not in c.name]
        if candidates:
            dst = RAW_DIR / TARGET_FILENAME
            candidates[0].rename(dst)
            print(f"[OK] Renamed {candidates[0].name} → {dst.name}")
            return True
    except subprocess.CalledProcessError as e:
        print(f"[WARN] Kaggle download failed: {e}")
    return False


def try_direct() -> bool:
    for url in DIRECT_URLS:
        print(f"[INFO] Trying direct URL: {url}")
        try:
            target = RAW_DIR / TARGET_FILENAME
            urllib.request.urlretrieve(url, target)
            print(f"[OK] Downloaded → {target}")
            return True
        except Exception as e:
            print(f"[WARN] Direct URL failed: {e}")
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kaggle", action="store_true",
                        help="Force Kaggle route (requires kaggle.json).")
    args = parser.parse_args()

    ensure_sample()
    target = RAW_DIR / TARGET_FILENAME
    if target.exists():
        print(f"[OK] {target} already exists; skipping download.")
        return

    ok = False
    if args.kaggle:
        ok = try_kaggle() or try_direct()
    else:
        ok = try_direct() or try_kaggle()

    if not ok:
        print("[WARN] Could not download full dataset. "
              "Dashboard will use the bundled synthetic sample instead.")


if __name__ == "__main__":
    main()
