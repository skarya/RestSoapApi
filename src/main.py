"""
main.py
CLI entry point for the API Automation Framework.

Usage:
    python src/main.py <input_file> [--parallel]

Examples:
    python src/main.py data/input/TestSuite_REST.json
    python src/main.py data/input/TestSuite_SOAP.xlsx --parallel
    ApiAutomation.exe data\\input\\TestSuite_REST.xlsx --parallel
"""
import argparse
import os
import sys
from datetime import datetime

# ── Path fix for PyInstaller ──────────────────────────────────────────────────
# When running as a bundled .exe, sys.path may not include src/
_script_dir = os.path.dirname(os.path.abspath(__file__))
_root_dir   = os.path.dirname(_script_dir)
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)

from src.file_detector  import detect
from src.input_parser   import parse_file
from src.executor       import run
from src.reporter       import generate_report


BANNER = """
╔══════════════════════════════════════════════════════╗
║       🚀  API AUTOMATION FRAMEWORK  🚀               ║
║           REST & SOAP  |  Python Edition             ║
╚══════════════════════════════════════════════════════╝
"""


def _output_path(input_files: list) -> str:
    """Generate timestamped output path under data/output/."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if len(input_files) == 1:
        base_name = os.path.splitext(os.path.basename(input_files[0]))[0]
    else:
        base_name = f"Consolidated_{len(input_files)}_Suites"

    if hasattr(sys, "_MEIPASS"):
        # PyInstaller EXE mode — output next to the executable
        output_dir = os.path.join(os.path.dirname(sys.executable), "data", "output")
    else:
        output_dir = os.path.join(_root_dir, "data", "output")

    os.makedirs(output_dir, exist_ok=True)
    return os.path.join(output_dir, f"report_{base_name}_{timestamp}.xlsx")


def _print_summary_table(results: list):
    """Print a clean ASCII summary table to the console."""
    print("\n" + "─" * 70)
    print(f"  {'#':<4} {'Test Case ID':<22} {'Type':<6} {'Method':<8} {'Code':<6} {'Time(ms)':<10} {'Status'}")
    print("─" * 70)
    for idx, r in enumerate(results, start=1):
        pf = r.get("pass_fail", "ERROR")
        pf_display = "✅ PASS" if pf == "PASS" else ("❌ FAIL" if pf == "FAIL" else "⚠️ ERROR")
        print(
            f"  {idx:<4} "
            f"{str(r.get('testcaseid','')):<22} "
            f"{str(r.get('api_type','')):<6} "
            f"{str(r.get('method','')):<8} "
            f"{str(r.get('status_code','')):<6} "
            f"{str(r.get('response_time_ms','')):<10} "
            f"{pf_display}"
        )
    print("─" * 70)


def main():
    print(BANNER)

    # ── Argument parsing ──────────────────────────────────────────────────────
    parser = argparse.ArgumentParser(
        description="API Automation Framework — REST & SOAP test runner",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "input_files",
        nargs="+",
        help=(
            "One or more paths to input files.\n"
            "  Must contain '_REST' or '_SOAP' in the filename.\n"
            "  Supported formats: .json, .xlsx, .xls\n"
            "  Example: file1_REST.json file2_SOAP.xlsx"
        ),
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        default=False,
        help="Run all requests concurrently (parallel mode). Default: serial.",
    )
    args = parser.parse_args()

    input_files = [os.path.abspath(f) for f in args.input_files]
    parallel    = args.parallel
    mode_label  = "Parallel" if parallel else "Serial"

    all_test_cases = []
    
    print(f"  Mode        : {mode_label}")
    print(f"  Input Files : {len(input_files)}")
    print()

    # ── Process each file ────────────────────────────────────────────────────
    for input_file in input_files:
        if not os.path.isfile(input_file):
            print(f"❌ ERROR: Input file not found: {input_file}")
            continue

        try:
            metadata = detect(input_file)
            print(f"  Parsing '{os.path.basename(input_file)}' ({metadata['api_type']})...")
            test_cases = parse_file(input_file, metadata["api_type"])
            all_test_cases.extend(test_cases)
        except Exception as e:
            print(f"❌ ERROR processing '{input_file}': {e}")

    if not all_test_cases:
        print("⚠️  No test cases found in any input file. Exiting.")
        sys.exit(0)

    print(f"\n  Total test cases found: {len(all_test_cases)}")

    # ── Execute ───────────────────────────────────────────────────────────────
    start_time = datetime.now()
    results = run(all_test_cases, parallel=parallel)
    end_time = datetime.now()

    # ── Print summary table ───────────────────────────────────────────────────
    _print_summary_table(results)

    total   = len(results)
    passed  = sum(1 for r in results if r.get("pass_fail") == "PASS")
    failed  = sum(1 for r in results if r.get("pass_fail") == "FAIL")
    errors  = sum(1 for r in results if r.get("pass_fail") == "ERROR")
    duration = (end_time - start_time).total_seconds()

    print(f"\n  Results : {passed} PASSED  |  {failed} FAILED  |  {errors} ERRORS  |  Total: {total}")
    print(f"  Duration: {duration:.2f}s\n")

    # ── Generate report ───────────────────────────────────────────────────────
    output_path = _output_path(input_files)
    print("  Generating Consolidated Excel report...")
    try:
        saved_path = generate_report(
            results    = results,
            input_file = input_files[0] if len(input_files) == 1 else "Consolidated_Suites",
            mode       = mode_label,
            output_path= output_path,
            start_time = start_time,
            end_time   = end_time,
        )
        print(f"\n  ✅ Report saved to:\n     {saved_path}\n")
    except Exception as e:
        print(f"❌ ERROR generating report: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
