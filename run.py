import argparse
import json

import attr
import hexdump

import max_dump
from max_dump.file_props_parser import extract_file_props
from max_dump.storage_parser import storage_parse, read_stream
from max_dump.class_frontend import terse_class
from max_dump.dll_frontend import terse_dll
from max_dump.scene_frontend import link_scene_and_class
from max_dump.dump_cameras import dump_cameras


STREAM_NAMES = ('ClassData', 'ClassDirectory3', 'Config', 'DllDirectory',
                'FileAssetMetaData3', 'SaveConfigData', 'Scene',
                'ScriptedCustAttribDefs', 'VideoPostQueue')


def dumps(c):
    return json.dumps(c, indent=4, ensure_ascii=False)


def dump_stream(max_fname, stream_name):
    """Print contents of the stream as hex string.
    """
    ba = read_stream(max_fname, stream_name)
    print(hexdump.dump(ba))


def parse_stream(max_fname, stream_name):
    c = storage_parse(max_fname, stream_name)
    if stream_name == "DllDirectory":
        c = terse_dll(c)
    elif stream_name == "ClassDirectory3":
        c = terse_class(c)
    elif stream_name == "Scene":
        class_data = storage_parse(max_fname, "ClassDirectory3")
        c = link_scene_and_class(c, class_data, tersed=False)
    print(dumps(c))


def main():
    parser = argparse.ArgumentParser(
            description='List cameras in the max file'
    )
    parser.add_argument('max_fname')
    help = "Print file properties"
    parser.add_argument('--props', action="store_true", help=help)
    help = "Parse chunk-based stream"
    parser.add_argument('--parse-stream', choices=STREAM_NAMES,
                        metavar='STREAM_NAME', help=help)
    help = "Print contents of the stream as hex string"
    parser.add_argument('--dump-stream', choices=STREAM_NAMES,
                        metavar='STREAM_NAME', help=help)
    args = parser.parse_args()

    if args.parse_stream:
        parse_stream(args.max_fname, args.parse_stream)
    elif args.dump_stream:
        dump_stream(args.max_fname, args.dump_stream)
    elif args.props:
        props = extract_file_props(args.max_fname)
        out = json.dumps(props, indent=4)
        print(out)
    else:
        cams = dump_cameras(args.max_fname)
        print(dumps(cams))


if __name__ == "__main__":
    main()
