from giraffe_orm.cli_utils import resolve_db_instance

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(prog="giraffe_orm")
    parser.add_argument(
        "--app",
        "-A",
        help="Target GiraffeORM instance",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("migrate")

    upgrade_parser = subparsers.add_parser("upgrade")
    upgrade_parser.add_argument("migration_name", help="Migration file name/version.")

    args = parser.parse_args()

    db = resolve_db_instance(args.app)

    if args.command == "migrate":
        db.migrate()
        return

    if args.command == "upgrade":
        db.upgrade(args.migration_name)
        return


if __name__ == "__main__":
    main()
