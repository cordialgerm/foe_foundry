from pathlib import Path

import torch
from sentence_transformers import (
    SentenceTransformer,
    SentenceTransformerTrainer,
    SentenceTransformerTrainingArguments,
    losses,
    models,
)
from transformers import (
    BertForMaskedLM,
    BertTokenizer,
    PreTrainedModel,
    PreTrainedTokenizer,
)

model_dir = Path(__file__).parent.parent / "models"
mlm_model_dir = model_dir / "mlm-finetuned"
mlm_model_dir_rel = mlm_model_dir.relative_to(Path(__file__).parent.parent)

st_model_dir = model_dir / "st-finetuned"
st_model_dir_rel = st_model_dir.relative_to(Path(__file__).parent.parent)


def load_model_for_mlm(
    use_saved: bool = True,
) -> tuple[PreTrainedModel, PreTrainedTokenizer]:
    mlm_model_dir.mkdir(parents=True, exist_ok=True)

    if use_saved:
        pre_trained_model = mlm_model_dir
    else:
        pre_trained_model = "bert-base-uncased"

    tokenizer = BertTokenizer.from_pretrained(pre_trained_model)
    mlm_model = BertForMaskedLM.from_pretrained(pre_trained_model)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    mlm_model.to(device)  # type: ignore
    return mlm_model, tokenizer


def load_sentence_embedding_model(use_saved: bool = True):
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
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    return model
