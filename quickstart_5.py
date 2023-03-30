from PIL import Image
import torch
import fiftyone as fo
from torchvision.transforms import functional as func
from transformers import DetrImageProcessor, DetrForObjectDetection
from fiftyone.core.dataset import delete_dataset, dataset_exists, list_datasets

dataset = fo.Dataset.from_dir(dataset_type=fo.types.COCODetectionDataset,
                              data_path="./data/Station_Beach/",
                              labels_path="data/instances_default.json",
                              name="DertResNet50-Facebook", )
dataset.persistent = True
# predictions_view = dataset.take(dataset.count(), seed=51)
#
# processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50")
# model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50")
#
# # Get class list
# classes = dataset.default_classes
# # Add predictions to samples
# with fo.ProgressBar() as pb:
#     for sample in pb(predictions_view):
#         image = Image.open(sample.filepath).convert('RGB')
#         image = func.to_tensor(image).to('cpu')
#         c, h, w = image.shape
#
#         inputs = processor(images=image, return_tensors="pt")
#         outputs = model(**inputs)
#         # convert outputs (bounding boxes and class logits) to COCO API
#         target_sizes = torch.tensor([image.size()[1:]])  # tensor([[3040, 4056]])  order: x,y
#         results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.65)[0]
#
#         # Convert detections to FiftyOne format
#         detections = []
#         for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
#             # Convert to [top-left-x, top-left-y, width, height]
#             # in relative coordinates in [0, 1] x [0, 1]
#             x1, y1, x2, y2 = box
#             rel_box = [x1 / w, y1 / h, (x2 - x1) / w, (y2 - y1) / h]
#
#             item_name = model.config.id2label[label.item()]
#             if item_name == 'person':
#                 detections.append(
#                     fo.Detection(
#                         label=classes[label],  # 1
#                         bounding_box=rel_box,  # [0.xxx, 0.xxx, 0.xxx, 0.xxx]
#                         confidence=score
#                     )
#                 )
#
#         # Save predictions to dataset
#         sample["predictions"] = fo.Detections(detections=detections)
#         sample.save()
#
# session = fo.launch_app(dataset)
# session.wait()
