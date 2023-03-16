import glob
import random

import fiftyone as fo
import fiftyone.zoo as foz
from fiftyone import ViewField as F


# def rand_box():
#     lx = 1
#     ly = 1
#     rx = random.uniform(0, lx)
#     ry = random.uniform(0, ly)
#     w = random.uniform(0, lx - rx)
#     h = random.uniform(0, ly - ry)
#     return [rx, ry, w, h]
#
#
# # Ex: your custom label format
# annotations = {
#     "./test_data/Station_Beach/2022-08-31_09-50-16.jpg": [
#         {"bbox": rand_box(), "label": 'person'},
#         {"bbox": rand_box(), "label": '1'},
#     ],
# }
#
# # Create samples for your data
# samples = []
# images_patt = "./test_data/Station_Beach/2022-08-31_09-50-16.jpg"
# for filepath in glob.glob(images_patt):
#     sample = fo.Sample(filepath=filepath)
#
#     # Convert detections to FiftyOne format
#     detections = []
#     for obj in annotations[filepath]:
#         label = obj["label"]
#
#         # Bounding box coordinates should be relative values
#         # in [0, 1] in the following format:
#         # [top-left-x, top-left-y, width, height]
#         bounding_box = obj["bbox"]
#
#         detections.append(
#             fo.Detection(label=label, bounding_box=bounding_box)
#         )
#
#     # Store detections in a field name of your choice
#     sample["ground_truth"] = fo.Detections(detections=detections)
#
#     samples.append(sample)
#
# # Create dataset
# dataset = fo.Dataset("my-detection-dataset_non_persistent")
# dataset.add_samples(samples)
# dataset.persistent = False
#
# # Let's edit the ground truth annotations for the sample with the most high confidence false positives
# sample_id = dataset.first().id
# view = dataset.select(sample_id)
#
# # Step 3: Send samples to CVAT
#
# # A unique identifier for this run
# anno_key = "francis3"

dataset = foz.load_zoo_dataset("quickstart")
view = dataset.take(1)

anno_key = "cvat_new_field"

view.annotate(
    anno_key,
    label_field="new_classifications",
    label_type="classifications",
    classes=["dog", "cat", "person"],
    launch_editor=True,
    username='franciszero',
    password='cTBrvG@bHn2r3X8',
    url="http://localhost:8080",
)
print(dataset.get_annotation_info(anno_key))
# Create annotations in CVAT
dataset.load_annotations(anno_key, cleanup=True)
dataset.delete_annotation_run(anno_key)
