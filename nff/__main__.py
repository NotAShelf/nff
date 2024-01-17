import argparse
import os
import sys
import stat


def main():
    parser = argparse.ArgumentParser(description="Process nftables config file.")
    parser.add_argument(
        "-f", "--file", help="nftables config file (e.g: /etc/nftables.conf)"
    )
    parser.add_argument(
        "--indent",
        choices=["tabs", "spaces"],
        default="tabs",
        help="Type of indentation (tabs or spaces)",
    )
    parser.add_argument("--output", default=None, help="Output file")
    parser.add_argument(
        "--optimize",
        action="store_true",
        help="Optimize output by trimming consecutive empty lines into one",
    )
    args = parser.parse_args()

    if len(sys.argv) <= 1:
        print("See --help for usage", file=sys.stderr)
        sys.exit(0)

    try:
        with open(args.file, "r") as f:
            fi = os.stat(args.file)
            if not stat.S_ISREG(fi.st_mode):
                print(f"error: not a regular file: {args.file}", file=sys.stderr)
                sys.exit(1)

            w = []
            lvl = 0
            prev_was_empty = False

            for line in f:
                # remove all spaces
                line = line.strip()

                # skip indent level change
                skip = False

                if "{" in line and "}" in line:
                    # '{' and '}' at the same line, skip
                    skip = True

                if not skip and line.endswith("}"):
                    lvl -= 1

                if args.indent == "spaces":
                    newline = "  " * lvl + line + "\n"
                else:
                    newline = "\t" * lvl + line + "\n"

                if newline.strip() == "" and args.optimize:
                    # empty line
                    if prev_was_empty:
                        continue
                    else:
                        prev_was_empty = True
                        newline = "\n"
                else:
                    prev_was_empty = False

                # write to memory
                w.append(newline)

                if not skip and line.endswith("{"):
                    lvl += 1

            # output memory buffer
            if args.output:
                with open(args.output, "w") as out_file:
                    out_file.write("".join(w))
            else:
                print("".join(w))

    except Exception as err:
        print(f"error: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
