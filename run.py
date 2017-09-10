import argparse
import json

import attr
import hexdump

from max_dump.file_props_parser import extract_file_props
from max_dump.storage_parser import storage_parse, read_stream


STREAM_NAMES = ('ClassData', 'ClassDirectory3', 'Config', 'DllDirectory',
                'FileAssetMetaData3', 'SaveConfigData', 'Scene',
                'ScriptedCustAttribDefs', 'VideoPostQueue')


def dumps(c):
    return json.dumps(c, indent=4)


def dump_stream(max_fname, stream_name):
    """Print contents of the stream as hex string.
    """
    ba = read_stream(max_fname, stream_name)
    print(hexdump.dump(ba))


def parse_stream(max_fname, stream_name):
    c = storage_parse(max_fname, stream_name)
    print(dumps(c))


def main():
    parser = argparse.ArgumentParser(
            description='Extract info from a max file'
    )
    parser.add_argument('max_fname')
    help = "Parse chunk-based stream"
    parser.add_argument('-p', '--parse-stream', choices=STREAM_NAMES,
                        metavar='STREAM_NAME', help=help)
    help = "Print contents of the stream as hex string"
    parser.add_argument('-d', '--dump-stream', choices=STREAM_NAMES,
                        metavar='STREAM_NAME', help=help)
    args = parser.parse_args()

    if args.parse_stream:
        parse_stream(args.max_fname, args.parse_stream)
    elif args.dump_stream:
        dump_stream(args.max_fname, args.dump_stream)
    else:
        props = extract_file_props(args.max_fname)
        out = json.dumps(props, indent=4)
        print(out)


if __name__ == "__main__":
    main()
