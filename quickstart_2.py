import os

import fiftyone as fo

workspace = os.getcwd()

# # Create a dataset from a list of images
# dataset = fo.Dataset.from_images(
#     [workspace + "/test_data/Station_Beach/2022-08-31_09-50-16.jpg",
#      workspace + "/test_data/Station_Beach/2022-09-02_15-00-16.jpg"]
# )

# Create a dataset from a directory of images
dataset = fo.Dataset.from_images_dir("./test_data/Station_Beach")

# # Create a dataset from a glob pattern of images
# dataset = fo.Dataset.from_images_patt("/path/to/images/*.jpg")

session = fo.launch_app(dataset)
session.wait()
