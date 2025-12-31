# coding=utf-8


def hash_dict(d):
    items = sorted(d.items())
    hashable_items = tuple((k, hash_recursive(v)) if v else (k, '') for k, v in items)

    return hashable_items


def hash_recursive(obj):
    # 递归处理字典中的各种数据类型
    if isinstance(obj, dict):
        return hash_dict(obj)
    elif isinstance(obj, (list, tuple)):
        return tuple(hash_recursive(item) for item in obj)
    elif isinstance(obj, int):
        return obj
    elif isinstance(obj, str):
        return hash(obj)
    elif isinstance(obj, long):
        return obj
    else:
        # 其他数据类型可能需要根据需要添加相应的处理逻辑
        raise TypeError("Unsupported type: " + str(type(obj)))
