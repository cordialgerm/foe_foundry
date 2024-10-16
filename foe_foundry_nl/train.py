from pprint import pprint

from datasets import DatasetDict
from sentence_transformers import (
    SentenceTransformer,
    SentenceTransformerTrainer,
    SentenceTransformerTrainingArguments,
    losses,
    models,
)
from transformers import (
    DataCollatorForLanguageModeling,
    EarlyStoppingCallback,
    PreTrainedModel,
    PreTrainedTokenizer,
    Trainer,
    TrainingArguments,
)

from .data.background import load_background_dataset
from .data.monsters import load_triplet_loss_dataset
from .model import (
    load_model_for_mlm,
    mlm_model_dir,
    mlm_model_dir_rel,
    st_model_dir,
)


def fine_tune_bert_on_background_corpus(fresh: bool, skip_training: bool = False):
    if fresh and skip_training:
        raise ValueError("Cannot skip training when starting fresh")

    # load model and dataset
    print("Loading model and dataset...")
    model, tokenizer = load_model_for_mlm(use_saved=not fresh)
    dataset, n_train, n_test = load_background_dataset()
    print(
        f"Loaded {n_train + n_test} background documents. {n_train} for training and {n_test} for testing"
    )

    trainer, tokenized_dataset = _setup_mlm_trainer(model, tokenizer, dataset, n_train)

    if not skip_training:
        # Fine-Tune the model on the background corpus
        print("Fine-tuning model...")
        trainer.train()

        # Save the fine-tuned model
        print("Saving Model")
        trainer.save_model(str(mlm_model_dir_rel))
        tokenizer.save_pretrained(str(mlm_model_dir_rel))

    # measure performance on validation set
    print("Validation Metrics:")
    eval_result = trainer.evaluate(tokenized_dataset["validation"])  # type: ignore
    print("Validation Dataset Using Fine-Tuned Model:")
    pprint(eval_result)

    print("Baseline Dataset Using Pre-Trained Model:")
    model2, tokenizer2 = load_model_for_mlm(use_saved=False)
    trainer2, tokenized_dataset2 = _setup_mlm_trainer(
        model2, tokenizer2, dataset, n_train
    )
    eval_result2 = trainer2.evaluate(tokenized_dataset2["validation"])  # type: ignore
    pprint(eval_result2)

    print("Success!")


def fine_tune_bert_contrastive(fresh: bool = False, skip_training: bool = False):
    print(f"Loading MLM model from {mlm_model_dir}...")

    # Load the pre-trained BERT model for MLM
    word_embedding_model = models.Transformer(str(mlm_model_dir), max_seq_length=512)

    # Configure the Pooling layer for Semantic Search (Mean Pooling recommended)
    pooling_model = models.Pooling(
        word_embedding_model.get_word_embedding_dimension(),
        pooling_mode_mean_tokens=True,  # Use mean pooling for semantic search
        pooling_mode_cls_token=False,  # Don't rely on CLS token because we're using a fine-tuned BERT model for MLM
        pooling_mode_max_tokens=False,  # trying mean pooling for now for semantic search
    )
    model = SentenceTransformer(modules=[word_embedding_model, pooling_model])

    print("Generating triplet training data...")
    dataset, n_train, n_eval, n_test = load_triplet_loss_dataset()
    print(f"{n_train=}, {n_eval=}, {n_test=}")

    print("Fine-tuning model...")
    trainer = _setup_contrastive_trainer(model, dataset, n_train)
    trainer.train()

    print(f"Saving Model to {st_model_dir}...")
    model.save(str(st_model_dir))


def _setup_contrastive_trainer(
    model: SentenceTransformer, dataset: DatasetDict, n_train: int
) -> SentenceTransformerTrainer:
    num_train_epochs = 3
    train_batch_size = 16
    total_steps = (n_train // train_batch_size) * num_train_epochs
    warmup_steps = total_steps // 10

    train_loss = losses.TripletLoss(
        model=model,
        distance_metric=losses.TripletDistanceMetric.COSINE,
        triplet_margin=1.0,
    )

    trainer = SentenceTransformerTrainer(
        model=model,
        args=SentenceTransformerTrainingArguments(
            output_dir=str(st_model_dir),
            overwrite_output_dir=True,
            eval_strategy="epoch",
            save_strategy="epoch",
            logging_dir="./logs",
            logging_strategy="epoch",
            save_total_limit=2,  # Only save the last two models
            num_train_epochs=num_train_epochs,
            per_device_train_batch_size=train_batch_size,
            per_device_eval_batch_size=2 * train_batch_size,
            learning_rate=5e-5,
            lr_scheduler_type="cosine",
            warmup_steps=warmup_steps,
            load_best_model_at_end=True,
            save_steps=50,  # Save checkpoint every 500 steps
        ),
        loss=train_loss,
        train_dataset=dataset["train"],
        eval_dataset=dataset["eval"],
    )

    return trainer


def _setup_mlm_trainer(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizer,
    dataset: DatasetDict,
    n_train: int,
) -> tuple[Trainer, DatasetDict]:
    # tokenize data
    def tokenize_function(examples):
        return tokenizer(
            examples["text"], padding="max_length", truncation=True, max_length=512
        )

    tokenized_dataset = dataset.map(
        tokenize_function, batched=True, remove_columns=["text"]
    )

    # Set up Trainer
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer, mlm=True, mlm_probability=0.15
    )

    num_train_epochs = 10
    train_batch_size = 16
    total_steps = (n_train // train_batch_size) * num_train_epochs
    warmup_steps = total_steps // 10

    trainer = Trainer(
        model=model,
        args=TrainingArguments(
            output_dir=str(mlm_model_dir_rel),
            eval_strategy="epoch",
            save_strategy="epoch",
            logging_dir="./logs",
            logging_strategy="epoch",
            num_train_epochs=num_train_epochs,
            per_device_train_batch_size=train_batch_size,
            per_device_eval_batch_size=2 * train_batch_size,
            learning_rate=5e-5,
            lr_scheduler_type="cosine",
            warmup_steps=warmup_steps,
            load_best_model_at_end=True,
        ),
        train_dataset=tokenized_dataset["train"],  # type: ignore
        eval_dataset=tokenized_dataset["test"],  # type: ignore
        data_collator=data_collator,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=3)],
    )
    return trainer, tokenized_dataset
