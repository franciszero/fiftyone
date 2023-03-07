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
            label_tags_idx = None

            for idx, sidebar_group in enumerate(sidebar_groups):
                name = sidebar_group.get("name", None)
                if name == "tags":
                    sidebar_group["paths"] = ["tags", "_label_tags"]

                if name == "label tags":
                    label_tags_idx = idx

            if label_tags_idx is not None:
                sidebar_groups.pop(label_tags_idx)

    db.datasets.replace_one(match_d, dataset_dict)


def down(db, dataset_name):
    match_d = {"name": dataset_name}
    dataset_dict = db.datasets.find_one(match_d)

    app_config = dataset_dict.get("app_config", None)
    if app_config is not None:
        sidebar_groups = app_config.get("sidebar_groups", None)
        if sidebar_groups is not None:
            tags_idx = None
            found_label_tags = False

            for idx, sidebar_group in enumerate(sidebar_groups):
                name = sidebar_group.get("name", None)

                if name == "tags":
                    sidebar_group["paths"] = []
                    tags_idx = idx

                if name == "label tags":
                    sidebar_group["paths"] = []
                    found_label_tags = True

            if tags_idx is not None and not found_label_tags:
                sidebar_groups.insert(
                    tags_idx + 1,
                    {"name": "label tags", "paths": []},
                )

    db.datasets.replace_one(match_d, dataset_dict)
