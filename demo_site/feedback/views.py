import json
from django.shortcuts import render
from django.http import JsonResponse
from .models import FeedBack

# Create your views here.
def feedback(request):
    req = dict(request.POST)
    feedback = parse_serialize_array(req)
    feedback_object = FeedBack(
        citation_text=feedback['citation_text'], 
        citation_text_quality=int(feedback['citation_text_quality']), 
        citation_intent_quality=int(feedback['citation_intent_quality']), 
        comments=feedback['comment'])
    feedback_object.save()

    return JsonResponse({"success": True})


def parse_serialize_array(data):
    feedback_item_names = []
    feedback_item_values = []

    for k, v in data.items():
        if 'name' in k:
            feedback_item_names.append(v[0])
        elif 'value' in k:
            feedback_item_values.append(v[0])
    
    results = {name: value for name, value in zip(feedback_item_names, feedback_item_values)}
    return results