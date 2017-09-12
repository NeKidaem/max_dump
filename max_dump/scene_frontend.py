"""Link together data from ClassDirectory3 and Scene.

Add class name to header of a scene entry.
"""

from .class_frontend import terse_class


def link_scene_and_class(scene_data, class_data, tersed=True):
    if not tersed:
        class_data = terse_class(class_data)
    idx_to_class = {x["idx"]: x for x in class_data}
    for scene_entry in scene_data[0]["childs"]:
        # An identifier `idn' is a index of the class in ClassDirectory3.
        idx = scene_entry["header"]["idn"]
        scene_entry["header"]["class_name"] = idx_to_class[idx]["name"]
    return scene_data


def add_idx_to_childs(scene_data):
	self_idx = 0
	for child in scene_data[0]["childs"]:
		child["self_idx"] = self_idx
		child["self_idx_hex"] = hex(self_idx)
		self_idx += 1
	return scene_data
