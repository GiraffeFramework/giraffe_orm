import argparse
import importlib


def main():
    parser = argparse.ArgumentParser(prog="giraffe_orm")
    subparsers = parser.add_subparsers(dest="command", required=True)

    commands = ["migrate", "upgrade"]
    for name in commands:
        mod = importlib.import_module(f"giraffe_orm.commands.{name}")
        subparser = subparsers.add_parser(name)
        mod.add_arguments(subparser)
        subparser.set_defaults(execute=mod.execute)

    args = parser.parse_args()
    args.execute(args)


if __name__ == "__main__":
    main()
