#!/usr/bin/env python3
"""
HPE ProLiant Firmware Version Checker

Queries the HPE Linux SDR repository to find the latest iLO, System ROM and
NIC firmware versions. No browser or login required.

Source: https://downloads.linux.hpe.com/SDR/repo/fwpp-gen{10,11}/current/
NIC compatibility: https://docs.nvidia.com/networking/display/connectx6lxfirmwarev{VER}/firmware+compatible+products

Usage:
    python hpe-firmware-versions.py --model DL380-Gen11
    python hpe-firmware-versions.py --all
    python hpe-firmware-versions.py --all --format json
    python hpe-firmware-versions.py --model DL380-Gen11 --download --download-dir /tmp/fw

    # Include NIC firmware with MLNX_OFED and DOCA-HOST compatibility check:
    # ubuntu22 legacy (OFED 23.10-0.5.5.0):
    python hpe-firmware-versions.py --model DL380-Gen11 --nic --target-mlnx-ofed 23.10-0.5.5.0
    # ubuntu24 legacy (OFED 24.10-2.1.8.0, k8s 1.31-1.32):
    python hpe-firmware-versions.py --model DL380-Gen11 --nic --target-mlnx-ofed 24.10-2.1.8.0
    # ubuntu24 doca (DOCA 2.9.3, k8s 1.33+):
    python hpe-firmware-versions.py --model DL380-Gen11 --nic --target-doca 2.9.3
"""

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Optional, List

import requests

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

# HPE Linux SDR repository base URL
SDR_BASE = "https://downloads.linux.hpe.com/SDR/repo"

# NVIDIA firmware compatibility docs URL template.
# Replace dots in version with nothing: 26.43.1014 -> 26431014
NVIDIA_COMPAT_URL = "https://docs.nvidia.com/networking/display/connectx6lxfirmwarev{ver}/firmware+compatible+products"

# HPE server model configurations
# rom_code: U-code prefix that identifies the System ROM for this specific model
# nic_part: OEM part number of the Mellanox NIC installed (None if no Mellanox NIC)
HPE_MODELS = {
    "DL380-Gen11": {
        "name": "ProLiant DL380 Gen11",
        "generation": "Gen11",
        "ilo_gen": 6,
        "rom_code": "U54",
        "repo_url": f"{SDR_BASE}/fwpp-gen11/current/",
        "nic_part": "MCX631102AS-ADA",  # ConnectX-6 Lx 25GbE Dual-port SFP28
    },
    "DL320-Gen11": {
        "name": "ProLiant DL320 Gen11",
        "generation": "Gen11",
        "ilo_gen": 6,
        "rom_code": "U63",
        "repo_url": f"{SDR_BASE}/fwpp-gen11/current/",
        "nic_part": "MCX631102AS-ADA",  # ConnectX-6 Lx 25GbE Dual-port SFP28
    },
    "DL360-Gen11": {
        "name": "ProLiant DL360 Gen11",
        "generation": "Gen11",
        "ilo_gen": 6,
        "rom_code": "U58",
        "repo_url": f"{SDR_BASE}/fwpp-gen11/current/",
        "nic_part": "MCX631102AS-ADA",
    },
    "DL365-Gen11": {
        "name": "ProLiant DL365 Gen11",
        "generation": "Gen11",
        "ilo_gen": 6,
        "rom_code": "U59",
        "repo_url": f"{SDR_BASE}/fwpp-gen11/current/",
        "nic_part": "MCX631102AS-ADA",
    },
    "DL325-Gen11": {
        "name": "ProLiant DL325 Gen11",
        "generation": "Gen11",
        "ilo_gen": 6,
        "rom_code": "U62",
        "repo_url": f"{SDR_BASE}/fwpp-gen11/current/",
        "nic_part": "MCX631102AS-ADA",
    },
    "DL20-Gen10": {
        "name": "ProLiant DL20 Gen10",
        "generation": "Gen10",
        "ilo_gen": 5,
        "rom_code": "U43",
        "repo_url": f"{SDR_BASE}/fwpp-gen10/current/",
        "nic_part": None,  # No Mellanox NIC in DL20 Gen10
    },
    "DL360-Gen10": {
        "name": "ProLiant DL360 Gen10",
        "generation": "Gen10",
        "ilo_gen": 5,
        "rom_code": "U32",
        "repo_url": f"{SDR_BASE}/fwpp-gen10/current/",
        "nic_part": None,
    },
    "DL380-Gen10": {
        "name": "ProLiant DL380 Gen10",
        "generation": "Gen10",
        "ilo_gen": 5,
        "rom_code": "U30",
        "repo_url": f"{SDR_BASE}/fwpp-gen10/current/",
        "nic_part": None,
    },
}

# Cache SDR directory listings to avoid repeated requests (keyed by repo_url)
_repo_cache: dict = {}


@dataclass
class NicFirmwareInfo:
    part: str
    filename: str
    version: str
    driver_type: str   # "legacy" or "doca"
    os: str            # "ubuntu22" or "ubuntu24"
    mlnx_ofed: Optional[str] = None   # MLNX_OFED version this is certified with
    doca_host: Optional[str] = None   # DOCA-HOST version this is certified with


@dataclass
class FirmwareInfo:
    model: str
    model_name: str
    generation: str
    ilo_type: str
    ilo_version: Optional[str] = None
    ilo_filename: Optional[str] = None
    ilo_date: Optional[str] = None
    rom_version: Optional[str] = None
    rom_filename: Optional[str] = None
    rom_date: Optional[str] = None
    nic: List[NicFirmwareInfo] = field(default_factory=list)
    error: Optional[str] = None


def fetch_repo_index(repo_url: str) -> str:
    """Fetch and cache the SDR repository directory listing."""
    if repo_url not in _repo_cache:
        resp = requests.get(repo_url, timeout=30)
        resp.raise_for_status()
        _repo_cache[repo_url] = resp.text
    return _repo_cache[repo_url]


def get_latest_ilo(repo_url: str, ilo_gen: int) -> tuple:
    """Return (filename, version, date) of the latest iLO firmware in the repo."""
    html = fetch_repo_index(repo_url)

    # Match e.g. ilo6_174.fwpkg with optional date column
    # Directory listing format: href="ilo6_174.fwpkg"  ...  2026-01-15 05:21
    pattern = rf'href="(ilo{ilo_gen}_(\d+)\.fwpkg)"'
    matches = re.findall(pattern, html)
    if not matches:
        return None, None, None

    # Sort by version number (integer), pick highest
    matches.sort(key=lambda m: int(m[1]))
    filename, raw_ver = matches[-1]

    # Convert raw version (e.g. "174" → "1.74", "318" → "3.18")
    version = f"{raw_ver[:-2]}.{raw_ver[-2:]}" if len(raw_ver) >= 3 else raw_ver

    # Extract date from the directory listing line containing this filename
    date = _extract_date_from_listing(html, filename)

    return filename, version, date


def get_latest_rom(repo_url: str, rom_code: str) -> tuple:
    """Return (filename, version, date) of the latest System ROM for the given U-code."""
    html = fetch_repo_index(repo_url)

    # Match e.g. U54_2.72_11_27_2025.fwpkg
    pattern = rf'href="({re.escape(rom_code)}_(\d+\.\d+)_(\d{{2}})_(\d{{2}})_(\d{{4}})\.fwpkg)"'
    matches = re.findall(pattern, html)
    if not matches:
        return None, None, None

    # Sort by version (float), then by date as tiebreaker
    def sort_key(m):
        filename, ver, month, day, year = m
        return (float(ver), int(year), int(month), int(day))

    matches.sort(key=sort_key)
    filename, version, month, day, year = matches[-1]
    date = f"{year}-{month}-{day}"

    return filename, version, date


def _extract_date_from_listing(html: str, filename: str) -> Optional[str]:
    """Extract the date from the directory listing line for a given file."""
    # Apache-style listing: filename  YYYY-MM-DD HH:MM  size
    pattern = rf'{re.escape(filename)}[^<]*?(\d{{4}}-\d{{2}}-\d{{2}})'
    m = re.search(pattern, html)
    return m.group(1) if m else None


def get_nic_firmwares(repo_url: str, part: str) -> List[tuple]:
    """
    Return list of (filename, version) for all NIC firmware files matching
    the given OEM part number in the SDR repo, sorted by version ascending.
    """
    html = fetch_repo_index(repo_url)
    # e.g. 26_43_1014-MCX631102AS-ADA_Ax.pldm.fwpkg
    pattern = rf'"((\d+)_(\d+)_(\d+)-{re.escape(part)}_[^"]*\.pldm\.fwpkg)"'
    matches = re.findall(pattern, html)
    # Deduplicate (Apache listings sometimes duplicate entries)
    seen = set()
    result = []
    for filename, major, minor, build in matches:
        if filename not in seen:
            seen.add(filename)
            version = f"{major}.{minor}.{build}"
            result.append((filename, version))
    result.sort(key=lambda x: tuple(int(n) for n in x[1].split(".")))
    return result


# Cache NVIDIA compat pages to avoid repeated fetches
_nvidia_compat_cache: dict = {}


def check_nvidia_compat(version: str) -> dict:
    """
    Fetch NVIDIA firmware compatibility page for the given version and return
    a dict with keys 'mlnx_ofed' (list) and 'doca_host' (list).

    URL: https://docs.nvidia.com/networking/display/connectx6lxfirmwarev{VER}/firmware+compatible+products
    where VER = version with dots removed (e.g. 26.43.1014 -> 26431014)

    Two table formats exist:
      - Old (<=26.43.x): one row with label "MLNX_OFED / DOCA-HOST" containing OFED versions (24.10-x.x.x.x)
      - New (>=26.44.x): separate rows "MLNX_OFED" and "DOCA-HOST" with their own version lists
    """
    if version in _nvidia_compat_cache:
        return _nvidia_compat_cache[version]

    ver_nodots = version.replace(".", "")
    url = NVIDIA_COMPAT_URL.format(ver=ver_nodots)
    result = {"mlnx_ofed": [], "doca_host": [], "url": url}

    try:
        from bs4 import BeautifulSoup

        resp = requests.get(url, timeout=20)
        if resp.status_code != 200:
            _nvidia_compat_cache[version] = result
            return result

        soup = BeautifulSoup(resp.text, "html.parser")

        # Walk all table rows; look for rows where first cell matches a known driver label
        for row in soup.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) < 2:
                continue
            label = cells[0].get_text(strip=True)
            value = cells[1].get_text(separator=" ", strip=True)
            # Strip trailing "Note:..." footnote
            value = re.split(r'\s*Note:', value)[0].strip()
            versions = [v.strip() for v in value.split("/") if v.strip()]

            if label == "MLNX_OFED / DOCA-HOST":
                # Old format: all are OFED-style versions (e.g. 24.10-0.7.0.0)
                result["mlnx_ofed"] = [v for v in versions if re.match(r'\d+\.\d{2}-', v)]
            elif label == "MLNX_OFED":
                result["mlnx_ofed"] = [v for v in versions if re.match(r'\d+\.\d{2}-', v)]
            elif label == "DOCA-HOST":
                # New format: DOCA versions (e.g. 2.9.1)
                result["doca_host"] = [v for v in versions if re.match(r'^\d+\.\d+', v)
                                       and not re.match(r'\d+\.\d{2}-', v)]

    except Exception:
        pass

    _nvidia_compat_cache[version] = result
    return result


def find_nic_firmware_for_drivers(
    repo_url: str,
    part: str,
    target_mlnx_ofed: Optional[str],
    target_doca: Optional[str],
) -> List[NicFirmwareInfo]:
    """
    Given target MLNX_OFED and DOCA-HOST versions, find the highest HPE NIC
    firmware version that is certified with each.

    Returns a list with up to two NicFirmwareInfo entries (legacy + doca).
    """
    firmwares = get_nic_firmwares(repo_url, part)
    if not firmwares:
        return []

    legacy_result = None
    doca_result = None

    # Check from newest to oldest, stop as soon as we find a match for each type
    for filename, version in reversed(firmwares):
        if legacy_result and doca_result:
            break

        compat = check_nvidia_compat(version)
        print(f"    Checking NIC {version}: MLNX_OFED={compat['mlnx_ofed']} DOCA={compat['doca_host']}", file=sys.stderr)

        # Legacy match: target MLNX_OFED must appear in the certified list
        if not legacy_result and target_mlnx_ofed:
            for certified in compat["mlnx_ofed"]:
                if target_mlnx_ofed in certified or certified in target_mlnx_ofed:
                    legacy_result = NicFirmwareInfo(
                        part=part,
                        filename=filename,
                        version=version,
                        driver_type="legacy",
                        os="ubuntu22",
                        mlnx_ofed=certified,
                    )
                    break

        # DOCA match: target DOCA-HOST must appear in the certified list
        if not doca_result and target_doca:
            for certified in compat["doca_host"]:
                # Match on major.minor (e.g. 2.9.x matches 2.9.1)
                target_major_minor = ".".join(target_doca.split(".")[:2])
                cert_major_minor = ".".join(certified.split(".")[:2])
                if target_major_minor == cert_major_minor:
                    doca_result = NicFirmwareInfo(
                        part=part,
                        filename=filename,
                        version=version,
                        driver_type="doca",
                        os="ubuntu24",
                        doca_host=certified,
                    )
                    break

    result = []
    if legacy_result:
        result.append(legacy_result)
    if doca_result:
        result.append(doca_result)
    return result


def query_model(model_key: str, check_nic: bool = False,
                target_mlnx_ofed: Optional[str] = None,
                target_doca: Optional[str] = None) -> FirmwareInfo:
    """Query the SDR repo and return FirmwareInfo for the given model."""
    config = HPE_MODELS[model_key]
    info = FirmwareInfo(
        model=model_key,
        model_name=config["name"],
        generation=config["generation"],
        ilo_type=f"iLO {config['ilo_gen']}",
    )
    try:
        ilo_file, ilo_ver, ilo_date = get_latest_ilo(config["repo_url"], config["ilo_gen"])
        info.ilo_filename = ilo_file
        info.ilo_version = ilo_ver
        info.ilo_date = ilo_date

        rom_file, rom_ver, rom_date = get_latest_rom(config["repo_url"], config["rom_code"])
        info.rom_filename = rom_file
        info.rom_version = rom_ver
        info.rom_date = rom_date

        if check_nic and config.get("nic_part"):
            part = config["nic_part"]
            print(f"  Checking NIC firmware for {part}...", file=sys.stderr)
            info.nic = find_nic_firmware_for_drivers(
                config["repo_url"], part, target_mlnx_ofed, target_doca
            )
    except Exception as e:
        info.error = str(e)
    return info


def download_file(url: str, dest: Path) -> bool:
    """Download a file from url to dest. Returns True on success."""
    if dest.exists():
        print(f"  ⏭  Already exists: {dest.name}", file=sys.stderr)
        return True
    print(f"  📥 Downloading {dest.name} ...", file=sys.stderr)
    try:
        with requests.get(url, stream=True, timeout=120) as r:
            r.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    f.write(chunk)
        size_mb = dest.stat().st_size / (1024 * 1024)
        print(f"  ✅ {dest.name} ({size_mb:.1f} MB)", file=sys.stderr)
        return True
    except Exception as e:
        print(f"  ❌ Failed: {e}", file=sys.stderr)
        if dest.exists():
            dest.unlink()
        return False


def download_firmware(info: FirmwareInfo, download_dir: Path, include_nic: bool = False):
    """Download iLO, System ROM and optionally NIC firmware files to download_dir."""
    config = HPE_MODELS[info.model]
    repo_url = config["repo_url"]

    if info.ilo_filename:
        download_file(f"{repo_url}{info.ilo_filename}", download_dir / info.ilo_filename)
    if info.rom_filename:
        download_file(f"{repo_url}{info.rom_filename}", download_dir / info.rom_filename)
    if include_nic:
        for nic in info.nic:
            download_file(f"{repo_url}{nic.filename}", download_dir / nic.filename)


def print_text_output(results: List[FirmwareInfo]):
    print("\n" + "=" * 80)
    print("HPE ProLiant Firmware Versions  (source: HPE Linux SDR)")
    print(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    for info in results:
        print(f"\n{info.model_name} ({info.model}) - {info.generation}")
        print("-" * 60)
        if info.error:
            print(f"  Error: {info.error}")
            continue

        if info.ilo_version:
            print(f"  {info.ilo_type}:      {info.ilo_version}  [{info.ilo_filename}]")
            if info.ilo_date:
                print(f"    Date: {info.ilo_date}")
        else:
            print(f"  {info.ilo_type}:      Not found")

        if info.rom_version:
            print(f"  System ROM:  {info.rom_version}  [{info.rom_filename}]")
            if info.rom_date:
                print(f"    Date: {info.rom_date}")
        else:
            print("  System ROM:  Not found")

        if info.nic:
            print(f"  NIC firmware ({info.nic[0].part if info.nic else ''}):")
            for nic in info.nic:
                compat_str = f"MLNX_OFED {nic.mlnx_ofed}" if nic.mlnx_ofed else f"DOCA {nic.doca_host}"
                print(f"    [{nic.driver_type}/{nic.os}]  {nic.version}  [{nic.filename}]  (certified: {compat_str})")

    print("\n" + "=" * 80)
    print("Repo URLs:")
    seen = set()
    for info in results:
        url = HPE_MODELS[info.model]["repo_url"]
        if url not in seen:
            print(f"  {url}")
            seen.add(url)
    print("=" * 80)


def print_json_output(results: List[FirmwareInfo]):
    output = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "models": [asdict(info) for info in results],
    }
    print(json.dumps(output, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Check latest HPE ProLiant firmware versions from HPE Linux SDR"
    )
    parser.add_argument("--model", "-m", choices=list(HPE_MODELS.keys()),
                        action="append",
                        help="Server model(s) to query (can repeat)")
    parser.add_argument("--all", "-a", action="store_true",
                        help="Query all supported models")
    parser.add_argument("--format", "-f", choices=["text", "json"], default="text",
                        help="Output format (default: text)")
    parser.add_argument("--list-models", "-l", action="store_true",
                        help="List supported models and exit")
    parser.add_argument("--download", "-d", action="store_true",
                        help="Download firmware files after querying")
    parser.add_argument("--download-dir", default=".",
                        help="Directory to save downloaded files (default: current dir)")
    parser.add_argument("--nic", action="store_true",
                        help="Also find NIC firmware (requires --target-mlnx-ofed and/or --target-doca)")
    parser.add_argument("--target-mlnx-ofed",
                        help="Target MLNX_OFED version for NIC firmware selection (e.g. 24.10-2.1.8.0 ubuntu24, 23.10-0.5.5.0 ubuntu22)")
    parser.add_argument("--target-doca",
                        help="Target DOCA-HOST version for NIC firmware selection (e.g. 2.9.3)")
    parser.add_argument("--ci-config",
                        help="Path to caas-image-builder .gitlab-ci.yml (auto-reads OFED/DOCA targets). "
                             "Also reads from CAAS_IMAGE_BUILDER_PATH env var.")

    args = parser.parse_args()

    if args.list_models:
        print("Supported models:")
        for key, cfg in HPE_MODELS.items():
            nic = cfg.get("nic_part") or "none"
            print(f"  {key:18} - {cfg['name']} (iLO {cfg['ilo_gen']}, ROM: {cfg['rom_code']}, NIC: {nic})")
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

    models_to_query = list(HPE_MODELS.keys()) if args.all else args.model

    results = []
    for model in models_to_query:
        print(f"Querying {model}...", file=sys.stderr)
        results.append(query_model(
            model,
            check_nic=args.nic,
            target_mlnx_ofed=target_mlnx_ofed,
            target_doca=target_doca,
        ))

    if args.format == "json":
        print_json_output(results)
    else:
        print_text_output(results)

    if args.download:
        download_dir = Path(args.download_dir)
        download_dir.mkdir(parents=True, exist_ok=True)
        print(f"\nDownloading to: {download_dir}", file=sys.stderr)
        for info in results:
            if not info.error:
                print(f"\n[{info.model}]", file=sys.stderr)
                download_firmware(info, download_dir, include_nic=args.nic)


if __name__ == "__main__":
    main()
