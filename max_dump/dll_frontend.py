"""Make DllDirectory data less verbose.
"""


def terse_dll(dll_data):
    brief_data = []
    idx = 0
    for dll_entry in dll_data:
        if dll_entry["header"]["storage_type_name"] != "DLL_ENTRY":
            continue
        brief_entry = {"idx": hex(idx)}
        brief_entry["description"] = dll_entry["childs"][0]["parsed"]
        brief_entry["dll_name"] = dll_entry["childs"][1]["parsed"]
        brief_data.append(brief_entry)
        idx += 1
    return brief_data

