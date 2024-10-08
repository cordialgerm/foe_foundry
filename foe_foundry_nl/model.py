# from transformers import DistilBertTokenizer, DistilBertForMaskedLM
# import torch


# def load_model(
#     use_saved: bool = True,
# ) -> tuple[DistilBertForMaskedLM, DistilBertTokenizer]:
#     if use_saved:
#         output_dir = "./model"

#         # Load the fine-tuned model
#         model = DistilBertForMaskedLM.from_pretrained(output_dir)

#         # Load the tokenizer
#         tokenizer = DistilBertTokenizer.from_pretrained(output_dir)
#     else:
#         # Load pre-trained DistilBERT tokenizer and model
#         tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")
#         model = DistilBertForMaskedLM.from_pretrained(
#             "distilbert-base-uncased",
#             proxies={
#                 "http": "http://proxy-dmz.intel.com:912",
#                 "https": "http://proxy-dmz.intel.com:912",
#             },
#         )

#     device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#     model.to(device)
#     return model, tokenizer
