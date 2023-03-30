import fiftyone as fo
import sys
from fiftyone.core.dataset import delete_dataset, dataset_exists, list_datasets

model_name = str(sys.argv[1])
dataset = fo.load_dataset(model_name)
session = fo.launch_app(dataset)
session.wait()
