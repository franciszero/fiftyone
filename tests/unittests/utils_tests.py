"""
FiftyOne utilities unit tests.

| Copyright 2017-2023, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""
import time
import unittest

import numpy as np

import fiftyone as fo
import fiftyone.constants as foc
import fiftyone.core.media as fom
import fiftyone.core.odm as foo
import fiftyone.core.utils as fou
import fiftyone.core.uid as foui
from fiftyone.migrations.runner import MigrationRunner

from decorators import drop_datasets


class CoreUtilsTests(unittest.TestCase):
    def test_validate_hex_color(self):
        # Valid colors
        fou.validate_hex_color("#FF6D04")
        fou.validate_hex_color("#ff6d04")
        fou.validate_hex_color("#000")
        fou.validate_hex_color("#eee")

        # Invalid colors
        with self.assertRaises(ValueError):
            fou.validate_hex_color("aaaaaa")

        with self.assertRaises(ValueError):
            fou.validate_hex_color("#bcedfg")

        with self.assertRaises(ValueError):
            fou.validate_hex_color("#ggg")

        with self.assertRaises(ValueError):
            fou.validate_hex_color("#FFFF")

    def test_to_slug(self):
        self.assertEqual(fou.to_slug("coco_2017"), "coco-2017")
        self.assertEqual(fou.to_slug("c+o+c+o 2-0-1-7"), "c-o-c-o-2-0-1-7")
        self.assertEqual(fou.to_slug("cat.DOG"), "cat-dog")
        self.assertEqual(fou.to_slug("---z----"), "z")
        self.assertEqual(
            fou.to_slug("Brian's #$&@ [awesome?] dataset!"),
            "brians-awesome-dataset",
        )
        self.assertEqual(
            fou.to_slug("     sPaM     aNd  EgGs    "),
            "spam-and-eggs",
        )

        with self.assertRaises(ValueError):
            fou.to_slug("------")  # too short

        with self.assertRaises(ValueError):
            fou.to_slug("a" * 101)  # too long


class LabelsTests(unittest.TestCase):
    @drop_datasets
    def test_create(self):
        labels = fo.Classification(label="cow", confidence=0.98)
        self.assertIsInstance(labels, fo.Classification)

        with self.assertRaises(Exception):
            fo.Classification(label=100)

    @drop_datasets
    def test_copy(self):
        dataset = fo.Dataset()

        dataset.add_sample(
            fo.Sample(
                filepath="filepath1.jpg",
                test_dets=fo.Detections(
                    detections=[
                        fo.Detection(
                            label="friend",
                            confidence=0.9,
                            bounding_box=[0, 0, 0.5, 0.5],
                        )
                    ]
                ),
            )
        )

        sample = dataset.first()
        sample2 = sample.copy()

        self.assertIsNot(sample2, sample)
        self.assertNotEqual(sample2.id, sample.id)
        self.assertIsNot(sample2.test_dets, sample.test_dets)
        det = sample.test_dets.detections[0]
        det2 = sample2.test_dets.detections[0]
        self.assertIsNot(det2, det)
        self.assertNotEqual(det2.id, det.id)


class SerializationTests(unittest.TestCase):
    def test_embedded_document(self):
        label1 = fo.Classification(label="cat", logits=np.arange(4))

        label2 = fo.Classification(label="cat", logits=np.arange(4))

        d1 = label1.to_dict()
        d2 = label2.to_dict()
        d1.pop("_id")
        d2.pop("_id")
        self.assertDictEqual(d1, d2)

        d = label1.to_dict()
        self.assertEqual(fo.Classification.from_dict(d), label1)

        s = label1.to_json(pretty_print=False)
        self.assertEqual(fo.Classification.from_json(s), label1)

        s = label1.to_json(pretty_print=True)
        self.assertEqual(fo.Classification.from_json(s), label1)

    def test_sample_no_dataset(self):
        """This test only works if the samples do not have Classification or
        Detection fields because of the autogenerated ObjectIDs.
        """
        sample1 = fo.Sample(
            filepath="~/Desktop/test.png",
            tags=["test"],
            vector=np.arange(5),
            array=np.ones((2, 3)),
            float=5.1,
            bool=True,
            int=51,
        )

        sample2 = fo.Sample(
            filepath="~/Desktop/test.png",
            tags=["test"],
            vector=np.arange(5),
            array=np.ones((2, 3)),
            float=5.1,
            bool=True,
            int=51,
        )
        self.assertDictEqual(sample1.to_dict(), sample2.to_dict())

        self.assertEqual(
            fo.Sample.from_dict(sample1.to_dict()).to_dict(), sample1.to_dict()
        )

    @drop_datasets
    def test_sample_in_dataset(self):
        """This test only works if the samples do not have Classification or
        Detection fields because of the autogenerated ObjectIDs.
        """
        dataset1 = fo.Dataset()
        dataset2 = fo.Dataset()

        sample1 = fo.Sample(
            filepath="~/Desktop/test.png",
            tags=["test"],
            vector=np.arange(5),
            array=np.ones((2, 3)),
            float=5.1,
            bool=True,
            int=51,
        )

        sample2 = fo.Sample(
            filepath="~/Desktop/test.png",
            tags=["test"],
            vector=np.arange(5),
            array=np.ones((2, 3)),
            float=5.1,
            bool=True,
            int=51,
        )

        self.assertDictEqual(sample1.to_dict(), sample2.to_dict())

        dataset1.add_sample(sample1)
        dataset2.add_sample(sample2)

        self.assertNotEqual(sample1, sample2)

        s1 = fo.Sample.from_dict(sample1.to_dict())
        s2 = fo.Sample.from_dict(sample2.to_dict())

        self.assertFalse(s1.in_dataset)
        self.assertNotEqual(s1, sample1)

        self.assertDictEqual(s1.to_dict(), s2.to_dict())


class MediaTypeTests(unittest.TestCase):
    @drop_datasets
    def setUp(self):
        self.img_sample = fo.Sample(filepath="image.png")
        self.img_dataset = fo.Dataset()
        self.img_dataset.add_sample(self.img_sample)

        self.vid_sample = fo.Sample(filepath="video.mp4")
        self.vid_dataset = fo.Dataset()
        self.vid_dataset.add_sample(self.vid_sample)

    def test_img_types(self):
        self.assertEqual(self.img_sample.media_type, fom.IMAGE)
        self.assertEqual(self.img_dataset.media_type, fom.IMAGE)

    def test_vid_types(self):
        self.assertEqual(self.vid_sample.media_type, fom.VIDEO)
        self.assertEqual(self.vid_dataset.media_type, fom.VIDEO)

    def test_img_change_attempts(self):
        with self.assertRaises(fom.MediaTypeError):
            self.img_sample.filepath = "video.mp4"

    def test_vid_change_attempts(self):
        with self.assertRaises(fom.MediaTypeError):
            self.vid_sample.filepath = "image.png"


class MigrationTests(unittest.TestCase):
    def test_runner(self):
        def revs(versions):
            return [(v, v + ".py") for v in versions]

        runner = MigrationRunner(
            "0.0.1",
            "0.3",
            _revisions=revs(["0.1", "0.2", "0.3"]),
        )
        self.assertEqual(runner.revisions, ["0.1", "0.2", "0.3"])

        runner = MigrationRunner(
            "0.1",
            "0.3",
            _revisions=revs(["0.1", "0.2", "0.3"]),
        )
        self.assertEqual(runner.revisions, ["0.2", "0.3"])

        runner = MigrationRunner(
            "0.3",
            "0.1",
            _revisions=revs(["0.1", "0.2", "0.3"]),
        )
        self.assertEqual(runner.revisions, ["0.3", "0.2"])

        runner = MigrationRunner(
            "0.3",
            "0.0.1",
            _revisions=revs(["0.1", "0.2", "0.3"]),
        )
        self.assertEqual(runner.revisions, ["0.3", "0.2", "0.1"])

    def test_future(self):
        pkg_ver = foc.VERSION
        future_ver = str(int(pkg_ver[0]) + 1) + pkg_ver[1:]

        # Uprading to a future version is not allowed

        with self.assertRaises(EnvironmentError):
            MigrationRunner(pkg_ver, future_ver)

        with self.assertRaises(EnvironmentError):
            MigrationRunner("0.1", future_ver)

        # Downgrading from a future version is not allowed

        with self.assertRaises(EnvironmentError):
            MigrationRunner(future_ver, pkg_ver)

        with self.assertRaises(EnvironmentError):
            MigrationRunner(future_ver, "0.1")


class UIDTests(unittest.TestCase):
    def test_log_import(self):
        fo.config.do_not_track = False
        foc.UA_ID = foc.UA_DEV

        foui.log_import_if_allowed(test=True)
        time.sleep(2)
        self.assertTrue(foui._import_logged)


class ConfigTests(unittest.TestCase):
    def test_multiple_config_cleanup(self):
        db = foo.get_db_conn()
        orig_config = foo.get_db_config()

        # Add some duplicate documents
        d = dict(orig_config.to_dict())
        for _ in range(2):
            d.pop("_id", None)
            db.config.insert_one(d)

        # Ensure that duplicate documents are automatically cleaned up
        config = foo.get_db_config()

        self.assertEqual(len(list(db.config.aggregate([]))), 1)
        self.assertEqual(config.id, orig_config.id)


class ProgressBarTests(unittest.TestCase):
    def _test_correct_value(self, progress, global_progress, quiet, expected):
        fo.config.show_progress_bars = global_progress
        with fou.ProgressBar(list(), progress=progress, quiet=quiet) as pb:
            assert pb._progress == expected

    def test_progress_None_uses_global(self):
        self._test_correct_value(
            progress=None, global_progress=True, quiet=None, expected=True
        )
        self._test_correct_value(
            progress=None, global_progress=False, quiet=None, expected=False
        )

    def test_progress_overwrites_global(self):
        self._test_correct_value(
            progress=True, global_progress=True, quiet=None, expected=True
        )
        self._test_correct_value(
            progress=True, global_progress=False, quiet=None, expected=True
        )
        self._test_correct_value(
            progress=False, global_progress=True, quiet=None, expected=False
        )
        self._test_correct_value(
            progress=False, global_progress=False, quiet=None, expected=False
        )

    def test_quiet_overwrites_all(self):
        # Careful, we expect here to have progress the opposite value of quiet, as they are opposites
        self._test_correct_value(
            progress=True, global_progress=True, quiet=True, expected=False
        )
        self._test_correct_value(
            progress=False, global_progress=False, quiet=False, expected=True
        )


if __name__ == "__main__":
    fo.config.show_progress_bars = False
    unittest.main(verbosity=2)
