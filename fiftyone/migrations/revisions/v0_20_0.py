"""
FiftyOne v0.20.0 revision.

| Copyright 2017-2023, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""


def up(db, dataset_name):
    match_d = {"name": dataset_name}
    dataset_dict = db.datasets.find_one(match_d)

    app_config = dataset_dict.get("app_config", None)
    if app_config is not None:
        sidebar_groups = app_config.get("sidebar_groups", None)
        if sidebar_groups is not None:
            for sidebar_group in sidebar_groups:
                name = sidebar_group.get("name", None)
                if name == "tags":
                    sidebar_group.setdefault("paths", ["tags", "_label_tags"])
                if name == "label tags":
                    sidebar_groups.remove(sidebar_group)

    db.datasets.replace_one(match_d, dataset_dict)


def down(db, dataset_name):
    match_d = {"name": dataset_name}
    dataset_dict = db.datasets.find_one(match_d)

    app_config = dataset_dict.get("app_config", None)
    if app_config is not None:
        sidebar_groups = app_config.get("sidebar_groups", None)
        if sidebar_groups is not None:
            for sidebar_group in sidebar_groups:
                name = sidebar_group.get("name", None)
                if name == "tags":
                    sidebar_group["paths"] = []
            sidebar_groups.append({"name": "label tags", "paths": []})

    db.datasets.replace_one(match_d, dataset_dict)
