import argparse
import sys
from .dump_config import dump_cluster_config
from .analyze import (
    show_secrets_and_env_vars,
    log_none_values,
    show_verbose_structure,
    check_unused_resources,
)


def main():
    parser = argparse.ArgumentParser(
        description="Kubernetes Configuration Enumeration and Analysis Tool"
    )
    subparsers = parser.add_subparsers(dest="command", help="Subcommands")

    # Dump subcommand
    dump_parser = subparsers.add_parser(
        "dump", help="Dump Kubernetes cluster configuration"
    )
    dump_parser.add_argument("url", help="Kubernetes API URL")
    dump_parser.add_argument(
        "--output", "-o", help="Output file path (default: stdout)"
    )

    # Analyze subcommand
    analyze_parser = subparsers.add_parser(
        "analyze", help="Analyze Kubernetes configuration"
    )
    analyze_subparsers = analyze_parser.add_subparsers(
        dest="analyze_command", help="Analysis subcommands"
    )

    # Secrets and env vars subcommand
    secrets_parser = analyze_subparsers.add_parser(
        "secrets", help="Show secrets and environment variables"
    )
    secrets_parser.add_argument(
        "file", help="Path to the JSON file containing Kubernetes configuration"
    )
    secrets_parser.add_argument(
        "--truncate", type=int, help="Truncate long values to specified length"
    )
    secrets_parser.add_argument(
        "--skip",
        action="append",
        help="Skip values containing this string (case insensitive). Can be used multiple times.",
    )
    secrets_parser.add_argument(
        "--skip-ns",
        action="append",
        help="Skip resources in this namespace. Can be used multiple times.",
    )

    # Log None values subcommand
    none_parser = analyze_subparsers.add_parser(
        "none-values", help="Log instances of None values"
    )
    none_parser.add_argument(
        "file", help="Path to the JSON file containing Kubernetes configuration"
    )

    # Verbose structure subcommand
    verbose_parser = analyze_subparsers.add_parser(
        "verbose", help="Show verbose structure of resources"
    )
    verbose_parser.add_argument(
        "file", help="Path to the JSON file containing Kubernetes configuration"
    )

    # Unused resources subcommand
    unused_parser = analyze_subparsers.add_parser(
        "unused", help="Check for unused Secrets or ConfigMaps"
    )
    unused_parser.add_argument(
        "file", help="Path to the JSON file containing Kubernetes configuration"
    )

    args = parser.parse_args()

    if args.command == "dump":
        config_json = dump_cluster_config(args.url)
        if args.output:
            with open(args.output, "w") as f:
                f.write(config_json)
            print(f"Configuration dumped to {args.output}")
        else:
            print(config_json)
    elif args.command == "analyze":
        if args.analyze_command == "secrets":
            show_secrets_and_env_vars(args.file, args.truncate, args.skip, args.skip_ns)
        elif args.analyze_command == "none-values":
            log_none_values(args.file)
        elif args.analyze_command == "verbose":
            show_verbose_structure(args.file)
        elif args.analyze_command == "unused":
            check_unused_resources(args.file)
        else:
            analyze_parser.print_help()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
