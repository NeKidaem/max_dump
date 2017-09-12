# max_dump

Extract information from a max file.

# Installation


    $ pip install git+https://github.com/nrdhm/max_dump.git


### Examples

List cameras


    $ python run.py max_dump/tests/data/2017_many_cams_and_other_stuff.max


Extract file properties from 3ds max file:


    $ python run.py --props max_dump/tests/data/01-teapot_no_cams_vray.max

    {
        "General": {
            "count": 4,
            "items": [
                "3ds Max Version: 18.00",
                "Uncompressed",
                "Build: 18.0.873.0",
                "Saved As Version: 18.00"
            ]
        },

        ...

        "Render Data": {
            "count": 13,
            "items": [
                "User Name=JohnDoe",
                "Computer Name=DESKTOP-KTGFBKA",
                "Render Width=320",
                "Render Height=240",
                "Render Aspect=1.00",
                "Renderer ClassIDA=1941615238",
                "Renderer ClassIDB=2012806412",
                "Renderer Name=V-Ray Adv 3.00.08",
                "Animation Start=0",
                "Animation End=0",
                "Render Flags=32",
                "Scene Flags=57032",
                "RenderElements=0"
            ]
        }
    }


Parse chunk-based stream:


    $ python run.py max_dump/tests/data/01-teapot_no_cams_vray.max  --parse-stream VideoPostQueue

    {
        "header": null,
        "childs": [
            {
                "header": {
                    "idn": 80,
                    "length": 4,
                    "storage_type": "CStorageValue"
                },
                "value": "01 00 00 00"
            },
            {
                "header": {
                    "idn": 96,
                    "length": 36,
                    "storage_type": "CStorageContainer"
                },
                "childs": [
                    {
                        "header": {
                            "idn": 16,
                            "length": 24,
                            "storage_type": "CStorageValue"
                        },
                        "value": "07 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00 20 12 00 00 00 00 00 00"
                    },
                    {
                        "header": {
                            "idn": 32,
                            "length": 0,
                            "storage_type": "CStorageValue"
                        },
                        "value": ""
                    }
                ]
            }
        ]
    }



# Description

Read file properties from 3ds Max file.

More about properties here:

http://help.autodesk.com/view/3DSMAX/2016/ENU/?guid=__files_GUID_A8663B8E_7E30_474E_B3DB_E21585F125B1_htm

3ds max file is OLE structured storage that contains streams.

List of streams:

    ['\x05DocumentSummaryInformation', '\x05SummaryInformation', 'ClassData', 'ClassDirectory3', 'Config', 'DllDirectory', 'FileAssetMetaData3', 'SaveConfigData', 'Scene', 'ScriptedCustAttribDefs', 'VideoPostQueue']

The script uses a stream named '\x05DocumentSummaryInformation'.

Below are notes on the structure of the stream.

The stream begins with a list of headers

    1E 00 00 00 -- Header delimiter
    08 00 00 00 -- String length
    General
    00          -- Null terminator and padding
    03 00 00 00 -- Some value, may be delimiter
    04 00 00 00 -- Number of properties under the header

    1E 00 00 00
    0C 00 00 00
    Mesh 20 Totals
    00
    03 00 00 00
    02 00 00 00

List of properties starts right after the last header.

    1E 10 00 00             -- Marks the begining of the list
    36 00 00 00             -- Number of properties, double check

    18 00 00 00             -- String length
    3ds Max Version: 18.00  -- Property
    00 00                   -- Null terminator, padded

    10 00 00 00
    Uncompressed
    00 00 00 00

    14 00 00 00
    Build: 18.0.873.0
    00 00 00

    18 00 00 00
    Saved As Version: 18.00
    00
    10 00 00 00

    Vertices: 507
    00 00 00
    0C 00 00 00
    Faces: 992

    ....

    14 00 00 00
    RenderElements=0
    00 00 00 00

    34 00 00 00  -- idk, maybe just a footer
    03 00 00 00
