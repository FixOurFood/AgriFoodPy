import argparse
import json
import sys
from .pipeline import Pipeline


def main(args=None):
    parser = argparse.ArgumentParser(
        description="Run an AgriFoodPy pipeline from a configuration file."
    )

    parser.add_argument(
        "config",
        help="Pipeline configuration YAML file"
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Optional output file to store the datablock as JSON",
        default=None
    )

    parser.add_argument(
        "--nodes",
        action="store_true",
        help="Print the nodes and parameters to stdout"
    )

    parser.add_argument(
        "--no-run",
        action="store_false",
        help="Do not run the pipeline"
    )

    parser.add_argument(
        "--from-node",
        type=int,
        help="Index of the first node to be executed"
    )

    parser.add_argument(
        "--to-node",
        type=int,
        help="Index of the last node to be executed"
    )

    parser.add_argument(
        "--skip-nodes",
        nargs="+",
        type=int,
        help="List of nodes to be skipped in the pipeline execution"
    )

    # get system args if none passed
    if args is None:
        args = sys.argv[1:]

    args = parser.parse_args(args or ['--help'])

    pipeline = Pipeline.read(args.config)

    if args.nodes:
        pipeline.print_nodes()

    from_node = args.from_node if args.from_node is not None else 0
    to_node = args.to_node if args.to_node is not None else len(pipeline.nodes)
    skip_nodes = args.skip_nodes if args.skip_nodes is not None else None

    if args.no_run:
        pipeline.run(from_node=from_node, to_node=to_node, skip=skip_nodes)

    datablock = pipeline.datablock

    if args.output is not None:
        with open(args.output, "w") as f:
            json.dump(datablock, f, indent=2, default=str)

    return 0