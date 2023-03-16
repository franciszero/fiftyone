import fiftyone as fo
import fiftyone.zoo as foz
from fiftyone import DatasetView

dataset = foz.load_zoo_dataset(
    "coco-2017",
    split="validation",
    dataset_name="evaluate-detections-tutorial",
)
dataset.persistent = True
print(dataset)

# Print a ground truth detection
sample = dataset.first()
print(sample.ground_truth.detections[0])
# <Detection: {
#     'id': '64093c181f06cc0a7fd32706',
#     'attributes': {},
#     'tags': [],
#     'label': 'potted plant',
#     'bounding_box': [
#         0.37028125,
#         0.3345305164319249,
#         0.038593749999999996,
#         0.16314553990610328,
#     ],
#     'mask': None,
#     'confidence': None,
#     'index': None,
#     'supercategory': 'furniture',
#     'iscrowd': 0,
# }>

session = fo.launch_app(dataset)
# View the dataset in the App
session.wait()
