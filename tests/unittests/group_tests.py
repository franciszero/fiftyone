"""
FiftyOne group-related unit tests.

| Copyright 2017-2022, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""
import unittest
import os
import random
import string

import eta.core.utils as etau

import fiftyone as fo
from fiftyone import ViewField as F

from decorators import drop_datasets


class GroupTests(unittest.TestCase):
    @drop_datasets
    def test_add_group_field(self):
        dataset = fo.Dataset()

        self.assertIsNone(dataset.media_type)
        self.assertIsNone(dataset.group_field)
        self.assertIsNone(dataset.default_group_slice)
        self.assertIsNone(dataset.group_slice)

        dataset.add_group_field("group_field", default="ego")

        self.assertEqual(dataset.media_type, "group")
        self.assertEqual(dataset.group_field, "group_field")
        self.assertEqual(dataset.default_group_slice, "ego")
        self.assertEqual(dataset.group_slice, "ego")
        self.assertDictEqual(dataset.group_media_types, {})

    @drop_datasets
    def test_add_implied_group_field(self):
        group = fo.Group()
        samples = [
            fo.Sample(
                filepath="left-image.jpg",
                group_field=group.element("left"),
            ),
            fo.Sample(
                filepath="ego-video.mp4",
                group_field=group.element("ego"),
            ),
            fo.Sample(
                filepath="right-image.jpg",
                group_field=group.element("right"),
            ),
        ]

        dataset = fo.Dataset()
        dataset.add_samples(samples)

        self.assertEqual(dataset.media_type, "group")
        self.assertEqual(dataset.group_field, "group_field")

        self.assertEqual(dataset.group_slice, "left")
        self.assertEqual(dataset.default_group_slice, "left")
        self.assertDictEqual(
            dataset.group_media_types,
            {"left": "image", "ego": "video", "right": "image"},
        )

    @drop_datasets
    def test_basics(self):
        dataset = _make_group_dataset()

        self.assertEqual(dataset.media_type, "group")
        self.assertEqual(dataset.group_slice, "ego")
        self.assertEqual(dataset.default_group_slice, "ego")
        self.assertIn("group_field", dataset.get_field_schema())
        self.assertEqual(len(dataset), 2)

        num_samples = 0
        for sample in dataset:
            num_samples += 1

        self.assertEqual(num_samples, 2)

        num_groups = 0
        for group in dataset.iter_groups():
            self.assertIsInstance(group, dict)
            self.assertIn("left", group)
            self.assertIn("ego", group)
            self.assertIn("right", group)
            num_groups += 1

        self.assertEqual(num_groups, 2)

        sample = dataset.first()

        self.assertEqual(sample.group_field.name, "ego")
        self.assertEqual(sample.media_type, "video")

        group_id = sample.group_field.id
        group = dataset.get_group(group_id)

        self.assertIsInstance(group, dict)
        self.assertIn("left", group)
        self.assertIn("ego", group)
        self.assertIn("right", group)

    @drop_datasets
    def test_field_operations(self):
        dataset = _make_group_dataset()

        self.assertSetEqual(
            set(dataset.group_slices),
            {"left", "right", "ego"},
        )
        self.assertDictEqual(
            dataset.group_media_types,
            {"left": "image", "ego": "video", "right": "image"},
        )
        self.assertEqual(dataset.default_group_slice, "ego")

        dataset.default_group_slice = "left"
        self.assertEqual(dataset.default_group_slice, "left")

        # Datasets may only have one group field
        with self.assertRaises(ValueError):
            dataset.clone_sample_field("group_field", "group_field_copy")

        with self.assertRaises(ValueError):
            dataset.delete_sample_field("group_field")

        dataset.rename_sample_field("group_field", "still_group_field")
        self.assertEqual(dataset.group_field, "still_group_field")

        dataset.rename_sample_field("still_group_field", "group_field")

    @drop_datasets
    def test_delete_samples(self):
        dataset = _make_group_dataset()

        view = dataset.select_group_slice(_allow_mixed=True)
        self.assertEqual(len(view), 6)

        sample = view.shuffle(seed=51).first()

        dataset.delete_samples(sample.id)
        self.assertEqual(len(view), 5)

        dataset.delete_groups(sample.group_field.id)
        self.assertEqual(len(view), 3)

        group = next(iter(dataset.iter_groups()))

        dataset.delete_groups(group)

        self.assertEqual(len(view), 0)

    @drop_datasets
    def test_keep(self):
        dataset = _make_group_dataset()

        view = dataset.select_group_slice(_allow_mixed=True)
        self.assertEqual(len(view), 6)

        dataset.limit(1).keep()

        self.assertEqual(len(view), 3)

        dataset.select_group_slice("ego").keep()
        sample = view.first()

        self.assertEqual(len(view), 1)
        self.assertEqual(sample.group_field.name, "ego")

        dataset.clear()

        self.assertEqual(len(view), 0)

    @drop_datasets
    def test_slice_operations(self):
        dataset = _make_group_dataset()

        self.assertSetEqual(
            set(dataset.group_slices),
            {"left", "right", "ego"},
        )
        self.assertEqual(dataset.default_group_slice, "ego")
        self.assertEqual(dataset.group_slice, "ego")

        dataset.rename_group_slice("ego", "still_ego")

        self.assertSetEqual(
            set(dataset.group_slices),
            {"left", "right", "still_ego"},
        )
        self.assertEqual(dataset.default_group_slice, "still_ego")
        self.assertEqual(dataset.group_slice, "still_ego")
        self.assertEqual(len(dataset.select_group_slice(_allow_mixed=True)), 6)

        sample = dataset.first()
        self.assertEqual(sample.group_field.name, "still_ego")

        dataset.delete_group_slice("still_ego")

        self.assertSetEqual(set(dataset.group_slices), {"left", "right"})
        self.assertIn(dataset.default_group_slice, ["left", "right"])
        self.assertEqual(dataset.group_slice, dataset.default_group_slice)
        self.assertEqual(len(dataset.select_group_slice()), 4)

        dataset.delete_group_slice("left")

        self.assertSetEqual(set(dataset.group_slices), {"right"})
        self.assertEqual(dataset.default_group_slice, "right")
        self.assertEqual(dataset.group_slice, "right")
        self.assertEqual(len(dataset.select_group_slice()), 2)

        dataset.delete_group_slice("right")

        self.assertEqual(dataset.group_slices, [])
        self.assertIsNone(dataset.default_group_slice)
        self.assertIsNone(dataset.group_slice)
        self.assertEqual(len(dataset.select_group_slice()), 0)

        group = fo.Group()
        sample = fo.Sample(
            filepath="ego-video.mp4",
            group_field=group.element("ego"),
        )

        dataset.add_sample(sample)

        self.assertEqual(dataset.group_slices, ["ego"])
        self.assertEqual(dataset.default_group_slice, "ego")
        self.assertEqual(dataset.group_slice, "ego")
        self.assertEqual(len(dataset.select_group_slice()), 1)

    @drop_datasets
    def test_views(self):
        dataset = _make_group_dataset()

        # Group fields cannot be excluded
        with self.assertRaises(ValueError):
            view = dataset.exclude_fields("group_field")

        view = dataset.select_fields()

        self.assertEqual(view.media_type, "group")
        self.assertEqual(view.group_slice, "ego")
        self.assertEqual(view.default_group_slice, "ego")
        self.assertIn("group_field", view.get_field_schema())
        self.assertEqual(len(view), 2)

        num_samples = 0
        for sample in view:
            num_samples += 1

        self.assertEqual(num_samples, 2)

        num_groups = 0
        for group in view.iter_groups():
            self.assertIsInstance(group, dict)
            self.assertIn("left", group)
            self.assertIn("ego", group)
            self.assertIn("right", group)
            num_groups += 1

        self.assertEqual(num_groups, 2)

        sample = view.first()

        self.assertEqual(sample.group_field.name, "ego")
        self.assertEqual(sample.media_type, "video")

        group_id = sample.group_field.id
        group = view.get_group(group_id)

        self.assertIsInstance(group, dict)
        self.assertIn("left", group)
        self.assertIn("ego", group)
        self.assertIn("right", group)

        view = dataset.match(F("field") == 2)

        self.assertEqual(len(view), 1)
        self.assertEqual(view.first().field, 2)

        view = dataset.match(F("groups.left.field") == 4)

        self.assertEqual(len(view), 1)
        self.assertEqual(view.first().field, 5)

        view = dataset.select_group_slice("left")

        self.assertEqual(view.media_type, "image")
        self.assertEqual(len(view), 2)

        sample = view.first()
        self.assertEqual(sample.group_field.name, "left")

        view = dataset.select_group_slice(["left", "right"])

        self.assertEqual(view.media_type, "image")
        self.assertEqual(len(view), 4)

        self.assertListEqual(
            view.values("group_field.name"),
            ["left", "right", "left", "right"],
        )

        with self.assertRaises(ValueError):
            view = dataset.select_group_slice(["left", "ego"])

        with self.assertRaises(ValueError):
            view = dataset.select_group_slice()

    @drop_datasets
    def test_attached_groups(self):
        dataset = _make_group_dataset()

        detections = [
            fo.Detections(detections=[fo.Detection(label="left")]),
            fo.Detections(detections=[fo.Detection(label="ego")]),
            fo.Detections(detections=[fo.Detection(label="right")]),
            fo.Detections(detections=[fo.Detection(label="LEFT")]),
            fo.Detections(detections=[fo.Detection(label="EGO")]),
            fo.Detections(detections=[fo.Detection(label="RIGHT")]),
        ]

        view = dataset.select_group_slice(_allow_mixed=True)
        view.set_values("ground_truth", detections)

        dataset.group_slice = "left"
        self.assertListEqual(
            dataset.values("ground_truth.detections.label", unwind=True),
            ["left", "LEFT"],
        )

        dataset.group_slice = "right"
        self.assertListEqual(
            dataset.values("ground_truth.detections.label", unwind=True),
            ["right", "RIGHT"],
        )

        dataset.group_slice = "ego"
        self.assertListEqual(
            dataset.values("ground_truth.detections.label", unwind=True),
            ["ego", "EGO"],
        )

        field = dataset.get_field("field")
        self.assertIsInstance(field, fo.IntField)

        field = dataset.get_field("groups.left.field")
        self.assertIsInstance(field, fo.IntField)

        field = dataset.get_field("ground_truth.detections.label")
        self.assertIsInstance(field, fo.StringField)

        field = dataset.get_field("groups.right.ground_truth.detections.label")
        self.assertIsInstance(field, fo.StringField)

        # Verify that `groups.left.ground_truth` is correctly recognized as a
        # Detections field
        view = dataset.filter_labels(
            "groups.left.ground_truth",
            F("label") == F("label").upper(),
        )

        self.assertEqual(len(view), 1)

    @drop_datasets
    def test_aggregations(self):
        dataset = _make_group_dataset()

        self.assertEqual(dataset.count(), 2)
        self.assertEqual(dataset.count("frames"), 2)

        self.assertListEqual(dataset.distinct("field"), [2, 5])
        self.assertListEqual(
            dataset.select_group_slice(["left", "right"]).distinct("field"),
            [1, 3, 4, 6],
        )
        self.assertListEqual(
            dataset.select_group_slice(_allow_mixed=True).distinct("field"),
            [1, 2, 3, 4, 5, 6],
        )
        self.assertListEqual(dataset.distinct("frames.field"), [1, 2])

        view = dataset.limit(1)

        self.assertEqual(view.count(), 1)
        self.assertEqual(view.count("frames"), 2)

        self.assertListEqual(view.distinct("field"), [2])
        self.assertListEqual(
            view.select_group_slice(["left", "right"]).distinct("field"),
            [1, 3],
        )
        self.assertListEqual(
            view.select_group_slice(_allow_mixed=True).distinct("field"),
            [1, 2, 3],
        )
        self.assertListEqual(view.distinct("frames.field"), [1, 2])

        view = dataset.limit(1).select_group_slice("ego")

        self.assertEqual(view.count(), 1)
        self.assertEqual(view.count("frames"), 2)

        self.assertListEqual(view.distinct("field"), [2])
        self.assertListEqual(view.distinct("frames.field"), [1, 2])

    @drop_datasets
    def test_set_values(self):
        dataset = _make_group_dataset()

        dataset.set_values("new_field", [3, 4])

        self.assertListEqual(dataset.values("new_field"), [3, 4])
        self.assertListEqual(
            dataset.select_group_slice("left").values("new_field"),
            [None, None],
        )

        sample = dataset.first()

        self.assertEqual(sample.new_field, 3)

        sample = dataset.select_group_slice("left").first()

        self.assertIsNone(sample.new_field)

        view = dataset.select_group_slice(["left", "right"])

        view.set_values("new_field", [10, 20, 30, 40])

        self.assertListEqual(
            dataset.select_group_slice(_allow_mixed=True).values("new_field"),
            [10, 3, 20, 30, 4, 40],
        )

        sample = dataset.select_group_slice("left").first()

        self.assertEqual(sample.new_field, 10)

        view = dataset.limit(1)

        view.set_values("frames.new_field", [[3, 4]])

        self.assertListEqual(dataset.values("new_field"), [3, 4])

        self.assertListEqual(
            dataset.limit(1).values("frames.new_field", unwind=True), [3, 4]
        )

        sample = dataset.first()
        frame = sample.frames.first()

        self.assertEqual(frame.new_field, 3)

    @drop_datasets
    def test_to_dict(self):
        dataset = _make_group_dataset()

        d = dataset.to_dict()

        dataset2 = fo.Dataset.from_dict(d)

        self.assertEqual(dataset2.media_type, "group")
        self.assertEqual(dataset2.group_slice, "ego")
        self.assertEqual(dataset2.default_group_slice, "ego")
        self.assertIn("group_field", dataset2.get_field_schema())
        self.assertEqual(len(dataset2), 2)

        sample = dataset2.first()

        self.assertEqual(sample.group_field.name, "ego")
        self.assertEqual(sample.media_type, "video")
        self.assertEqual(len(sample.frames), 0)

        d = dataset.to_dict(include_frames=True)

        dataset3 = fo.Dataset.from_dict(d)

        self.assertEqual(dataset3.media_type, "group")
        self.assertEqual(dataset3.group_slice, "ego")
        self.assertEqual(dataset3.default_group_slice, "ego")
        self.assertIn("group_field", dataset3.get_field_schema())
        self.assertEqual(len(dataset3), 2)
        self.assertEqual(dataset3.count("frames"), 2)

        sample = dataset3.first()

        self.assertEqual(sample.group_field.name, "ego")
        self.assertEqual(sample.media_type, "video")
        self.assertEqual(len(sample.frames), 2)

        frame = sample.frames.first()

        self.assertEqual(frame.field, 1)

    @drop_datasets
    def test_clone(self):
        dataset = _make_group_dataset()

        dataset2 = dataset.clone()

        self.assertEqual(dataset2.media_type, "group")
        self.assertEqual(dataset2.group_slice, "ego")
        self.assertEqual(dataset2.default_group_slice, "ego")
        self.assertEqual(len(dataset2), 2)
        self.assertEqual(dataset2.count("frames"), 2)
        self.assertEqual(
            len(dataset2.select_group_slice(_allow_mixed=True)),
            6,
        )

        sample = dataset2.first()

        self.assertEqual(sample.group_field.name, "ego")
        self.assertEqual(sample.media_type, "video")
        self.assertEqual(len(sample.frames), 2)

        frame = sample.frames.first()

        self.assertEqual(frame.field, 1)

        view = dataset.limit(1)

        dataset3 = view.clone()

        self.assertEqual(dataset3.media_type, "group")
        self.assertEqual(dataset3.group_slice, "ego")
        self.assertEqual(dataset3.default_group_slice, "ego")
        self.assertEqual(len(dataset3), 1)
        self.assertEqual(dataset3.count("frames"), 2)
        self.assertEqual(
            len(dataset3.select_group_slice(_allow_mixed=True)),
            3,
        )

        sample = dataset3.first()

        self.assertEqual(sample.group_field.name, "ego")
        self.assertEqual(sample.media_type, "video")
        self.assertEqual(len(sample.frames), 2)

        frame = sample.frames.first()

        self.assertEqual(frame.field, 1)

        view = dataset.select_group_slice("ego")

        dataset4 = view.clone()

        self.assertEqual(dataset4.media_type, "video")
        self.assertIsNone(dataset4.group_slice)
        self.assertIsNone(dataset4.default_group_slice)
        self.assertEqual(len(dataset4), 2)
        self.assertEqual(dataset4.count("frames"), 2)

        sample = dataset4.first()

        self.assertEqual(sample.media_type, "video")
        self.assertEqual(len(sample.frames), 2)

        frame = sample.frames.first()

        self.assertEqual(frame.field, 1)


class GroupImportExportTests(unittest.TestCase):
    def setUp(self):
        temp_dir = etau.TempDir()
        tmp_dir = temp_dir.__enter__()

        self._temp_dir = temp_dir
        self._tmp_dir = tmp_dir

    def tearDown(self):
        self._temp_dir.__exit__()

    def _new_name(self):
        return "".join(
            random.choice(string.ascii_lowercase + string.digits)
            for _ in range(24)
        )

    def _new_dir(self):
        return os.path.join(self._tmp_dir, self._new_name())

    @drop_datasets
    def test_fiftyone_dataset(self):
        dataset = _make_group_dataset()

        export_dir = self._new_dir()

        dataset.export(
            export_dir=export_dir,
            dataset_type=fo.types.FiftyOneDataset,
            export_media=False,
        )

        dataset2 = fo.Dataset.from_dir(
            dataset_dir=export_dir,
            dataset_type=fo.types.FiftyOneDataset,
        )

        self.assertEqual(dataset2.media_type, "group")
        self.assertEqual(dataset2.group_slice, "ego")
        self.assertEqual(dataset2.default_group_slice, "ego")
        self.assertIn("group_field", dataset2.get_field_schema())
        self.assertIn("field", dataset2.get_frame_field_schema())
        self.assertEqual(len(dataset2), 2)

        sample = dataset.first()

        self.assertEqual(sample.group_field.name, "ego")
        self.assertEqual(sample.media_type, "video")
        self.assertEqual(len(sample.frames), 2)

        group_id = sample.group_field.id
        group = dataset.get_group(group_id)

        self.assertIsInstance(group, dict)
        self.assertIn("left", group)
        self.assertIn("ego", group)
        self.assertIn("right", group)

    @drop_datasets
    def test_legacy_fiftyone_dataset(self):
        dataset = _make_group_dataset()

        export_dir = self._new_dir()

        dataset.export(
            export_dir=export_dir,
            dataset_type=fo.types.LegacyFiftyOneDataset,
            export_media=False,
        )

        dataset2 = fo.Dataset.from_dir(
            dataset_dir=export_dir,
            dataset_type=fo.types.LegacyFiftyOneDataset,
        )

        # LegacyFiftyOneDataset doesn't know how to load this info...
        dataset2.default_group_slice = "ego"
        dataset2.group_slice = "ego"

        self.assertEqual(dataset2.media_type, "group")
        self.assertEqual(dataset2.group_slice, "ego")
        self.assertEqual(dataset2.default_group_slice, "ego")
        self.assertIn("group_field", dataset2.get_field_schema())
        self.assertIn("field", dataset2.get_frame_field_schema())
        self.assertEqual(len(dataset2), 2)

        sample = dataset.first()

        self.assertEqual(sample.group_field.name, "ego")
        self.assertEqual(sample.media_type, "video")
        self.assertEqual(len(sample.frames), 2)

        group_id = sample.group_field.id
        group = dataset.get_group(group_id)

        self.assertIsInstance(group, dict)
        self.assertIn("left", group)
        self.assertIn("ego", group)
        self.assertIn("right", group)


def _make_group_dataset():
    dataset = fo.Dataset()
    dataset.add_group_field("group_field", default="ego")

    group1 = fo.Group()
    group2 = fo.Group()

    samples = [
        fo.Sample(
            filepath="left-image1.jpg",
            group_field=group1.element("left"),
            field=1,
        ),
        fo.Sample(
            filepath="ego-video1.mp4",
            group_field=group1.element("ego"),
            field=2,
        ),
        fo.Sample(
            filepath="right-image1.jpg",
            group_field=group1.element("right"),
            field=3,
        ),
        fo.Sample(
            filepath="left-image2.jpg",
            group_field=group2.element("left"),
            field=4,
        ),
        fo.Sample(
            filepath="ego-video2.mp4",
            group_field=group2.element("ego"),
            field=5,
        ),
        fo.Sample(
            filepath="right-image2.jpg",
            group_field=group2.element("right"),
            field=6,
        ),
    ]

    dataset.add_samples(samples)

    sample = dataset.first()
    sample.frames[1] = fo.Frame(field=1)
    sample.frames[2] = fo.Frame(field=2)
    sample.save()

    return dataset


if __name__ == "__main__":
    fo.config.show_progress_bars = False
    unittest.main(verbosity=2)