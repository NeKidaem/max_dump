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
