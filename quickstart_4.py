import json
import glob
import random
import fiftyone as fo
import ntpath

# Import dataset by explicitly providing paths to the source media and labels
dataset = fo.Dataset.from_dir(dataset_type=fo.types.COCODetectionDataset,
                              data_path="./data/Station_Beach/",
                              labels_path="data/instances_default.json",
                              name="francis1", )
dataset.persistent = False
session = fo.launch_app(dataset)
session.wait()
