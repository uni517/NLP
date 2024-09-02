import os
import yaml
import torch
import pytorch_lightning as pl
from argparse import ArgumentParser, Namespace
from pytorch_lightning.metrics.functional import accuracy

from transformers import (
    OpenAIGPTDoubleHeadsModel,
    OpenAIGPTTokenizer,
    GPT2DoubleHeadsModel,
    GPT2Tokenizer,
    AdamW,
)
from model.data import add_special_tokens_

class PersonaChatModel(pl.LightningModule):
    def __init__(self, hparams):
        super().__init__()
        self.save_hyperparameters(hparams)

        MODEL_CLASSES = {
            "openai-gpt": (OpenAIGPTDoubleHeadsModel, OpenAIGPTTokenizer),
            "gpt2": (GPT2DoubleHeadsModel, GPT2Tokenizer),
        }
        model_class, tokenizer_class = MODEL_CLASSES[self.hparams.model_name]
        self.model = model_class.from_pretrained(self.hparams.model_name)
        self.tokenizer = tokenizer_class.from_pretrained(self.hparams.model_name)
        add_special_tokens_(self.model, self.tokenizer)
   
    def forward(self, input_ids=None, mc_token_ids=None, lm_labels=None, mc_labels=None, token_type_ids=None):
        outputs = self.model(
            input_ids=input_ids,
            token_type_ids=token_type_ids,
            mc_token_ids=mc_token_ids,
            mc_labels=mc_labels,
            labels=lm_labels
        )
        return outputs

    def training_step(self, batch, batch_idx):
        input_ids, mc_token_ids, lm_labels, mc_labels, token_type_ids = batch       
        outputs = self.model(
            input_ids=input_ids,
            token_type_ids=token_type_ids,
            mc_token_ids=mc_token_ids,
            mc_labels=mc_labels,            
            labels=lm_labels
        )
        lm_loss = outputs.loss
        mc_loss = outputs.mc_loss
        loss = (lm_loss * self.hparams.lm_coef + mc_loss * self.hparams.mc_coef) / self.hparams.gradient_accumulation_steps
        mc_pred = torch.topk(outputs.mc_logits, 1)[1].view(-1)
        acc = accuracy(mc_pred, mc_labels)
        self.log('train_loss', loss, on_epoch=True)
        self.log('train_nll', lm_loss, on_epoch=True)               
        self.log('train_acc', acc, on_epoch=True)
        return loss

    def validation_step(self, batch, batch_idx):
        input_ids, mc_token_ids, lm_labels, mc_labels, token_type_ids = batch       
        outputs = self.model(
            input_ids=input_ids,
            token_type_ids=token_type_ids,
            mc_token_ids=mc_token_ids,
            mc_labels=mc_labels,            
            labels=lm_labels
        )
        lm_loss = outputs.loss
        mc_loss = outputs.mc_loss 
        loss = (lm_loss * self.hparams.lm_coef + mc_loss * self.hparams.mc_coef) / self.hparams.gradient_accumulation_steps
        mc_pred = torch.topk(outputs.mc_logits, 1)[1].view(-1)
        acc = accuracy(mc_pred, mc_labels)
        self.log('val_loss', loss, on_step=True, sync_dist=True)
        self.log('val_nll', lm_loss, on_step=True, sync_dist=True)              
        self.log('val_acc', acc, on_step=True, sync_dist=True)

    def configure_optimizers(self):
        optimizer = AdamW(
            self.parameters(),
            self.hparams.learning_rate,
            betas=(self.hparams.adam_beta1, self.hparams.adam_beta2),
            eps=self.hparams.adam_epsilon
        )
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=10)
        return [optimizer], [scheduler]

    @classmethod
    def load_from_experiment(cls, experiment_folder: str):
        """Function that loads the model from an experiment folder.
        :param experiment_folder: Path to the experiment folder.
        :return:Pretrained model.
        """
        hparams_file = experiment_folder + "hparams.yaml"
        hparams = yaml.load(open(hparams_file).read(), Loader=yaml.FullLoader)
        checkpoints_folder= experiment_folder + "checkpoints/"
        checkpoints = [
            file for file in os.listdir(checkpoints_folder) if file.endswith(".ckpt")
        ]
        checkpoint_path = checkpoints_folder + checkpoints[-1]
        model = cls.load_from_checkpoint(
            checkpoint_path, hparams=Namespace(**hparams), strict=True
        )
        # Make sure model is in prediction mode
        model.eval()
        model.freeze()
        return model


    @staticmethod
    def add_model_specific_args(parent_parser):
        parser = ArgumentParser(parents=[parent_parser], add_help=False)
        parser.add_argument("--model_name", type=str, default="gpt2", help="Path, url or short name of the model")    
        parser.add_argument("--lm_coef", type=float, default=1.0, help="LM loss coefficient")
        parser.add_argument("--mc_coef", type=float, default=1.0, help="Multiple-choice loss coefficient")
        parser.add_argument("--gradient_accumulation_steps", type=int, default=8, help="Accumulate gradients on several steps")   
        parser.add_argument('--learning_rate', type=float, default=5e-5)
        parser.add_argument('--adam_beta1', type=float, default=0.9)
        parser.add_argument('--adam_beta2', type=float, default=0.999)
        parser.add_argument('--adam_epsilon', type=float, default=1e-8)
        return parser