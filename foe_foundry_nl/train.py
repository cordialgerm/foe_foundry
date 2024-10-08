from transformers import DataCollatorForLanguageModeling, Trainer, TrainingArguments

from ..rapg.rapg.data import load_dataset
from .model import load_model


def train_model():
    print("Beginning Training...")
    model, tokenizer = load_model(use_saved=True)

    custom_tokens = [
        "###",
        "##",
        "#",
        "***",
        "**",
        "*",
        "Armor Class",
        "AC",
        "HP",
        "Hit Points",
        "STR",
        "DEX",
        "CON",
        "WIS",
        "CHA",
        "INT",
        "DC",
        "Difficulty Class",
        "Challenge Rating",
        "CR",
        "<Entity>",
        "</Entity>",
        "<MonsterName>",
        "</MonsterName>",
        "<SpellName>",
        "</SpellName>",
        "<CreatureType>",
        "</CreatureType>",
    ]
    tokenizer.add_tokens(custom_tokens)

    model.resize_token_embeddings(len(tokenizer))

    print("Loading fine-tuning dataset...")
    dataset = load_dataset()

    def tokenize_function(examples):
        return tokenizer(
            examples["text"], truncation=True, padding=True, max_length=512
        )

    print("Tokenizing fine-tuning dataset...")
    tokenized_dataset = dataset.map(tokenize_function, batched=True)

    # Data collator for MLM - handles masking of tokens
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=True,
        mlm_probability=0.15,  # Mask 15% of tokens
    )

    # Define training arguments
    training_args = TrainingArguments(
        output_dir="./results",  # output directory
        num_train_epochs=3,  # number of training epochs
        per_device_train_batch_size=16,  # batch size per device during training
        logging_dir="./logs",  # directory for storing logs
        logging_steps=10,
        eval_strategy="epoch",  # evaluate at the end of each epoch
    )

    # Initialize the Trainer for MLM fine-tuning
    trainer = Trainer(
        model=model,  # the MLM model
        args=training_args,  # training arguments
        train_dataset=tokenized_dataset["train"],  # training dataset
        eval_dataset=tokenized_dataset["test"],  # evaluation dataset
        data_collator=data_collator,  # Data collator for MLM
    )

    # Fine-tune the model using Masked Language Modeling
    print("Begin fine-tuning...")
    trainer.train()
    print("Fine-tuning complete!")

    print("Saving Model to ./model")
    output_dir = "./model"
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    print("Model saved!")
