import fiftyone as fo
from fiftyone import ViewField as F

dataset = fo.load_dataset("DertResNet50-Facebook",
                          gt_field="ground_truth",
                          eval_key="eval",
                          compute_mAP=True, )

predictions_view = dataset.take(dataset.count(), seed=51)
high_conf_view = predictions_view.filter_labels("predictions", F("confidence") > 0.75, only_matches=False)
results = high_conf_view.evaluate_detections(
    "predictions",
    gt_field="detections",
    eval_key="eval",
    compute_mAP=True,
)
# Get the 10 most common classes in the dataset
counts = dataset.count_values("detections.detections.label")
classes_top10 = sorted(counts, key=counts.get, reverse=True)[:10]

# Print a classification report for the top-10 classes
results.print_report(classes=classes_top10)
print(results.mAP())
plot = results.plot_pr_curves(classes=["1"])
plot.show()
plot.freeze()  # replaces interactive plot with static image

