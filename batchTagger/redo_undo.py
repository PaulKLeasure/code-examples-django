from pprint import pprint
from . import models
from . import serializers
from core.models import Asset, Option, ivault_t_search, ivault_t_options, ivault_t_vals
from core.serializers import AssetSerializer
from core.functions import assetOption_stringifier, selfHealAssetOptions, update_core_ivault_t_search_and_vals
from django.core.exceptions import ValidationError
from iv_logger.functions import commitLogEntryToDatabase, build_log_text, ensureLog
from django.db import transaction
import json


# todo: do we update the username each time or is it just for historical purposes on the first call?
def apply_selected_action_to_batch(item_id, action, username):
    log_mode = 'default'
    context = {}  
    context["message"] = "ERROR: Batch action: "+action+" had an error and was roleld back."
    context["success"] = False
    logMode = "batch"
    try:
        history_item = models.History.objects.get(id=item_id)
        if history_item:
            item = serializers.HistorySerializer(history_item, many=False)
            history_data = item.data
    except models.History.DoesNotExist:
        data = {"action": "undo", "saved": False, "id": False}
        return data

    assets_ids = history_data["asset_ids"]
    oids_added = history_data["oids_added"]
    oids_removed = history_data["oids_removed"]

    # Make these queries transactional so they will roll-back if there is an error
    # Trigger atomic transaction so loop is executed in a single transaction
    with transaction.atomic():
        i = 0
        for asset_id in assets_ids:
            i += 1
            # this is reverse
            #print(f"{action}: for asset {asset_id} oids_added: {oids_added} oids_removed: {oids_removed}")
            asset_item = get_asset_item(id=asset_id)
            #log_text_before_update = build_log_text("before update", "Asset", asset_item)
            #selfHealAssetOptions(asset_item)
            #ensureLog(asset_item)
            if asset_item:
                #This is needed so the logger can tell the diff befor and after
                log_text_before_update = build_log_text("before update","Asset",asset_item)
                asset_options_ids = asset_item.options.all().values_list('id', flat=True)
                asset_options = asset_item.options.all()
                # object list
                asset_options_list = []
                # id list used for stringify backwards compat
                asset_options_id_list = []
                # shallow copy of existing data
                for asset_id in asset_options_ids:
                    asset_options_id_list.append(asset_id)
                for opt in asset_options:
                    asset_options_list.append(opt)
                for removed_id in oids_removed:
                    #try:
                    # get the option
                    option = get_option_item(removed_id)
                    if action == 'undo':
                        if removed_id not in asset_options_id_list:
                            asset_options_id_list.append(removed_id)
                        if option not in asset_options_list:
                            asset_options_list.append(option)
                    elif action == 'redo':
                        if removed_id in asset_options_id_list:
                            asset_options_id_list.remove(removed_id)
                        if option in asset_options_list:
                            asset_options_list.remove(option)
                    #except ValueError as e:
                    #    print(f"action: {action}; error: {e}")
                    #    return {"action": action, "saved": False, "id": item_id, "error": f"Unable to find specified items in undo {action}"}
                for added_id in oids_added:
                    #try:
                    # get the option
                    option = get_option_item(added_id)
                    if action == 'undo':
                        if added_id in asset_options_id_list:
                            asset_options_id_list.remove(added_id)
                        if option in asset_options_list:
                            asset_options_list.remove(option)
                    elif action == 'redo':
                        if added_id not in asset_options_id_list:
                            asset_options_id_list.append(added_id)
                        if option not in asset_options_list:
                            asset_options_list.append(option)
                    #except ValueError as e:
                    #    print(f"action: {action}; error: {e}")
                    #    return {"action": action, "saved": False, "id": item_id, "error": f"Unable to find specified items in undo {action}"}
                # clear the option data from the object
                asset_item.options.clear()
                # rehydrate the asset_item options
                for opt in asset_options_list:
                    asset_item.options.add(opt)
                asset_item.search_string = ''
                asset_item.search_string = assetOption_stringifier(asset_options_id_list)
                #try:
                asset_item.full_clean()
                asset_item.save()
                #Serialize asset_item
                serializedAssetItem = AssetSerializer(asset_item, many=False)
                searialAssDat = serializedAssetItem.data
                #For backwards compatability with wellborn.com Curator
                f_name = searialAssDat['fileName'].replace("media", "").replace("/","")
                #print("NAME: "+f_name)
                s_string = str(searialAssDat['search_string'])
                timestampIn = searialAssDat['timestamp']
                optionIds = searialAssDat['search_string'].split("--")
                # print('================================')
                # print('--- ivault_t_search  DATA -----')
                # print('f_name = ' + f_name )
                # print('s_string = ' + s_string )
                # print('================================')
                # --- UPDATE core_ivault_t_search (legacy table) ----
                ivaultTSearchObject = ivault_t_search.objects.get(fileName=f_name.replace("%20", " "))
                ivaultTSearchObject.search_string = s_string
                ivaultTSearchObject.timestamp = timestampIn            
                ivaultTSearchObject.save(update_fields=['search_string','timestamp'])
                # --- UPDATE core_ivault_t_vals (legacy table) ----
                # Remove the ivault_t_vals prior to add back in the updated options
                ivaultTValsObjs = ivault_t_vals.objects.filter(fileName=f_name)
                for tValsObj in ivaultTValsObjs:
                    tValsObj.delete()
                for optId in optionIds:
                    if optId.strip() != "":
                        ivaultTValsObject = ivault_t_vals(fileName=f_name, optId=int(optId), selected="", option_group="", option_text="", resolution="")
                        ivaultTValsObject.save()
                #This will properly not log if transaction does not complete (tested)
                commitLogEntryToDatabase(username, "update", "Asset", asset_item, logMode, log_text_before_update)
                commitLogEntryToDatabase(":bkwd cmpatbl updt", "bkwd cmpatbl UPDATE", "ivault_t_search", ivaultTSearchObject, "batch-edited") 
                commitLogEntryToDatabase(":bkwd cmpatbl updt", "bkwd cmpatbl UPDATE", "ivault_t_vals", ivaultTValsObject, "batch-edited")
        # update history_item, set state to 0 for "undo"
        undo, redo = 0, 1
        action_state = undo if action == 'undo' else redo
        history_item.state = action_state
        history_item.save()
        context["success"] = True
        context["message"] = "Success: Batch action: "+action+" applied."
        #  Create LOG entry for the BATCH ACTION
        

    batch_action_data = {"batch_action_item_id":item_id, "action": action, "username": username, "success":context["success"]}   
    commitLogEntryToDatabase(username, action, "BatchTagHistory", history_item, logMode, json.dumps(batch_action_data)) 

    data = {"action": "undo", "saved": True, "id": item_id, "success":context["success"], "message":context['message'], "batch_action_data":batch_action_data}
    print("////////////////////////////////")
    print("     Batch Action Data     ")
    pprint(data)
    print("////////////////////////////////")
    return data


def get_asset_item(id):
    asset_item = Asset.objects.get(id=id)
    if asset_item:
        return asset_item
    else:
        return None


def get_option_item(id):
    option_item = Option.objects.get(id=id)
    if option_item:
        return option_item
    else:
        return None
