import glob
import random

import fiftyone as fo

images_patt = "./test_data/Station_Beach/*"


def rand_box():
    lx = 1
    ly = 1
    rx = random.uniform(0, lx)
    ry = random.uniform(0, ly)
    w = random.uniform(0, lx - rx)
    h = random.uniform(0, ly - ry)
    return [rx, ry, w, h]


# Ex: your custom label format
annotations = {
    "./test_data/Station_Beach/2022-08-31_09-50-16.jpg": [
        {"bbox": rand_box(), "label": '1'},
        {"bbox": rand_box(), "label": '1'},
    ],
    "./test_data/Station_Beach/2022-09-02_13-50-14.jpg": [
        {"bbox": rand_box(), "label": '1'},
        {"bbox": rand_box(), "label": '1'},
    ],
    "./test_data/Station_Beach/2022-09-02_15-00-16.jpg": [
        {"bbox": rand_box(), "label": '1'},
        {"bbox": rand_box(), "label": '1'},
    ],
    "./test_data/Station_Beach/2022-09-02_15-50-16.jpg": [
        {"bbox": rand_box(), "label": '1'},
        {"bbox": rand_box(), "label": '1'},
    ],
    "./test_data/Station_Beach/2022-09-02_16-30-16.jpg": [
        {"bbox": rand_box(), "label": '1'},
        {"bbox": rand_box(), "label": '1'},
    ],
    "./test_data/Station_Beach/2022-09-04_14-43-18.jpg": [
        {"bbox": rand_box(), "label": '1'},
        {"bbox": rand_box(), "label": '1'},
    ],
    "./test_data/Station_Beach/2022-09-04_15-31-23.jpg": [
        {"bbox": rand_box(), "label": '1'},
        {"bbox": rand_box(), "label": '1'},
    ],
    "./test_data/Station_Beach/2022-09-05_17-50-16.jpg": [
        {"bbox": rand_box(), "label": '1'},
        {"bbox": rand_box(), "label": '1'},
    ],
    "./test_data/Station_Beach/2022-09-06_15-40-16.jpg": [
        {"bbox": rand_box(), "label": '1'},
        {"bbox": rand_box(), "label": '1'},
    ],
    "./test_data/Station_Beach/2022-09-07_15-26-00.jpg": [
        {"bbox": rand_box(), "label": '1'},
        {"bbox": rand_box(), "label": '1'},
    ],
    "./test_data/Station_Beach/2022-09-08_08-50-16.jpg": [
        {"bbox": rand_box(), "label": '1'},
        {"bbox": rand_box(), "label": '1'},
    ],
    "./test_data/Station_Beach/2022-09-11_12-40-15.jpg": [
        {"bbox": rand_box(), "label": '1'},
        {"bbox": rand_box(), "label": '1'},
    ],
    "./test_data/Station_Beach/2022-09-13_13-35-37.jpg": [
        {"bbox": rand_box(), "label": '1'},
        {"bbox": rand_box(), "label": '1'},
    ],
    "./test_data/Station_Beach/2022-09-13_18-24-10.jpg": [
        {"bbox": rand_box(), "label": '1'},
        {"bbox": rand_box(), "label": '1'},
    ],
    "./test_data/Station_Beach/2022-09-14_16-50-16.jpg": [
        {"bbox": rand_box(), "label": '1'},
        {"bbox": rand_box(), "label": '1'},
    ],
    "./test_data/Station_Beach/2022-09-17_16-10-16.jpg": [
        {"bbox": rand_box(), "label": '1'},
        {"bbox": rand_box(), "label": '1'},
    ],
    "./test_data/Station_Beach/2022-09-19_17-33-01.jpg": [
        {"bbox": rand_box(), "label": '1'},
        {"bbox": rand_box(), "label": '1'},
    ],
    "./test_data/Station_Beach/2022-09-19_18-03-10.jpg": [
        {"bbox": rand_box(), "label": '1'},
        {"bbox": rand_box(), "label": '1'},
    ],
    "./test_data/Station_Beach/2022-09-22_13-23-02.jpg": [
        {"bbox": rand_box(), "label": '1'},
        {"bbox": rand_box(), "label": '1'},
    ],
}

# Create samples for your data
samples = []
for filepath in glob.glob(images_patt):
    sample = fo.Sample(filepath=filepath)

    # Convert detections to FiftyOne format
    detections = []
    for obj in annotations[filepath]:
        label = obj["label"]

        # Bounding box coordinates should be relative values
        # in [0, 1] in the following format:
        # [top-left-x, top-left-y, width, height]
        bounding_box = obj["bbox"]

        detections.append(
            fo.Detection(label=label, bounding_box=bounding_box)
        )

    # Store detections in a field name of your choice
    sample["ground_truth"] = fo.Detections(detections=detections)

    samples.append(sample)

# Create dataset
dataset = fo.Dataset("my-detection-dataset_non_persistent")
dataset.add_samples(samples)
dataset.persistent = False
# dataset.default_classes = ['0', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light', 'fire hydrant', '12', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', '26', 'backpack', 'umbrella', '29', '30', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket', 'bottle', '45', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', '66', 'dining table', '68', '69', 'toilet', '71', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator', '83', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush']

# Print a ground truth detection
sample = dataset.first()
print(sample.ground_truth.detections[0])
# <Detection: {
#     'id': '64132149c7e419ef5f5e848f',
#     'attributes': {},
#     'tags': [],
#     'label': '1',
#     'bounding_box': [
#         0.14144799078191383,
#         0.30414157483031257,
#         0.40678507537054576,
#         0.21392984221488906,
#     ],
#     'mask': None,
#     'confidence': None,
#     'index': None,
# }>

session = fo.launch_app(dataset)
session.wait()
