import fiftyone as fo
from fiftyone import ViewField as F
from fiftyone import dataset_exists, delete_dataset, list_datasets

default_dataset = fo.load_dataset("DertResNet50")
# predictions_view = default_dataset.take(default_dataset.count(), seed=51)
high_conf_view = default_dataset.view().filter_labels("predictions", F("confidence") > 0.5, only_matches=False)
results = high_conf_view.evaluate_detections(
    "predictions",
    gt_field="detections",
    eval_key="eval",
    compute_mAP=True,
)
# Get the 10 most common classes in the dataset
counts = default_dataset.count_values("detections.detections.label")
classes_top10 = sorted(counts, key=counts.get, reverse=True)[:10]

# Print a classification report for the top-10 classes
results.print_report(classes=classes_top10)
print("mAP score: %.3f" % results.mAP())
plot = results.plot_pr_curves(classes=["1"])
plot.show()
# plot.freeze()  # replaces interactive plot with static image
