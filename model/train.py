import os
import pytorch_lightning as pl
from pytorch_lightning.plugins import DeepSpeedPlugin
from pytorch_lightning.callbacks import EarlyStopping, ModelCheckpoint
from pytorch_lightning.loggers import TensorBoardLogger
from argparse import ArgumentParser
from datetime import datetime
from personachat import PersonaChatModel
from data import get_data_loaders

def train():
    # ------------------------------------------
    # Hyperparameters for dataset processing  
    # ------------------------------------------  
    parser = ArgumentParser()
    parser.add_argument("--dataset_path", type=str, default="", help="Path or url of the dataset. If empty download from S3.")
    parser.add_argument("--dataset_cache", type=str, default="personachat_self", help="Path or url of the dataset cache")
    parser.add_argument("--train_batch_size", type=int, default=4, help="Batch size for training")
    parser.add_argument("--valid_batch_size", type=int, default=4, help="Batch size for validation")
    parser.add_argument("--test_run_num", type=int, default=-1, help="Datapoints to run with in a test run")    
    parser.add_argument('--dataloader_num_workers', type=int, default=4, help="Number of workers of dataloader")
    
    # ------------------------------------------
    # Hyperparameters for model configuration  
    # ------------------------------------------     
    parser.add_argument("--no_persona", action='store_true', help="No Persona Evaluation")
    parser.add_argument("--no_comet_persona", action='store_true', help="No Comet Persona Evaluation")
    parser.add_argument("--num_beams", type=int, default=5, help="Number of beams for comet expansion")    
    parser.add_argument("--num_candidates", type=int, default=2, help="Number of candidates for training")
    parser.add_argument("--max_history", type=int, default=2, help="Number of previous exchanges to keep in history")
    parser.add_argument("--personality_permutations", type=int, default=1, help="Number of permutations of personality sentences")    
  
    # ------------------------------------------
    # Hyperparameters for training  
    # ------------------------------------------ 
    parser.add_argument("--deepspeed", action='store_true', help="Training with deepspeed")    
    parser.add_argument("--seed", type=int, default=1234, help="Training seed.")
    parser.add_argument("--save_top_k", default=1, type=int, help="The best k models according to the quantity monitored will be saved.")
    parser.add_argument("--monitor", default="val_loss", type=str, help="Quantity to monitor.")
    parser.add_argument("--metric_mode", default="min", type=str, help="If we want to min/max the monitored quantity.", choices=["auto", "min", "max"])
    parser.add_argument("--patience", default=3, type=int, help="Training will be stopped after number of epochs without improvement.")

    parser = PersonaChatModel.add_model_specific_args(parser)
    parser = pl.Trainer.add_argparse_args(parser)
    hparams = parser.parse_args()
    
    pl.seed_everything(hparams.seed)

    # ------------------------------------------
    # Init early stopping
    # ------------------------------------------
    early_stop_callback = EarlyStopping(
        monitor=hparams.monitor,
        min_delta=0.0,
        patience=hparams.patience,
        verbose=True,
        mode=hparams.metric_mode,
    )

    # ------------------------
    # Init loggers 
    # ------------------------
    # Tensorboard Callback
    tb_logger = TensorBoardLogger(
        save_dir="experiments/",
        version="version_" + datetime.now().strftime("%d-%m-%Y--%H-%M-%S"),
        name="",
    )

    # Model Checkpoint Callback
    ckpt_path = os.path.join(
        "experiments/", tb_logger.version, "checkpoints",
    )

    # --------------------------------
    # Init model checkpoint callback
    # -------------------------------
    checkpoint_callback = ModelCheckpoint(
        dirpath=ckpt_path,
        save_top_k=hparams.save_top_k,
        verbose=True,
        monitor=hparams.monitor,
        period=1,
        mode=hparams.metric_mode,
        save_weights_only=True
    )

    # ------------------------------------------
    # model and datasets
    # ------------------------------------------
    model = PersonaChatModel(hparams)
    train_loader, valid_loader = get_data_loaders(hparams, model.tokenizer)

    # ------------------------------------------
    # training
    # ------------------------------------------
    if hparams.deepspeed == True:
        trainer = pl.Trainer.from_argparse_args(
            hparams,
            logger=tb_logger,
            callbacks=[checkpoint_callback, early_stop_callback],
            terminate_on_nan=True,
            plugins=DeepSpeedPlugin("model/deepspeed_config.json")
        )
    else:    
        trainer = pl.Trainer.from_argparse_args(
            hparams,
            logger=tb_logger,
            callbacks=[checkpoint_callback, early_stop_callback],
            terminate_on_nan=True
        )
    
    trainer.fit(model=model, train_dataloader=train_loader, val_dataloaders=valid_loader)

if __name__ == "__main__":
    train()