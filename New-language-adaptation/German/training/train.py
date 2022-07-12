 #!/usr/bin/env python
# coding: utf-8

import nemo
import nemo.collections.asr as nemo_asr

print(nemo.__version__)

from hydra import initialize, initialize_config_module, initialize_config_dir, compose
from omegaconf import OmegaConf, open_dict
from pytorch_lightning.callbacks import ModelCheckpoint
import pytorch_lightning as pl

asr_model = nemo_asr.models.EncDecCTCModelBPE.from_pretrained(model_name="stt_en_citrinet_1024")

# Now let's update the vocabulary in this model
# Lets change the tokenizer vocabulary by passing the path to the new directory,
asr_model.change_vocabulary(
    new_tokenizer_dir="./data/processed/tokenizer/tokenizer_spe_bpe_v1024/",
    new_tokenizer_type="bpe"
)

USE_TARRED_DATASET = True

if USE_TARRED_DATASET:
    # Setup train, validation, test configs
    with open_dict(asr_model.cfg):    
      # Train dataset  (Concatenate train manifest cleaned and dev manifest cleaned)
      asr_model.cfg.train_ds.manifest_filepath = './data/processed/tar/train/tarred_audio_manifest.json'
      asr_model.cfg.train_ds.is_tarred = True
      asr_model.cfg.train_ds.tarred_audio_filepaths='./data/processed/tar/train/audio_{0..127}.tar'

      asr_model.cfg.train_ds.batch_size = 16
      asr_model.cfg.train_ds.num_workers = 32
      asr_model.cfg.train_ds.pin_memory = True
      asr_model.cfg.train_ds.trim_silence = True

      # Validation dataset  (Use test dataset as validation, since we train using train + dev)
      asr_model.cfg.validation_ds.manifest_filepath = ['./data/processed/test_manifest_merged.json', './data/processed/dev_manifest_merged.json']
      asr_model.cfg.validation_ds.batch_size = 32
      asr_model.cfg.validation_ds.num_workers = 32
      asr_model.cfg.validation_ds.pin_memory = True
      asr_model.cfg.validation_ds.trim_silence = True
else:
    # Setup train, validation, test configs
    with open_dict(asr_model.cfg):    
      # Train dataset  (Concatenate train manifest cleaned and dev manifest cleaned)
      asr_model.cfg.train_ds.manifest_filepath = './data/processed/train_manifest_merged.json'
      asr_model.cfg.train_ds.batch_size = 16
      asr_model.cfg.train_ds.num_workers = 32
      asr_model.cfg.train_ds.pin_memory = True
      asr_model.cfg.train_ds.trim_silence = True

      # Validation dataset  (Use test dataset as validation, since we train using train + dev)
      asr_model.cfg.validation_ds.manifest_filepath = ['./data/processed/test_manifest_merged.json', './data/processed/dev_manifest_merged.json']
      asr_model.cfg.validation_ds.batch_size = 32
      asr_model.cfg.validation_ds.num_workers = 32
      asr_model.cfg.validation_ds.pin_memory = True
      asr_model.cfg.validation_ds.trim_silence = True

# Point to the new train and validation data for fine-tuning
asr_model.setup_training_data(train_data_config=asr_model.cfg.train_ds)
asr_model.setup_validation_data(val_data_config=asr_model.cfg.validation_ds)

# Use the smaller learning rate we set before
with open_dict(asr_model.cfg.optim):
  asr_model.cfg.optim.name="adamw"
  asr_model.cfg.optim.lr = 0.01
  asr_model.cfg.optim.betas = [0.8, 0.25]  # from paper
  asr_model.cfg.optim.weight_decay = 0.001  # Original weight decay
  asr_model.cfg.optim.sched.warmup_steps = None  # Remove default number of steps of warmup
  asr_model.cfg.optim.sched.warmup_ratio = 0.05  # 5 % warmup
  asr_model.cfg.optim.sched.min_lr = 1e-5
  asr_model.cfg.optim.sched.max_steps = 50000

# Setup checkpointing and train
checkpoint_callback = ModelCheckpoint(
    save_top_k=50,
    monitor="val_wer",
    mode="min",
    dirpath="./checkpoint-dir-1024",
    filename="citrinet-DE-{epoch:02d}-{val_wer:04f}",
    save_on_train_epoch_end=True,
    every_n_epochs = 1
)

trainer = pl.Trainer(precision=16, 
                     devices=8, 
                     accelerator='gpu',   
                     strategy='ddp', 
                     max_epochs=500, 
                     log_every_n_steps = 100,
                     default_root_dir="./checkpoint-1024/",
                     callbacks=[checkpoint_callback],                      
                     accumulate_grad_batches=8 # For a global batch size of 16*8*8 = 1024
)

trainer.fit(asr_model)
trainer.save_to('de-asr-model.nemo')