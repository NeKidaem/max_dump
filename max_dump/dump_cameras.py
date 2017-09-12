import io
from struct import unpack, pack

from max_dump.storage_parser import storage_parse
from max_dump.class_frontend import terse_class
from max_dump.scene_frontend import link_scene_and_class, add_idx_to_childs
from max_dump.utils import index_by, group_by, INT_S

# super class id of all cameras
CAMERA_SUPER_CLASS_ID = '0x20'


def dump_cameras(max_fname):
    """Найти все камеры в данном макс файле.

    Найти все объекты Node, которые ссылаются на объекты камер.
    Собрать и вернуть имена этих объектов.
    """
    class_list = terse_class(storage_parse(max_fname, "ClassDirectory3"))
    scene = get_scene(max_fname, class_list)
    cameras_objs = get_scene_cameras(scene, class_list)
    cameras_indicies = index_by(cameras_objs, "self_idx")

    names = []
    name_to_class = index_by(class_list, "name")
    node_idx = name_to_class["Node"]["idx"]
    idn_to_scene_objects = group_by(scene[0]["childs"], "header__idn")
    for node_obj in idn_to_scene_objects[node_idx]:
        for ref in get_node_refs(node_obj):
            if ref in cameras_indicies:
                names.append(get_node_object_name(node_obj))
    return names


def get_node_object_name(node):
    idn_to_child = index_by(node["childs"], "header__idn")
    name_idn = "0x962"
    assert name_idn in idn_to_child, ("The node does not have "
                                      "a child with needed identifier")
    obj_name = idn_to_child[name_idn]["parsed"]
    return obj_name


def get_scene_cameras(scene, class_list):
    """Return list of camera objects from the scene.
    """
    camera_classes = [x for x in class_list
                      if x["super_class_id"] == CAMERA_SUPER_CLASS_ID]
    idn_to_scene_objects = group_by(scene[0]["childs"], "header__idn")
    camera_objects = []
    for camera_class in camera_classes:
        camera_class_objects = idn_to_scene_objects[camera_class["idx"]]
        camera_objects.extend(camera_class_objects)
    return camera_objects


def get_node_refs(node):
    """Return node references.

    A Node usually contains a chunk with indexes to other objects in the Scene
    stream. The objects look like childs of the Node.
    """
    idn_to_child = index_by(node["childs"], "header__idn")
    ref_idn = "0x2035"
    assert ref_idn in idn_to_child, ("The node does not have "
                                     "a child with needed identifier")
    refs_hex = bytes.fromhex(idn_to_child[ref_idn]["hex_spaced"])
    refs_hex_io = io.BytesIO(refs_hex)
    refs = []
    while True:
        b = refs_hex_io.read(INT_S)
        if not b:
            break
        i, = unpack('i', b)
        refs.append(i)
    return refs


def get_scene(max_fname, class_list):
    scene = storage_parse(max_fname, "Scene")
    scene = link_scene_and_class(scene, class_list)
    add_idx_to_childs(scene)
    return scene
