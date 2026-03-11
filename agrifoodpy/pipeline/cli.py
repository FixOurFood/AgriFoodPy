import argparse
import json
from .pipeline import Pipeline


def main():
    parser = argparse.ArgumentParser(
        description="Run an AgriFoodPy pipeline from a configuration file."
    )

    parser.add_argument(
        "config",
        help="Pipeline configuration YAML file"
    )

    parser.add_argument(
        "--output",
        help="Optional output file to store the datablock as JSON",
        default=None
    )

    parser.add_argument(
        "--show-datablock",
        action="store_true",
        help="Print the final datablock to stdout"
    )


    parser.add_argument(
        "--show-nodes",
        action="store_true",
        help="Print the final datablock to stdout"
    )

    parser.add_argument(
        "--norun",
        action="store_true",
        help="Do not run the pipeline"
    )

    args = parser.parse_args()

    pipeline = Pipeline.read(args.config)

    if args.show_nodes:
        pipeline.print_nodes()

    if not args.norun:
        pipeline.run()

    datablock = pipeline.datablock

    if args.show_datablock:
        print(json.dumps(datablock, indent=2, default=str))

    if args.output:
        with open(args.output, "w") as f:
            json.dump(datablock, f, indent=2, default=str)