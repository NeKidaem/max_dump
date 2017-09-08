import argparse
import json

import attr

from max_dump.file_props_parser import extract_file_props
from max_dump.storage_parser import storage_parse, EnumEncoder


STREAM_NAMES = ('ClassData', 'ClassDirectory3', 'Config', 'DllDirectory',
                'FileAssetMetaData3', 'SaveConfigData', 'Scene',
                'ScriptedCustAttribDefs', 'VideoPostQueue')


def dumps(c):
    d = attr.asdict(c)
    s = json.dumps(d, indent=4, cls=EnumEncoder)
    return s


def main():
    parser = argparse.ArgumentParser(
            description='Extract info from a max file'
    )
    parser.add_argument('max_fname')
    help = "Parse chunk-based stream"
    parser.add_argument('-s', '--parse-stream', choices=STREAM_NAMES,
                        metavar='STREAM_NAME', help=help)
    args = parser.parse_args()

    if args.parse_stream:
        stream_name = args.parse_stream
        c = storage_parse(args.max_fname, stream_name)
        print(dumps(c))
    else:
        props = extract_file_props(args.max_fname)
        out = json.dumps(props, indent=4)
        print(out)


if __name__ == "__main__":
    main()
