from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt
from . import batch
from . import paging
from . import redo_undo
from pprint import pprint
import json

history_params = ['id', 'undo', 'redo', 'page']

def get_user_from_token(request):
    token_key = request.META.get('HTTP_AUTHORIZATION').replace("Token ", "")
    user = Token.objects.get(key=token_key).user
    return user


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@csrf_exempt
def batch_tagger(request):
    payload = json.loads(request.body.decode("utf-8"))
    user = get_user_from_token(request=request)
    data = {}

    # Only authorized for user is admin
    if not user.is_admin:
        context = {"response_code": 401, "message": "Not authorized! " + user.username + " is not an admin.",
                   "success": "false"}
        return JsonResponse(context, safe=False)

    if payload:
        data = batch.save_history(data=payload, username=user.username)

    return JsonResponse({'data': data, 'username': user.username}, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def history(request):
    valid = False
    user = get_user_from_token(request=request)

    # Only authorized for user is admin
    if not user.is_admin:
        context = {"response_code": 401, "message": "Not authorized! " + user.username + " is not an admin.",
                   "success": "false"}
        return JsonResponse(context, safe=False)

    for param in history_params:
        if request.GET.get(param):
            valid = True
            break

    lookup_key = request.GET.get(param)
    data = {}

    if param == 'id':
        data = batch.get_item(item_id=lookup_key)
    elif param == 'page':
        data = paging.get_page(page=lookup_key)
    elif param == 'undo':
        data = redo_undo.apply_selected_action_to_batch(item_id=lookup_key, action='undo', username=user.username)
    elif param == 'redo':
        data = redo_undo.apply_selected_action_to_batch(item_id=lookup_key, action='redo', username=user.username)

    return JsonResponse({'history': True, 'param': param, 'data': data}, safe=False)
