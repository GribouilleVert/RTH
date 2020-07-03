import argparse
from stock.yml_adapter import YAMLAdapter
from stock.adapters import JSONAdapter
from rtg.core.errors import WrongFileFormat


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="the file path which will be decoded")
    parser.add_argument("-R", "--readable", help="outputs in readable format instead of returning raw data",
                        action="store_false")

    args = parser.parse_args()

    ext = args.file.split('.')[-1]

    if ext not in ['yml', 'json']:
        raise WrongFileFormat(ext)

    adapter = None
    if ext == 'yml':
        adapter = YAMLAdapter(args.file)
    elif ext == 'json':
        adapter = JSONAdapter(args.file)

    net_instance = adapter()
    result = net_instance.__calculate_routing_tables(raw=args.readable)
    if args.readable is True:
        print(result)


if __name__ == '__main__':
    main()
