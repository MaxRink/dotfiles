#!/usr/bin/env python3
"""
Lenovo ThinkSystem Firmware Version Checker

Queries the Lenovo support JSON API to find the latest XCC, UEFI and NIC firmware
versions. No browser or Selenium required.

Source: https://datacentersupport.lenovo.com/us/en/api/v4/downloads/drivers
NIC compatibility: https://docs.nvidia.com/networking/display/connectx6lxfirmwarev{VER}/firmware+compatible+products

Usage:
    python lenovo-firmware-versions.py --model SR650V3
    python lenovo-firmware-versions.py --all --format json
    python lenovo-firmware-versions.py --model SR650V3 --download --download-dir ~/Downloads/firmwares

    # Include NIC firmware with MLNX_OFED and DOCA-HOST compatibility check:
    # ubuntu22 legacy (OFED 23.10-0.5.5.0):
    python lenovo-firmware-versions.py --model SR650V3 --nic --target-mlnx-ofed 23.10-0.5.5.0
    # ubuntu24 legacy (OFED 24.10-2.1.8.0, k8s 1.31-1.32):
    python lenovo-firmware-versions.py --model SR650V3 --nic --target-mlnx-ofed 24.10-2.1.8.0
    # ubuntu24 doca (DOCA 2.9.3, k8s 1.33+):
    python lenovo-firmware-versions.py --model SR650V3 --nic --target-doca 2.9.3

Production driver versions (from caas-image-builder .gitlab-ci.yml):
    k8s 1.31-1.32 / ubuntu22 → OFED 23.10-0.5.5.0
    k8s 1.31-1.32 / ubuntu24 → OFED 24.10-2.1.8.0
    k8s 1.33       / ubuntu24 → DOCA 2.9.2
    k8s 1.34-1.35  / ubuntu24 → DOCA 2.9.3
"""

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Optional, List

import requests

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False


LENOVO_API_BASE = "https://datacentersupport.lenovo.com/us/en/api/v4/downloads/drivers"
LENOVO_DC_BASE = "https://datacentersupport.lenovo.com/us/en/products/servers/thinksystem"

# NVIDIA firmware compatibility docs URL template.
# Replace dots in version with nothing: 26.43.1014 -> 26431014
NVIDIA_COMPAT_URL = "https://docs.nvidia.com/networking/display/connectx6lxfirmwarev{ver}/firmware+compatible+products"

# Cache to avoid hitting NVIDIA docs repeatedly for the same firmware version
_nvidia_compat_cache: dict = {}

# Server model configurations.
# url_name: path component used in the Lenovo support URL (e.g. "sr650v3")
# type: product type code (e.g. "7D76")
# nic_generation: "v3" for Eagle Stream (xx.XX.XXXX version naming),
#                 "v2" for Whitley (DOCA/OFED version in filename),
#                 None if model has no Mellanox NIC
LENOVO_MODELS = {
    "SR650V3": {
        "name": "ThinkSystem SR650 V3",
        "type": "7D76",
        "url_name": "sr650v3",
        "platform": "Eagle Stream",
        "nic_generation": "v3",
    },
    "SR630V3": {
        "name": "ThinkSystem SR630 V3",
        "type": "7D72",
        "url_name": "sr630v3",
        "platform": "Eagle Stream",
        "nic_generation": "v3",
    },
    "SR650V2": {
        "name": "ThinkSystem SR650 V2",
        "type": "7Z73",
        "url_name": "sr650v2",
        "platform": "Whitley",
        "nic_generation": "v2",
    },
    "SR630V2": {
        "name": "ThinkSystem SR630 V2",
        "type": "7Z71",
        "url_name": "sr630v2",
        "platform": "Whitley",
        "nic_generation": "v2",
    },
    "SR250V2": {
        "name": "ThinkSystem SR250 V2",
        "type": "7D7Q",
        "url_name": "sr250v2",
        "platform": "Whitley",
        "nic_generation": None,
    },
    "SR650": {
        "name": "ThinkSystem SR650",
        "type": "7X06",
        "url_name": "sr650",
        "platform": "Purley",
        "nic_generation": None,
    },
}


@dataclass
class NicFirmwareInfo:
    filename: str
    version: str       # Numeric version like "26.47.1026" (V3) or label like "doca-3.1.0" (V2)
    driver_type: str   # "legacy" or "doca"
    mlnx_ofed: Optional[str] = None   # MLNX_OFED version certified with
    doca_host: Optional[str] = None   # DOCA-HOST version certified with
    download_url: Optional[str] = None


@dataclass
class FirmwareInfo:
    model: str
    model_name: str
    platform: str
    xcc_version: Optional[str] = None
    xcc_build: Optional[str] = None
    xcc_date: Optional[str] = None
    xcc_file: Optional[str] = None
    xcc_url: Optional[str] = None
    uefi_version: Optional[str] = None
    uefi_build: Optional[str] = None
    uefi_date: Optional[str] = None
    uefi_file: Optional[str] = None
    uefi_url: Optional[str] = None
    nic: List[NicFirmwareInfo] = field(default_factory=list)
    error: Optional[str] = None


def _get_unix_ts(item: dict) -> int:
    d = item.get("Date", {})
    return d.get("Unix", 0) if isinstance(d, dict) else 0


def _format_date(ts_ms: int) -> str:
    if not ts_ms:
        return "unknown"
    return datetime.fromtimestamp(ts_ms / 1000).strftime("%d %b %Y")


def fetch_api_items(url_name: str, type_code: str) -> list:
    """
    Fetch all firmware items from the Lenovo support API for a given model.

    Requires the Referer header to be set correctly — otherwise the API
    returns 'deny access'.
    """
    product_id = f"servers%2Fthinksystem%2F{url_name}%2F{type_code.lower()}"
    referer = f"{LENOVO_DC_BASE}/{url_name}/{type_code.lower()}/downloads/driver-list/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": referer,
    }
    r = requests.get(f"{LENOVO_API_BASE}?productId={product_id}", headers=headers, timeout=30)
    r.raise_for_status()
    body = r.json().get("body", {})
    if not isinstance(body, dict):
        raise ValueError(f"Unexpected API response: {str(body)[:100]}")
    return body.get("DownloadItems", [])


def _extract_fw_url(item: dict, prefix: str) -> Optional[str]:
    """Return the first URL in item's Files that contains the given filename prefix."""
    for f in item.get("Files", []):
        url = f.get("URL", "")
        if prefix in url:
            return url
    return None


def _normalize_fw_url(url: str) -> tuple:
    """
    Given a Lenovo firmware download URL, return (filename, download_url).

    V3 models distribute XCC/UEFI as .zip (containing .uxz inside).
    V2/V1 models distribute XCC/UEFI as .uxz directly.
    For V3, replace .zip with .uxz — the direct .uxz URL works too.
    """
    filename = url.split("/")[-1]
    if filename.endswith(".zip") and "lnvgy_fw_" in filename:
        filename = filename[:-4] + ".uxz"
        url = url[:-4] + ".uxz"
    return filename, url


def extract_xcc_info(items: list) -> dict:
    """Extract latest XCC/BMC firmware info from API items."""
    candidates = [
        i for i in items
        if "XClarity Controller" in i.get("Title", "") and "Firmware" in i.get("Title", "")
    ]
    if not candidates:
        return {}
    item = max(candidates, key=_get_unix_ts)

    for f in item.get("Files", []):
        url = f.get("URL", "")
        if not (url.endswith(".zip") or url.endswith(".uxz")):
            continue
        # Skip auxiliary archives (copyright, extras, license, sbom)
        basename = url.split("/")[-1]
        if any(s in basename for s in ("_copyright", "_extras", "_license", "_sbom")):
            continue
        m = re.search(r"lnvgy_fw_xcc_([a-z0-9]+)-(\d+\.\d+)_anyos", url, re.IGNORECASE)
        if m:
            filename, dl_url = _normalize_fw_url(url)
            return {
                "version": m.group(2),
                "build": m.group(1),
                "file": filename,
                "url": dl_url,
                "date": _format_date(_get_unix_ts(item)),
            }
    return {}


def extract_uefi_info(items: list) -> dict:
    """Extract latest UEFI/BIOS firmware info from API items."""
    candidates = [
        i for i in items
        if ("UEFI" in i.get("Title", "") or "BIOS" in i.get("Title", ""))
        and "Firmware" in i.get("Title", "")
        and "NIC" not in i.get("Title", "")
    ]
    if not candidates:
        return {}
    item = max(candidates, key=_get_unix_ts)

    for f in item.get("Files", []):
        url = f.get("URL", "")
        if not (url.endswith(".zip") or url.endswith(".uxz")):
            continue
        basename = url.split("/")[-1]
        if any(s in basename for s in ("_copyright", "_extras", "_license", "_sbom")):
            continue
        m = re.search(r"lnvgy_fw_uefi_([a-z0-9]+)-(\d+\.\d+)_anyos", url, re.IGNORECASE)
        if m:
            filename, dl_url = _normalize_fw_url(url)
            return {
                "version": m.group(2),
                "build": m.group(1),
                "file": filename,
                "url": dl_url,
                "date": _format_date(_get_unix_ts(item)),
            }
    return {}


def extract_nic_candidates_v3(items: list) -> list:
    """
    Extract NIC firmware candidates for V3 models (Eagle Stream).

    Filename pattern: mlnx-lnvgy_fw_nic_cx-xx.XX.XXXX-..._anyos_comp.zip
    The 'xx' prefix maps to '26' (ConnectX-6 Lx family).
    Returns list of dicts sorted newest-first.
    """
    candidates = [
        i for i in items
        if "mellanox" in i.get("Title", "").lower()
        and "Firmware" in i.get("Title", "")
        and "ConnectX" in i.get("Title", "")
        and "Windows" not in i.get("Title", "")
    ]
    candidates.sort(key=_get_unix_ts, reverse=True)

    result = []
    for item in candidates:
        for f in item.get("Files", []):
            url = f.get("URL", "")
            m = re.search(r"lnvgy_fw_nic_cx-xx\.(\d+\.\d+)-", url, re.IGNORECASE)
            if m:
                ver = f"26.{m.group(1)}"
                filename = url.split("/")[-1]
                if filename.endswith(".zip"):
                    filename = filename[:-4] + ".uxz"
                result.append({
                    "version": ver,
                    "filename": filename,
                    "date": _format_date(_get_unix_ts(item)),
                    "download_url": url,
                })
                break
    return result


def extract_nic_candidates_v2(items: list) -> list:
    """
    Extract NIC firmware candidates for V2 models (Whitley).

    Filename pattern: mlnx-lnvgy_fw_nic_cx-doca-X.Y.Z-N_linux_x86-64.bin
    or:               mlnx-lnvgy_fw_nic_cx-24.04-0.6.6.0-0_linux_x86-64.bin
    Returns list of dicts sorted newest-first.
    """
    candidates = [
        i for i in items
        if "mellanox" in i.get("Title", "").lower()
        and "Firmware" in i.get("Title", "")
        and "Linux" in i.get("Title", "")
    ]
    candidates.sort(key=_get_unix_ts, reverse=True)

    result = []
    for item in candidates:
        for f in item.get("Files", []):
            url = f.get("URL", "")
            if "_linux_x86-64.bin" not in url:
                continue
            filename = url.split("/")[-1]
            m_doca = re.search(r"lnvgy_fw_nic_cx-doca-([\d.]+)-", filename)
            m_ofed = re.search(r"lnvgy_fw_nic_cx-([\d.]+-[\d.]+)-\d", filename)
            if m_doca:
                ver = f"doca-{m_doca.group(1)}"
                driver_type = "doca"
            elif m_ofed:
                ver = m_ofed.group(1)
                driver_type = "legacy"
            else:
                ver = "unknown"
                driver_type = "unknown"
            result.append({
                "version": ver,
                "filename": filename,
                "date": _format_date(_get_unix_ts(item)),
                "download_url": url,
                "driver_type": driver_type,
            })
            break
    return result


def check_nvidia_compat(version: str) -> dict:
    """
    Fetch NVIDIA ConnectX-6 Lx firmware compatibility page and return certified
    MLNX_OFED and DOCA-HOST versions.

    Only works for numeric versions like '26.47.1026' (V3 models).
    URL: https://docs.nvidia.com/networking/display/connectx6lxfirmwarev{VER}/firmware+compatible+products
    """
    if version in _nvidia_compat_cache:
        return _nvidia_compat_cache[version]

    ver_nodots = version.replace(".", "")
    url = NVIDIA_COMPAT_URL.format(ver=ver_nodots)
    result = {"mlnx_ofed": [], "doca_host": [], "url": url}

    try:
        resp = requests.get(url, timeout=20)
        if resp.status_code != 200:
            _nvidia_compat_cache[version] = result
            return result

        if not BS4_AVAILABLE:
            _nvidia_compat_cache[version] = result
            return result

        soup = BeautifulSoup(resp.text, "html.parser")
        for row in soup.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) < 2:
                continue
            label = cells[0].get_text(strip=True)
            value = cells[1].get_text(separator=" ", strip=True)
            value = re.split(r"\s*Note:", value)[0].strip()
            versions = [v.strip() for v in value.split("/") if v.strip()]

            if label == "MLNX_OFED / DOCA-HOST":
                result["mlnx_ofed"] = [v for v in versions if re.match(r"\d+\.\d{2}-", v)]
            elif label == "MLNX_OFED":
                result["mlnx_ofed"] = [v for v in versions if re.match(r"\d+\.\d{2}-", v)]
            elif label == "DOCA-HOST":
                result["doca_host"] = [
                    v for v in versions
                    if re.match(r"^\d+\.\d+", v) and not re.match(r"\d+\.\d{2}-", v)
                ]
    except Exception:
        pass

    _nvidia_compat_cache[version] = result
    return result


def find_nic_for_drivers(
    candidates: list,
    target_mlnx_ofed: Optional[str],
    target_doca: Optional[str],
) -> List[NicFirmwareInfo]:
    """
    Given V3 NIC firmware candidates (numeric versions), find the best match
    for target MLNX_OFED and DOCA-HOST versions.

    Checks from newest to oldest, stops as soon as a match is found for each type.
    """
    legacy_result = None
    doca_result = None

    for candidate in candidates:
        ver = candidate["version"]
        if not re.match(r"^\d+\.\d+\.\d+$", ver):
            continue

        if legacy_result and doca_result:
            break

        compat = check_nvidia_compat(ver)
        print(f"    Checking NIC {ver}: MLNX_OFED={compat['mlnx_ofed']} DOCA={compat['doca_host']}", file=sys.stderr)

        if not legacy_result and target_mlnx_ofed:
            for certified in compat["mlnx_ofed"]:
                if target_mlnx_ofed in certified or certified in target_mlnx_ofed:
                    legacy_result = NicFirmwareInfo(
                        filename=candidate["filename"],
                        version=ver,
                        driver_type="legacy",
                        mlnx_ofed=certified,
                        download_url=candidate.get("download_url"),
                    )
                    break

        if not doca_result and target_doca:
            for certified in compat["doca_host"]:
                if ".".join(target_doca.split(".")[:2]) == ".".join(certified.split(".")[:2]):
                    doca_result = NicFirmwareInfo(
                        filename=candidate["filename"],
                        version=ver,
                        driver_type="doca",
                        doca_host=certified,
                        download_url=candidate.get("download_url"),
                    )
                    break

    result = []
    if legacy_result:
        result.append(legacy_result)
    if doca_result:
        result.append(doca_result)
    return result


def query_model(
    model_key: str,
    check_nic: bool = False,
    target_mlnx_ofed: Optional[str] = None,
    target_doca: Optional[str] = None,
) -> FirmwareInfo:
    """Query the Lenovo API for a model's latest firmware versions."""
    config = LENOVO_MODELS[model_key]
    info = FirmwareInfo(model=model_key, model_name=config["name"], platform=config["platform"])

    try:
        items = fetch_api_items(config["url_name"], config["type"])

        xcc = extract_xcc_info(items)
        if xcc:
            info.xcc_version = xcc.get("version")
            info.xcc_build = xcc.get("build")
            info.xcc_date = xcc.get("date")
            info.xcc_file = xcc.get("file")
            info.xcc_url = xcc.get("url")

        uefi = extract_uefi_info(items)
        if uefi:
            info.uefi_version = uefi.get("version")
            info.uefi_build = uefi.get("build")
            info.uefi_date = uefi.get("date")
            info.uefi_file = uefi.get("file")
            info.uefi_url = uefi.get("url")

        if check_nic:
            nic_gen = config.get("nic_generation")
            print(f"  Checking NIC firmware ({nic_gen or 'N/A'})...", file=sys.stderr)
            if nic_gen == "v3":
                candidates = extract_nic_candidates_v3(items)
                if (target_mlnx_ofed or target_doca) and candidates:
                    info.nic = find_nic_for_drivers(candidates, target_mlnx_ofed, target_doca)
                else:
                    for c in candidates[:3]:
                        info.nic.append(NicFirmwareInfo(
                            filename=c["filename"], version=c["version"], driver_type="unknown",
                            download_url=c.get("download_url"),
                        ))
            elif nic_gen == "v2":
                candidates = extract_nic_candidates_v2(items)
                for c in candidates[:2]:
                    info.nic.append(NicFirmwareInfo(
                        filename=c["filename"],
                        version=c.get("version", "unknown"),
                        driver_type=c.get("driver_type", "unknown"),
                        download_url=c.get("download_url"),
                    ))
            else:
                print(f"  No Mellanox NIC defined for {model_key}", file=sys.stderr)

    except Exception as e:
        info.error = str(e)

    return info


def download_file(url: str, dest: Path):
    """Download a firmware file to dest, skipping if it already exists."""
    if dest.exists():
        print(f"  [SKIP] {dest.name} already exists")
        return
    print(f"  Downloading {dest.name}...", end="", flush=True)
    r = requests.get(url, stream=True, timeout=120)
    r.raise_for_status()
    with open(dest, "wb") as fh:
        for chunk in r.iter_content(chunk_size=65536):
            fh.write(chunk)
    size_mb = dest.stat().st_size // 1024 // 1024
    print(f" OK ({size_mb} MB)")


def download_firmware(info: FirmwareInfo, download_dir: Path, include_nic: bool = False):
    """Download XCC, UEFI and optionally NIC firmware files to download_dir."""
    download_dir.mkdir(parents=True, exist_ok=True)
    if info.xcc_url and info.xcc_file:
        download_file(info.xcc_url, download_dir / info.xcc_file)
    if info.uefi_url and info.uefi_file:
        download_file(info.uefi_url, download_dir / info.uefi_file)
    if include_nic:
        for nic in info.nic:
            if nic.download_url:
                download_file(nic.download_url, download_dir / nic.filename)


def print_text_output(results: List[FirmwareInfo]):
    """Print results in human-readable text format."""
    print("\n" + "=" * 80)
    print("Lenovo ThinkSystem Firmware Versions")
    print(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    for info in results:
        downloads_url = f"{LENOVO_DC_BASE}/{LENOVO_MODELS[info.model]['url_name']}/{LENOVO_MODELS[info.model]['type'].lower()}/downloads/driver-list/"
        print(f"\n{info.model_name} ({info.model}) - {info.platform}")
        print("-" * 60)

        if info.error:
            print(f"  Error: {info.error}")
            continue

        if info.xcc_version:
            xcc_str = f"  XCC (BMC):  {info.xcc_version}"
            if info.xcc_build:
                xcc_str += f" (build: {info.xcc_build})"
            print(xcc_str)
            if info.xcc_date:
                print(f"    Date: {info.xcc_date}")
            if info.xcc_file:
                print(f"    File: {info.xcc_file}")
        else:
            print("  XCC (BMC):  Not found")

        if info.uefi_version:
            uefi_str = f"  UEFI:       {info.uefi_version}"
            if info.uefi_build:
                uefi_str += f" (build: {info.uefi_build})"
            print(uefi_str)
            if info.uefi_date:
                print(f"    Date: {info.uefi_date}")
            if info.uefi_file:
                print(f"    File: {info.uefi_file}")
        else:
            print("  UEFI:       Not found")

        if info.nic:
            print(f"  NIC firmware (Mellanox ConnectX):")
            for nic in info.nic:
                compat_str = ""
                if nic.mlnx_ofed:
                    compat_str = f"  (certified: MLNX_OFED {nic.mlnx_ofed})"
                elif nic.doca_host:
                    compat_str = f"  (certified: DOCA {nic.doca_host})"
                print(f"    [{nic.driver_type}]  {nic.version}  [{nic.filename}]{compat_str}")

    print("\n" + "=" * 80)
    print("Manual verification URLs:")
    for info in results:
        cfg = LENOVO_MODELS[info.model]
        url = f"{LENOVO_DC_BASE}/{cfg['url_name']}/{cfg['type'].lower()}/downloads/driver-list/"
        print(f"  {info.model}: {url}")
    print("=" * 80)


def print_json_output(results: List[FirmwareInfo]):
    """Print results in JSON format."""
    output = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "models": [asdict(info) for info in results],
    }
    print(json.dumps(output, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Check latest Lenovo ThinkSystem firmware versions (no browser required)"
    )
    parser.add_argument("--model", "-m", choices=list(LENOVO_MODELS.keys()),
                        action="append",
                        help="Server model(s) to query (can be specified multiple times)")
    parser.add_argument("--all", "-a", action="store_true",
                        help="Query all supported models")
    parser.add_argument("--format", "-f", choices=["text", "json"], default="text",
                        help="Output format (default: text)")
    parser.add_argument("--list-models", "-l", action="store_true",
                        help="List supported models and exit")
    parser.add_argument("--nic", action="store_true",
                        help="Also check NIC firmware (Mellanox ConnectX)")
    parser.add_argument("--target-mlnx-ofed",
                        help="Target MLNX_OFED version for NIC selection (e.g. 24.10-2.1.8.0)")
    parser.add_argument("--target-doca",
                        help="Target DOCA-HOST version for NIC selection (e.g. 2.9.3)")
    parser.add_argument("--ci-config",
                        help="Path to caas-image-builder .gitlab-ci.yml (auto-reads OFED/DOCA targets). "
                             "Also reads from CAAS_IMAGE_BUILDER_PATH env var.")
    parser.add_argument("--download", action="store_true",
                        help="Download firmware files")
    parser.add_argument("--download-dir", type=Path, default=Path("."),
                        help="Directory for downloaded files (default: current dir)")

    args = parser.parse_args()

    if args.list_models:
        print("Supported models:")
        for key, config in LENOVO_MODELS.items():
            nic = config.get("nic_generation") or "none"
            print(f"  {key:12} - {config['name']} (Type {config['type']}, {config['platform']}, NIC: {nic})")
        sys.exit(0)

    if not args.model and not args.all:
        parser.error("Either --model or --all is required")

    # Resolve NIC target versions: explicit flags override ci-config
    target_mlnx_ofed = args.target_mlnx_ofed
    target_doca = args.target_doca

    if args.nic and not target_mlnx_ofed and not target_doca:
        # Try to auto-read from ci-config
        try:
            _dir = Path(__file__).parent
            sys.path.insert(0, str(_dir))
            from parse_ci_drivers import parse_ci_drivers, find_ci_config
            ci_path = find_ci_config(args.ci_config)
            if ci_path:
                ci_drivers = parse_ci_drivers(ci_path)
                target_mlnx_ofed = ci_drivers.get("mlnx_ofed")
                target_doca = ci_drivers.get("doca")
                print(f"  CI config: {ci_path}", file=sys.stderr)
                print(f"  Auto-detected: OFED={target_mlnx_ofed} DOCA={target_doca}", file=sys.stderr)
            else:
                parser.error("--nic requires --target-mlnx-ofed or --target-doca "
                             "(or --ci-config / CAAS_IMAGE_BUILDER_PATH to auto-detect)")
        except ImportError:
            parser.error("--nic requires at least one of --target-mlnx-ofed or --target-doca")

    models_to_query = list(LENOVO_MODELS.keys()) if args.all else args.model

    results = []
    for model in models_to_query:
        print(f"Querying {model}...", file=sys.stderr)
        info = query_model(
            model,
            check_nic=args.nic,
            target_mlnx_ofed=target_mlnx_ofed,
            target_doca=target_doca,
        )
        results.append(info)

    if args.download:
        for info in results:
            if not info.error:
                print(f"\nDownloading {info.model}...", file=sys.stderr)
                download_firmware(info, args.download_dir, include_nic=args.nic)

    if args.format == "json":
        print_json_output(results)
    else:
        print_text_output(results)


if __name__ == "__main__":
    main()
