from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .config import DEFAULT_CONFIG_NAME, load_settings, write_default
from .processor import process_pair
from .tokenizer import generate_key, save_key


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sheetveil", description="Local deterministic tokenization of before-and-after Excel workbook pairs.")
    parser.add_argument("--version", action="version", version="SheetVeil 1.0.0")
    subs = parser.add_subparsers(dest="command", required=True)

    subs.add_parser("ui", help="Open the English desktop UI.")

    run = subs.add_parser("run", help="Tokenize a before-and-after workbook pair.")
    run.add_argument("--before", required=True, help="Path to the original input workbook.")
    run.add_argument("--after", required=True, help="Path to the manually produced output workbook.")
    run.add_argument("--output", required=True, help="Output directory for the shareable package.")
    run.add_argument("--config", help="Path to a SheetVeil JSON config.")
    run.add_argument("--force", action="store_true", help="Replace existing output files and saved key.")
    key_group = run.add_mutually_exclusive_group()
    key_group.add_argument("--key-file", help="Reuse an existing local key for stable tokens across runs.")
    key_group.add_argument("--save-key", help="Save the newly generated key to this path. Keep it private.")

    config = subs.add_parser("config", help="Create, show, or validate configuration.")
    config_subs = config.add_subparsers(dest="config_command", required=True)
    init = config_subs.add_parser("init", help="Write a default JSON configuration.")
    init.add_argument("--path", default=DEFAULT_CONFIG_NAME)
    init.add_argument("--force", action="store_true")
    show = config_subs.add_parser("show", help="Show effective configuration.")
    show.add_argument("--path")
    validate = config_subs.add_parser("validate", help="Validate a configuration file.")
    validate.add_argument("--path", required=True)

    key = subs.add_parser("keygen", help="Generate a reusable 256-bit local project key.")
    key.add_argument("--output", required=True)
    key.add_argument("--force", action="store_true")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "ui":
            try:
                from .ui import launch_ui
            except ImportError as exc:
                raise RuntimeError("The desktop UI requires Tkinter. On Linux, install the python3-tk package. The run and config commands work without Tkinter.") from exc
            try:
                launch_ui()
            except RuntimeError as exc:
                raise RuntimeError(f"{exc} The run and config commands work without a desktop display.") from exc
        elif args.command == "run":
            settings = load_settings(args.config)
            report = process_pair(args.before, args.after, settings=settings, output_dir=args.output,
                                  key_file=args.key_file, save_generated_key=args.save_key, force=args.force)
            print(json.dumps(report, indent=2))
        elif args.command == "config":
            if args.config_command == "init":
                print(write_default(args.path, args.force))
            elif args.config_command == "show":
                print(json.dumps(vars(load_settings(args.path)), indent=2))
            elif args.config_command == "validate":
                load_settings(args.path)
                print(f"Valid configuration: {args.path}")
        elif args.command == "keygen":
            path = Path(args.output)
            if path.exists() and not args.force:
                raise FileExistsError(f"Key already exists: {path}. Use --force to overwrite.")
            save_key(path, generate_key())
            print(f"Private key written to: {path}")
        return 0
    except Exception as exc:  # noqa: BLE001 - CLI boundary must report user-facing failures.
        print(f"SheetVeil error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
