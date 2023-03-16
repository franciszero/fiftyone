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

session = fo.launch_app(dataset)
# View the dataset in the App
session.wait()
