import os
import torch
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .apps import GeneratorConfig
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer
)

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

# Create your views here.
def index(request):
    return render(request, 'index.html')


def result(request):
    citing_context = request.POST.get('citing_context')
    cited_context = request.POST.get('cited_context')
    citing_input_type = request.POST.get('citing_input_type')
    model_type = request.POST.get("model_type")
    citation_intent = request.POST.get("citation_intent")
    model_path = GeneratorConfig.PRETRAINED_MODELS_PATH

    model_src = citing_context + " " + cited_context
    model_src = " " + \
        model_src.rstrip() if "t5" in model_type else model_src.rstrip()
    model_src = f'@{citation_intent} {process_source_input(model_src)}'

    pretrained_models_path = {
        "bart-abstract": os.path.join(model_path, "bart-cctgm-abs.bin"),
        "bart-title": os.path.join(model_path, "bart-cctgm-title.bin"),
        "t5-abstract": os.path.join(model_path, "t5-cctgm-abs.bin"),
        "t5-title": os.path.join(model_path, "t5-cctgm-title.bin"),
    }
    
    transformers_model_type = "facebook/bart-base" if model_type == "bart" else "t5-base"
    used_pretrained_models = f"{model_type}-{citing_input_type}"

    context = {
        "citation_text": generate_citation_text(model_src, transformers_model_type, pretrained_models_path[used_pretrained_models],
                                                num_beams=4, length_penalty=2),
        "citation_intent": citation_intent,
    }

    return render(request, 'result.html', context=context)


def use_task_specific_params(model, task):
    """Update config with summarization specific params."""
    task_specific_params = model.config.task_specific_params

    if task_specific_params is not None:
        pars = task_specific_params.get(task, {})
        model.config.update(pars)


def process_source_input(text):
    text = text.replace(
        '\n', ' ').replace("\r", " ").strip().lower()

    return text


def generate_citation_text(
    src: str,
    model_name: str,
    model_state_dict_path: str=None,
    device: str=DEVICE,
    fp16=False,
    prefix=None,
    **generate_kwargs,
) -> str:
    model_name = str(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(device)
    if fp16:
        model = model.half()

    if model_state_dict_path is not None:
        model.load_state_dict(torch.load(model_state_dict_path, map_location=torch.device('cpu')))

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    use_task_specific_params(model, 'summarization')

    if prefix is None:
        prefix = prefix or getattr(model.config, "prefix", "") or ""

    src = prefix + src
    tokenized_src = tokenizer(src, return_tensors="pt",
                              truncation=True).to(device)

    citation_text_preds = model.generate(
        input_ids=tokenized_src.input_ids,
        attention_mask=tokenized_src.attention_mask,
        **generate_kwargs,
    )

    citation_text = tokenizer.batch_decode(
        citation_text_preds, skip_special_tokens=True, clean_up_tokenization_spaces=True)

    return citation_text[0]
