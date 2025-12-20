# from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# # Load model once
# tokenizer = AutoTokenizer.from_pretrained("kipperdev/bart-summarizermodel")
# model = AutoModelForSeq2SeqLM.from_pretrained("kipperdev/bart-summarizermodel")


# def ai_summarize_text(text):
#     """
#     Summarizes text using the BART HF model
#     """
#     inputs = tokenizer(text, max_length=1024, truncation=True, return_tensors="pt")
#     summary_ids = model.generate(
#         inputs["input_ids"],
#         max_length=200,
#         min_length=50,
#         length_penalty=2.0,
#         num_beams=4,
#         early_stopping=True
#     )

#     return tokenizer.decode(summary_ids[0], skip_special_tokens=True)
