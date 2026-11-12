import argparse
import logging
import sys

from ocr_eval.config import load_config
from ocr_eval.report import write_reports
from ocr_eval.runner import run


def _print_report(report: dict, path, was_cached: bool) -> None:
    ds = report["dataset"]
    print(
        f"\n{report['name']} / {ds['name']} [{ds['split']}]: "
        f"{report['n_evaluated']} samples, {report['n_errors']} errors"
    )
    for k, v in report["summary"].items():
        print(f"  {k}: {v:.4f}")
    prof = report["profiling"]
    if prof:
        print(
            f"  inference: mean {prof['inference_s_mean']:.2f}s, p50 {prof['inference_s_p50']:.2f}s,"
            f" p90 {prof['inference_s_p90']:.2f}s, p95 {prof['inference_s_p95']:.2f}s,"
            f" p99 {prof['inference_s_p99']:.2f}s, {prof['s_per_megapixel']:.2f}s/MP"
        )
        for label, b in prof["by_image_size"].items():
            print(f"    {label}: {b['inference_s_mean']:.2f}s (n={b['n']})")
        if "energy_kwh_total" in prof:
            print(
                f"  energy: {prof['energy_kwh_total']:.6f} kWh, "
                f"{prof['emissions_kg_total']:.6f} kgCO2eq"
            )
    if was_cached:
        print(f"  unchanged since {report['created_at']}: not re-run (use --force)")
    print(f"  report: {path}/README.md")
    for failure in report["failures"]:
        print(f"  FAIL: {failure}", file=sys.stderr)


# 0 = all datasets pass, 2 = a threshold was violated (reports are still written), 1 = crash.
EXIT_THRESHOLD = 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ocr-eval")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("run", help="Run an evaluation from a YAML config")
    p.add_argument("config")
    p.add_argument(
        "--output-dir",
        default="reports_local",
        help="Where reports go. `reports/` is the versioned copy written by CI, not by local runs.",
    )
    p.add_argument("--force", action="store_true", help="Re-run even if nothing changed")
    p.add_argument("--max-samples", type=int, help="Override max_samples on every dataset")
    pl = sub.add_parser("plan", help="List the CI configs to run (JSON matrix on stdout)")
    pl.add_argument("--changed", nargs="*", default=[], help="Changed files, repo-relative")
    pl.add_argument("--all", action="store_true", help="Select every CI config")
    cp = sub.add_parser("compare", help="Write a side-by-side README with charts from all reports")
    cp.add_argument("reports_dir", nargs="?", default="reports")
    args = parser.parse_args(argv)

    if args.command == "compare":
        from ocr_eval.compare import build

        print(build(args.reports_dir))
        return 0

    if args.command == "plan":
        from pathlib import Path

        from ocr_eval.plan import plan, to_matrix

        selected = plan(Path(__file__).resolve().parents[2], args.changed, args.all)
        print(to_matrix(selected))
        return 0

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    for noisy in ("httpx", "httpcore", "huggingface_hub", "datasets"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    cfg = load_config(args.config)
    if args.max_samples:
        for ds in cfg.datasets:
            ds.max_samples = args.max_samples

    reports = run(cfg, args.output_dir, force=args.force)
    cached = [bool(r.get("_cached")) for r in reports]
    paths = write_reports(reports, args.output_dir)
    for report, path, was_cached in zip(reports, paths, cached):
        _print_report(report, path, was_cached)

    hw = reports[0]["hardware"]
    gpus = ", ".join(g["name"] for g in hw["gpus"]) or "no GPU"
    print(
        f"\nhardware: {hw['cpu_model']} ({hw['cpu_cores_logical']} threads), {gpus}, "
        f"{hw['ram_gb']} GB"
    )
    return 0 if all(r["passed"] for r in reports) else EXIT_THRESHOLD


if __name__ == "__main__":
    sys.exit(main())
