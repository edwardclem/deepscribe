import pytorch_lightning as pl
import wandb

from deepscribe2.datasets import PFADetectionDataModule
from deepscribe2.models.detection import RetinaNet
from deepscribe2 import transforms as T

DATA_BASE = "/local/ecw/DeepScribe_Data_2023-02-04-selected"
WANDB_PROJECT = "deepscribe-torchvision"
MONITOR_ATTRIBUTE = "map_50"
LOCALIZATION_ONLY = True

xforms = T.Compose(
    [
        T.RandomHorizontalFlip(),
        T.RandomShortestSize(
            [500, 640, 672, 704, 736, 768, 800], 1333
        ),  # taken directly from detectron2 config.
        # T.RandomIoUCrop(),
        # T.RandomZoomOut(),
        # T.RandomPhotometricDistort(),
    ]
)


pfa_data_module = PFADetectionDataModule(
    DATA_BASE,
    autocrop=True,
    batch_size=5,
    train_xforms=xforms,
    localization_only=LOCALIZATION_ONLY,
)


# imgs_base = f"{DATA_BASE}/cropped_images"
# categories = f"{DATA_BASE}/categories.txt"

# train_file = f"{DATA_BASE}/data_train.json"

# train_dataset = CuneiformLocalizationDataset(
#     train_file,
#     imgs_base,
#     categories,
#     transforms=xforms,
#     localization_only=LOCALIZATION_ONLY,
# )

# val_file = f"{DATA_BASE}/data_val.json"
# val_dataset = CuneiformLocalizationDataset(
#     train_file, imgs_base, categories, localization_only=LOCALIZATION_ONLY
# )

model = RetinaNet(num_classes=pfa_data_module.num_labels)

# load artifact!!

# download checkpoint locally (if not already cached)
# run = wandb.init(project=WANDB_PROJECT)
# artifact = run.use_artifact(f"ecw/{WANDB_PROJECT}/model-vjy1binx:v90", type="model")
# artifact_dir = artifact.download()
# model = RetinaNet.load_from_checkpoint(Path(artifact_dir) / "model.ckpt")


# loader = DataLoader(
#     train_dataset,
#     batch_size=5,
#     shuffle=True,
#     collate_fn=collate_retinanet,
#     num_workers=12,
# )
# val_loader = DataLoader(
#     val_dataset,
#     batch_size=5,
#     collate_fn=collate_retinanet,
#     num_workers=12,
# )

logger = pl.loggers.WandbLogger(project=WANDB_PROJECT, log_model="all")
checkpoint_callback = pl.callbacks.ModelCheckpoint(
    monitor=MONITOR_ATTRIBUTE, mode="max"
)
earlystop_callback = pl.callbacks.EarlyStopping(
    monitor=MONITOR_ATTRIBUTE, mode="max", patience=5
)

trainer = pl.Trainer(
    accelerator="gpu",
    devices=1,
    logger=logger,
    max_epochs=250,
    callbacks=[checkpoint_callback, earlystop_callback],
)
trainer.fit(model, datamodule=pfa_data_module)
