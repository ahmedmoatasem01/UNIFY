from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

model_path = r"E:\bart-large-cnn"

print("Loading model...")

tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSeq2SeqLM.from_pretrained(model_path)

summarizer = pipeline(
    "summarization",
    model=model,
    tokenizer=tokenizer
)

print("Model loaded!")

text = """
Artificial intelligence (AI) is intelligence demonstrated by machines.
AI research is defined as the study of systems that perceive their environment and take actions that maximize their chance of achieving their goals .
 Colloquially, the term "artificial intelligence" is often used to describe machines (or computers) that mimic "cognitive" functions that humans associate with the human mind, such as "learning" and "problem solving". 
 As machines become increasingly capable, tasks considered to require "intelligence" are often removed from the definition of AI, a phenomenon known as the AI effect. For instance, optical character recognition is frequently excluded from things considered to be AI, having become a routine technology.
"""

summary = summarizer(text, max_length=120, min_length=40, do_sample=False)

print("\n===== SUMMARY =====")
print(summary[0]["summary_text"])
