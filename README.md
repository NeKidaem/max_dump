# max_dump

Extract file properties from 3ds max file.

Example:

    $ python extract.py 02-test_frame_stamp.max

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
        "Mesh Totals": {
            "count": 2,
            "items": [
                "Vertices: 507",
                "Faces: 992"
            ]
        },
        "Scene Totals": {
            "count": 7,
            "items": [
                "Objects: 2",
                "Shapes: 0",
                "Lights: 1",
                "Cameras: 0",
                "Helpers: 0",
                "Space Warps: 0",
                "Total: 3"
            ]
        },
        "External Dependencies": {
            "count": 1,
            "items": [
                "bark5.jpg"
            ]
        },
        "Objects": {
            "count": 3,
            "items": [
                "Sphere001",
                "VRayLight001",
                "Plane001"
            ]
        },
        "Materials": {
            "count": 2,
            "items": [
                "Default",
                "Default2"
            ]
        },
        "Used Plug-Ins": {
            "count": 20,
            "items": [
                "viewportmanager.gup",
                "mrmaterialattribs.gup",
                "custattribcontainer.dlo",
                "mtl.dlt",
                "vrender2015.dlr",
                "mtlgen.dlt",
                "prosound.dlc",
                "ctrl.dlc",
                "prim.dlo",
                "dllights.dlo",
                "rend.dlr",
                "kernel.dlk",
                "acadblocks.dlu",
                "instancemgr.dlu",
                "reactor.dlc",
                "parameditor.gup",
                "biped.dlc",
                "sceneeffectloader.dlu",
                "bitmapproxies.dlu",
                "storageandfilter.bms"
            ]
        },
        "Render Data": {
            "count": 15,
            "items": [
                "User Name=JohnDoe",
                "Computer Name=DESKTOP-KTGFBKA",
                "Render Width=1024",
                "Render Height=768",
                "Render Aspect=1.00",
                "Renderer ClassIDA=1941615238",
                "Renderer ClassIDB=2012806412",
                "Renderer Name=V-Ray Adv 3.00.08",
                "Render Output=C:\\Users\\Vadim\\Desktop\\tmp\\2016.png",
                "Render Output Gamma=2.20",
                "Animation Start=0",
                "Animation End=0",
                "Render Flags=32",
                "Scene Flags=57032",
                "RenderElements=0"
            ]
        }
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
