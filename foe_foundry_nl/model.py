from pathlib import Path

import torch
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
