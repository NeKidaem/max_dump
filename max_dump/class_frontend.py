"""Make ClassDirectory3 data less verbose.
"""


def terse_class(class_data):
    brief_data = []
    idx = 0
    for class_entry in class_data:
        brief_entry = {"idx": hex(idx)}
        brief_entry.update(class_entry["childs"][0]["parsed"])
        brief_entry["dll_index_hex"] = hex(brief_entry["dll_index"])
        brief_entry["name"] = class_entry["childs"][1]["parsed"]
        brief_data.append(brief_entry)
        idx += 1
    return brief_data
