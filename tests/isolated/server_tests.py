"""
ServerService tests.

To run a single test, modify the main code to::

    singletest = unittest.TestSuite()
    singletest.addTest(TESTCASE("<TEST METHOD NAME>"))
    unittest.TextTestRunner().run(singletest)

| Copyright 2017-2020, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""
import asyncio
from collections import defaultdict
import json
import os
import time
import unittest
import urllib

from bson import ObjectId
import numpy as np
from tornado.testing import AsyncHTTPTestCase
from tornado.websocket import websocket_connect

import eta.core.serial as etas
import eta.core.utils as etau

import fiftyone as fo
import fiftyone.core.state as fos
from fiftyone.server.json_util import FiftyOneJSONEncoder
import fiftyone.server.main as fosm


class TestCase(AsyncHTTPTestCase):
    def get_app(self):
        return fosm.Application()

    def fetch_and_parse(self, path):
        response = self.fetch(path)
        return etas.load_json(response.body)


class RouteTests(TestCase):
    def test_fiftyone(self):
        response = self.fetch_and_parse("/fiftyone")
        self.assertEqual(response, fosm.FiftyOneHandler.get_response())

    def test_stages(self):
        response = self.fetch_and_parse("/stages")
        self.assertEqual(response, fosm.StagesHandler.get_response())

    def test_filepath(self):
        data = {"hello": "world"}
        with etau.TempDir() as tmp:
            path = os.path.join(tmp, "data.json")
            etas.write_json(data, path)
            response = self.fetch_and_parse("/filepath%s" % path)

        self.assertEqual(response, data)


class StateTests(TestCase):

    image_url = "https://user-images.githubusercontent.com/3719547/74191434-8fe4f500-4c21-11ea-8d73-555edfce0854.png"
    test_one = os.path.abspath("./test_one.png")
    test_two = os.path.abspath("./test_two.png")
    dataset = fo.Dataset("test")
    sample1 = fo.Sample(filepath=test_one)
    sample2 = fo.Sample(filepath=test_two)

    @classmethod
    def setUpClass(cls):
        urllib.request.urlretrieve(cls.image_url, cls.test_one)
        etau.copy_file(cls.test_one, cls.test_two)
        cls.dataset.add_sample(cls.sample1)
        cls.dataset.add_sample(cls.sample2)
        cls.sample1["scalar"] = 1
        cls.sample1["label"] = fo.Classification(label="test")
        cls.sample1.tags.append("tag")
        cls.sample1["floats"] = [
            0.5,
            float("nan"),
            float("inf"),
            float("-inf"),
        ]
        cls.sample1.save()

    def setUp(self):
        super().setUp()
        self.__app_client = self.get_ws()
        self.gather_events({self.app: 1})
        self.send(self.app, "as_app", {})
        self.__session_client = self.get_ws()
        self.gather_events({self.session: 1})

    def get_ws(self):
        websocket_connect(self.get_socket_path(), callback=self.stop)
        return self.wait().result()

    @property
    def app(self):
        return self.__app_client

    @property
    def session(self):
        return self.__session_client

    @property
    def enc(self):
        return FiftyOneJSONEncoder

    def assertNormalizedEqual(self, one, two):
        one = self.enc.loads(self.enc.dumps(one))
        two = self.enc.loads(self.enc.dumps(two))
        self.assertEqual(one, two)

    def get_socket_path(self):
        return "ws://localhost:%d/state" % self.get_http_port()

    def send(self, client, event, message={}):
        payload = {"type": event}
        payload.update(message)
        client.write_message(FiftyOneJSONEncoder.dumps(payload))

    def gather_events(self, num_events):
        results = defaultdict(list)
        for client, num_events in num_events.items():
            for i in range(0, num_events):
                client.read_message(self.stop)
                message = self.wait().result()
                message = FiftyOneJSONEncoder.loads(message)
                results[client].append(message)
        return results

    """
    @todo figure out tests
    def test_update(self):
        state = fos.StateDescription(dataset=self.dataset).serialize()
        self.send(self.session, "update", {"state": state})
        results = self.gather_events({self.app: 2})
        for client, result in results.items():
            for message in result:
                if message["type"] == "update":
                    result_state = fos.StateDescription.from_dict(
                        message["state"]
                    ).serialize()
                    self.assertNormalizedEqual(result_state, state)
                if message["type"] == "statistics":
                    aggs = fos.DatasetStatistics(self.dataset).aggregations
                    stats = self.dataset.aggregate(aggs)
                    stats = [r.serialize(reflective=True) for r in stats]
                    self.assertNormalizedEqual(message["stats"], stats)
                    self.assertFalse(message["extended"])
                if message["type"] == "notification":
                    print(message)
    """


if __name__ == "__main__":
    fo.config.show_progress_bars = False
    unittest.main(verbosity=2)
