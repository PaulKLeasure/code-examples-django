#from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from tagBot.models import TagBotModes, TagBotMapping
from tagBot.serializers import TagBotMappingSerializer
from core.models import Option
from django.core.exceptions import ObjectDoesNotExist
from core.serializers import OptionSerializer
from iv_logger.functions import commitLogEntryToDatabase, build_log_text
from django.http import JsonResponse
import pprint
pp = pprint.PrettyPrinter(indent=4)
from django.db.models import Q # filter using operators '&' or '|'


"""
This func is for initial development and testing
"""
def test(request):
	context = {}
	filename = request.GET.get('filename')
	mode = request.GET.get('mode')
	context["codes"] = []
	print( mode )

	if( mode == None ):
		raise Exception("TagBot URL nust include a `mode` parameter.")
	if( filename == None ):
		raise Exception("TagBot URL nust include a `filename` parameter.")
	
	nomenclatureSyntaxWriter()
	codes = process_filename_codes(filename, mode)
	# print("RETURNED CODES:")
	# pp.pprint(codes)
	context["codes"] = codes
	return JsonResponse(context, safe=False)

def fix_nomenclature(request):
	context = {}
	nomenclatureSyntaxWriter()
	return JsonResponse(context, safe=False)


"""
/////////////////////////////////////////////////////////////////////////////
Takes a filename and a mode and returns a list 
of IDs based on a combination of alpha code to ID mapping
and logic mapped to alpha codes 
/////////////////////////////////////////////////////////////////////////////
"""

def process_filename_codes(filename_in, mode_id, dryrun=False):
	optIdsRemovedByMappingAndLogic = []
	context = {}
	logMode = 'tagbot'
	log_msg = ""
	filename = codifyFilenameSuffix(filename_in)
	#tokenKey = request.META.get('HTTP_AUTHORIZATION').replace("Token ", "")
	#username_authenticatedByToken = Token.objects.get(key=tokenKey).user.usernam
	"""
	This returns a list of serialized Tagbot Mapping 
	Rule objects
	Queried by: 
	 - Any matching alphs codes marked with mode "ALL"
	 - Plus any matching alpha code with selected mode (if any)
	"""
	mappingRulesList = getMappingRulesPerFilenameAndMode(filename, mode_id)

	"""
	apply_simple_mapped_filters(mappinRulesList)
	  Extract and apply mapping Rules with no "~LOGIC"
	  Returns:
	  - ["filtered_ids"], a list of filtered option ids
	  - ["applied_logic"], data about applied logic
	  - ['option_results_data'], list of Option objects based on the filtered ids
	"""
	simpleMapData = apply_simple_mapped_filters(mappingRulesList, filename)
	#print("==============")
	#print('apply_simple_mapped_filters(mappinRulesIn)')
	#print("==============")
	#pp.pprint(simpleMapData)

	for removeId in simpleMapData['removed_ids']:
		optIdsRemovedByMappingAndLogic.append(removeId)

	idsFromSimpleMapping = simpleMapData['filtered_ids'] 
	codesFromFilename = filename.split('_')
	applied_logic = apply_logic_filters(idsFromSimpleMapping, filename, mode_id)
	filtered_ids = applied_logic['filtered_ids']
	
	for removeId in applied_logic['removed_ids']:
		optIdsRemovedByMappingAndLogic.append(removeId)

	#Deduplicate the list
	filtered_ids = list(dict.fromkeys(filtered_ids))

	log_msg += applied_logic['log_msg']
	log_msg += "IDs:" +"".join([str(elem)+"," for elem in filtered_ids])
	
	context['success'] = True 
	context['count'] = len(applied_logic['filtered_ids'])
	context['ids'] = applied_logic['filtered_ids']
	context['meta'] = {}
	context['meta']['filename_fragments'] = codesFromFilename 
	context['meta']['applied_logic'] = simpleMapData['applied_logic'] + applied_logic['applied_logic']
	
	mappedResults = simpleMapData['option_results_data']
	logicalResults = applied_logic['option_results_data']


	print('====== PROCESS =======')
	#print('mappedResults')
	#pp.pprint(mappedResults)
	print('====== PROCESS =======')
	print('optIdsRemovedByMappingAndLogic')
	pp.pprint(optIdsRemovedByMappingAndLogic)
	print('====== PROCESS =======')

	# Mash results together and dedupe and 
	# remove the exclusion with optIdsRemovedByMappingAndLogic
	optionResultsData = []
	for opt in mappedResults:
		if opt['id'] not in optIdsRemovedByMappingAndLogic:
			optionResultsData.append(opt)
	for opt in logicalResults:
		if opt['id'] not in optIdsRemovedByMappingAndLogic:
			if opt not in optionResultsData:
				optionResultsData.append(opt)

	#print('Updated Filtered optionResultsData')
	#pp.pprint(optionResultsData)

	context['meta']['option_results_data'] = optionResultsData
	context['meta']['log_msg'] = 'TagBot| filename:' + filename + ", " + log_msg
	pseudoObject = {}
	pseudoObject['fileName'] = filename_in  
	if not dryrun:
		commitLogEntryToDatabase("API", "TagBot:Dry Run", 'file:' + filename, pseudoObject, logMode, log_msg)

	return context


"""
Extract and apply "simple" (no ~LOGIC) mapping Rules
- Include optionId(s) if the set of alpha codes from the Rule::nomenclature
  is a subset of alpha codes from the filename
- Include optionId(s) if Rule::nomenclature contains '~DEFAULT'
Returns:
- ["filtered_ids"], a list of filtered option ids
- ["applied_logic"], data about applied logic
- ['option_results_data'], list of Option objects based on the filtered ids
"""
def apply_simple_mapped_filters(mappingRulesIn, filenameIn):
	context = {}
	filtered_ids_total = []
	logic_applied = []
	idsRemovedByMapping = []
	verbalMappingStr = ''
	# create set from filename alpha codes
	alphaCodesFromFilename = getAlphaCodesFromFilename(filenameIn)
	for rule in mappingRulesIn:
		if "~LOGIC" not in rule['nomenclature'] :
			filtered_ids = []
			logic_summary = {}
			# create set from rule's nomenclature
			alphaCodesFromRule = rule['nomenclature'].strip().replace("{","").replace("}","").split(',')
			# check if rule codes set is within filename set
			ruleApplies = set(alphaCodesFromRule).issubset(alphaCodesFromFilename)
			if ruleApplies or '~DEFAULT' in rule['nomenclature'] :
				if rule['optionIds']:
					ids = rule['optionIds'].split(",")
					for id in ids:
						#-------
						# Determine append or remove based on minus sign
						if '-' in id:
							absid = id.replace('-','')
							idsRemovedByMapping.append(int(absid))
							verbalMappingStr += " ~ this mapping REMOVED "+ str(absid)+". "
							if absid in ids: 
								print('Mapping removed this ID '+ absid)
								#origListOfIds.remove(absid)
						#-------
						if id not in filtered_ids :
							filtered_ids.append(id)
						if id not in filtered_ids_total:
							filtered_ids_total.append(id)
							logic_summary['tagbot_mapping_id'] = rule['id']
							logic_summary['tagbot_mapping_rule'] = "mapped " + rule['nomenclature'] + " to " + str(rule['optionIds'])
							logic_summary['logic'] = "Directly mapped " + str(id)
							logic_summary['applied_results'] = filtered_ids
							logic_summary['passed_condition_test'] = True
							if logic_summary not in logic_applied:
								logic_applied.append(logic_summary)
	
	context['verbalMappingStr'] = verbalMappingStr
	context["filtered_ids"] = filtered_ids_total
	context["applied_logic"] = logic_applied
	context["removed_ids"] = idsRemovedByMapping
	context['option_results_data'] = fetch_options_by_filtered_ids(filtered_ids_total)

	return context

"""
Fetch alpha code meta from dB based on filename

- Get alpha codes from file name
- Fetch tagbot mapping rules per alpha code
 - serialize each rule
- combine results in list and
- return list

 NOTE: This step gets the Rules that contain the alpha codes
       but does not perform the mapping logic at this point.
"""
def getMappingRulesPerFilenameAndMode(filename, mode_id = False):
	filenameCodeResults = []
	fnCodes = getAlphaCodesFromFilename(filename)

	for fncode in fnCodes:
		tagMappingObjectsPerAlphaCode = []
		nomenclature =[]
		# for each code, get the data mapping object(s) from the db table
		tagCode = "{"+fncode+"}"
		# Always include TAGS for mode=ALL (id = 1)
		query = Q(nomenclature__contains=tagCode) & Q(mode_id=1)
		# Always include ~DEFAULT for ALL mode
		query |= Q(nomenclature__icontains="~DEFAULT") & Q(mode_id=1)
		
		# Include specified mode tags
		if mode_id and int(mode_id) > 1:
			query |= Q(nomenclature__contains=tagCode) & Q(mode_id=mode_id)
			# Always include DEFAULT for specified mode
			query |= Q(nomenclature__icontains="~DEFAULT") & Q(mode_id=mode_id)

		tagMappingObjectsPerAlphaCode = TagBotMapping.objects.filter(query)
		
		for tagMapObj in tagMappingObjectsPerAlphaCode:			
			# Fetch the mode
			try:
				modeObj = TagBotModes.objects.get(pk=tagMapObj.mode_id)
			except ObjectDoesNotExist:
				return "ERROR: TagBotModes does not exist"

			# Serialize the results into a workable data object
			serializedTagMap = TagBotMappingSerializer(tagMapObj, many=False)
			serializedTagMapData = serializedTagMap.data
			serializedTagMapData['mode'] = modeObj.name
			if serializedTagMapData['optionIds'] is not None:
				serializedTagMapData['optionIds'] = serializedTagMapData['optionIds'].replace(" ","")
			if serializedTagMapData not in filenameCodeResults:
				filenameCodeResults.append(serializedTagMapData)

	return filenameCodeResults

	
"""
Extract alpha code logic from dB and apply results
"""
def apply_logic_filters(ids_input,filenameIn, mode_id):
	#print('===========  apply_logic_filters(ids_input, mode_id) ================')
	context = {}
	context['logic_applied'] = []
	context["removed_ids"] =[]
	filtered_ids_out = []
	filtered_ids = []
	logicObjsList = []
	logicList = []
	logic_applied = []
	answersList = []
	log_msg = ""
	answer = ""
	verbalLogicList = []

	# Create list of filename codes
	alphaCodesFromFilename = getAlphaCodesFromFilename(filenameIn)
	try:
		modeObj = TagBotModes.objects.get(pk=int(mode_id))
	except ObjectDoesNotExist:
		modeObj = False
		print("TagBotMode ObjectDoesNotExist "+ str(modeObj) + " in tagBot.functions.apply_logic_filters(ids_input,filenameIn, mode_id): ")

    # For each alphaCode
	# Fetch mapping rules that have "~LOGIC" in the nomenclature
	for alphaCode in alphaCodesFromFilename:
		tagCode = "{"+alphaCode+"}"
		# Always include TAGS from the "ALL" mode (id of 1)
		query = Q(nomenclature__icontains="~LOGIC") & Q(mode_id=1) & Q(logic__icontains=tagCode)
		query |= Q(nomenclature__icontains="~DEFAULT") & Q(nomenclature__icontains="~LOGIC") & Q(mode_id=1) & Q(logic__icontains=tagCode)
		# Include result for specified mode tags (eg. "SFK" with mode_id of 2)
		if modeObj and modeObj.id > 1:
			query |= Q(nomenclature__icontains="~LOGIC") & Q(mode_id=modeObj.id) & Q(logic__icontains=tagCode)
			# Always include DEFAULT for specified mode
			query |= Q(nomenclature__icontains="~DEFAULT") & Q(nomenclature__icontains="~LOGIC") & Q(mode_id=modeObj.id) & Q(logic__icontains=tagCode)

		logicObjects = TagBotMapping.objects.filter(query)
		for logicObj in logicObjects:
			if logicObj not in logicObjsList:
				logicObjsList.append(logicObj)

	#print('==================================================')
	#print('logicObjsList (' + str( len(logicObjsList)  )+")"  )
	#print('==================================================')
	#pp.pprint(logicObjsList)

	if logicObjsList:
		for logicObj in logicObjsList:			
			serializedLogic = TagBotMappingSerializer(logicObj, many=False)
			serializedLogicData = serializedLogic.data
			logicDict = {}
			theLogicArray = serializedLogicData['logic'].split('_')
			logicDict["tagbot_mapping_id"] = serializedLogicData['id']			
			""" VALIDATE LOGIC LIST  """
			if not '_IF:' in serializedLogicData['logic']:
				raise Exception( "Invalid logic string in record "+str(logicObj.id)+" missing `_IF:` ")
			if not '_THEN:' in serializedLogicData['logic']:
				raise Exception( "Invalid logic string in record "+str(logicObj.id)+" missing `_THEN:` ")
			"""
			Build a list of logic dictionaries from theLogicArray
			obtained by querying the TagBotMapping dB table
			"""
			for logicParts in theLogicArray:
				logicPart = logicParts.split(':')
				if logicPart[0] == 'IF':
					logicDict['ifCond'] = logicPart[1].replace("{","").replace("}","").strip()
					logicDict['statement'] = 'IF '+str(logicPart[1].strip())
				if logicPart[0] == 'THEN':
					logicDict['then'] = logicPart[1].strip()
					logicDict['statement'] += ' THEN '+str(logicPart[1].strip())
				if logicPart[0] == 'ELSE':
					logicDict['else'] = logicPart[1].strip()
					logicDict['statement'] += ' ELSE '+str(logicPart[1].strip())

			logicList.append(logicDict)
			log_msg = log_msg + " Logic:"+logicDict['statement']+' ' 
		"""
		Iterate and "digest" list of logic statements (logicList)
		NOTE:
		    - The logic dict contains 'ifCond', 'then' & 'else'
		    - The 'ifCond' may have comma sep's alpha codes.
		         - A comma in the 'ifCond' indicates a logical AND
		         - A minus sign (-) indicates an excluded alpha code
		             - exlcuded means it does NOT exist in the
		               list of filename alpa codes (nomenclature)
		         - eg. TTT,-BYY
		            Means it must have TTT "and" must not have BYY
		    - 'then'==> value(s) to apply when 'ifCond' is True
		    - 'else'==> value(s) to apply when 'ifCond' is False
			NOTE: 'else' is seldom if ever used.
		"""
		for logic in logicList:
			hasAlphaCodesRequiredByConditional = False
			excludedCodesPresentInConditional = False
			includedAlphCodes = []
			excludedAlphaCodes = []
			applied_logic = []
			verbalTESTLogicString = ""
			verbalLogicString = ""
			logic_summary = {}
			logic_summary['tagbot_mapping_id'] = logic["tagbot_mapping_id"]
			logic_summary['tagbot_mapping_rule'] = logic['statement']
			logic_summary['passed_condition_test'] = False
		
			# Determin AND'd set of alph codes by splitting them by commas (if there are any commas).			
			includedAlphCodes = logic['ifCond'].split(',')
			
			# Iterate and look to see if any have a minus sign
			for possibleAlphaCodeExclusion in includedAlphCodes:
				# Any alpha codes prefixed with "-" are
				# appened to the excludedAlphaCodes list (with minus sign removed) 
				if '-' in possibleAlphaCodeExclusion:
					excludedAlphaCodes.append(possibleAlphaCodeExclusion.replace('-',''))
					# remove this item from includedAlphCodes
					includedAlphCodes.remove(possibleAlphaCodeExclusion)

			# Determine:
			# Do ALL alpha codes AND'd by ~LOGIC conditional exist in alphaCodesFromFilename?
			if includedAlphCodes:
				hasAlphaCodesRequiredByConditional = set(includedAlphCodes).issubset(alphaCodesFromFilename)

			if (hasAlphaCodesRequiredByConditional):
				verbalTESTLogicString += 'TEST Inclusion '+ ', '.join(includedAlphCodes) + ' PASSED. '
				#print(verbalTESTLogicString, end = '')
			else:
				verbalTESTLogicString += 'TESTED Inclusion: '+ ', '.join(includedAlphCodes) + ' FAILED. '
				#print(verbalTESTLogicString, end = '')
			
			# Do ALL alpha codes excluded by ~LOGIC conditional exist in alphaCodesFromFilename?
			if excludedAlphaCodes :
				# See if logicly exluded letter codes are within the nomenclature
				excludedCodesPresentInConditional= set(excludedAlphaCodes).issubset(alphaCodesFromFilename)
			
				if excludedCodesPresentInConditional:
					verbalTESTLogicString += 'TESTED Excludion '+ ', '.join(excludedAlphaCodes) + ' FAILED. '
					#print(verbalTESTLogicString, end = '')
				else:
					verbalTESTLogicString += 'TESTED Exclusion '+ ', '.join(excludedAlphaCodes) + ' PASSED. '
					#print(verbalTESTLogicString, end = '')
			
			logic_summary['tested'] = verbalTESTLogicString

			# Create the conition string for feedback
			condStr = "Filename has "+str(includedAlphCodes)
			if len(excludedAlphaCodes) > 0 :
				condStr += " and not "+ str(excludedAlphaCodes)

			# Translate and apply the ~LOGIC
			if hasAlphaCodesRequiredByConditional and not excludedCodesPresentInConditional:
				"""
				Since the ID(s) required by the conditonal are present, and the IDs to be 
				excluded are NOT present, the logic of the `THEN` can be applied.
				"""
				conditionalStringOfIds = logic['then']
				data = applyIdStringSetToResultsList(ids_input, conditionalStringOfIds)
				filtered_ids = data['ids']
				verbalLogicString = "(IF) Condition: "+condStr+". "
				logic_summary['logic'] = verbalLogicString
				logic_summary['applied_results'] = data['verbalLogicStr']
				logic_summary['passed_condition_test'] = True
				#print(verbalLogicString)
				for removedId in data["removed_ids"]:
					#print('AppliedLogic ID Removed: ' + str(removedId))
					context["removed_ids"].append(removedId)
					#pp.pprint(context["removed_ids"])
			else:
				if 'else' in logic:
					conditionalStringOfIds = logic['else']
					data = applyIdStringSetToResultsList(ids_input, conditionalStringOfIds)
					filtered_ids = data['ids']
					verbalLogicString += "(ELSE) Condition: "+condStr+" not met. "
					logic_summary['logic'] = verbalLogicString
					logic_summary['applied_results'] = data['verbalLogicStr']
					logic_summary['passed_condition_test'] = True
					print(verbalLogicString)
					verbalLogicList.append(verbalLogicString)
					for removedId in data["removed_ids"]:
						#print('AppliedLogic ID Removed: ' + str(removedId))
						context["removed_ids"].append(removedId)
						#pp.pprint(context["removed_ids"])
				else: 
					verbalLogicString += "No condition is met leaving: " + (', '.join(filtered_ids)) 
					#print(verbalLogicString)
			
			logic_applied.append(logic_summary)	

	context['filtered_ids'] = filtered_ids
	#if 'data' in locals():
	#	for removedId in data["removed_ids"]:
	#		print('AppliedLogic ID Removed: ' + str(removedId))
	#		context["removed_ids"].append(removedId)
	#		pp.pprint(context["removed_ids"])
	context['option_results_data'] = fetch_options_by_filtered_ids(filtered_ids)
	context['applied_logic'] = logic_applied
	context['log_msg'] = log_msg
	return context 


"""
Take the list of ids that result from the logic and
applies them to the aggregate set of ids.
eg.  If the logic produces a result of 1132,555,-8876, then
     This function will add 1132 and 555 to origListOfIds
	 And remove 8876 from origListOfIds while aviding duplciates.
"""
def applyIdStringSetToResultsList(origListOfIds, strOfIdsToApply):
	context = {}
	context["removed_ids"] = []
	idsRemovedByLogic = []
	# Convert strOfIdsToApply to a py list
	idList = strOfIdsToApply.split(",")
	verbalLogicStr = "Applied tag IDs:"+ str(idList)
	#print('strOfIdsToApply')
	#pp.pprint(strOfIdsToApply)
	#print('origListOfIds')
	#pp.pprint(origListOfIds)
	for id in idList:
		# Determine append or remove based on minus sign
		if '-' in id:
			absid = id.replace('-','')
			idsRemovedByLogic.append(int(absid))
			verbalLogicStr += " ~ this logic REMOVED "+ str(absid)+". "
			if absid in origListOfIds: 
				print('absid = '+ absid)
				origListOfIds.remove(absid)		
		else:
			if id not in origListOfIds:
				origListOfIds.append(id)

	context['ids'] = origListOfIds
	for removedId in idsRemovedByLogic:
		context["removed_ids"].append(removedId)
	context['verbalLogicStr'] = verbalLogicStr
	#print('context')
	#pp.pprint(context)
	return context


"""
Fetch Asset Option Objects based on the filtered IDs
"""
def fetch_options_by_filtered_ids(filtered_ids_in = []):
	optionsData = []
	filtered_ids = []
	# ensure nermic ints
	for potentialyNonNumericId in filtered_ids_in:
		if potentialyNonNumericId.isnumeric():
			filtered_ids.append(int(potentialyNonNumericId))

	if filtered_ids:
		for oid in filtered_ids:
			try:
				optObj = Option.objects.get(id=oid)
				if(optObj):
					serializedOption = OptionSerializer(optObj,many=False)
					serialOptionData = serializedOption.data
					if serialOptionData not in optionsData:
						optionsData.append(serialOptionData)	
			except ObjectDoesNotExist:
				print("ObjectDoesNotExist "+ str(id) + " in tagBot.functions.fetch_options_by_filtered_ids(filtered_ids): ")
	return optionsData


"""
creates alpha codes from filename
"""
def getAlphaCodesFromFilename(fn):
	filename = codifyFilenameSuffix(fn)
	# Create list of filename codes
	return filename.split('_')

""" 
Converts the filename suffix to the underscore seprated
format of the filename so the Tagbot rules can be written 
against them.
"""
def codifyFilenameSuffix(fn):
	sufxs = ['.jpg','.JPG','.jpeg','.png','.PNG','.tif','.tiff','.TIFF','.TIF','.pdf','.PDF']
	for sufx in sufxs:
		if sufx in fn:
			convertedSuffix = sufx.upper().replace(".","_")
			return fn.replace(sufx,convertedSuffix)
	return fn


"""
Utility function for Data Preperation 

Idempotent string conversion to include curly braces

This function takes LOGIC data that has been
human entered without using { } around the filename
code and adds the {  } to the filename codes so it
can work with the logic.
eg. 
   In the dB table `tagBotMapping` column `nomentclature`:
   original string:  _IF:GNS,-INS_THEN:2905,-2906   becomes
   rebuilt string:   _IF:{GNS},{-INS}_THEN:2905,-2906
"""
def rebuildLogicStringSyntax():
	
	tagBotObjs = TagBotMapping.objects.filter(nomenclature__contains="~LOGIC")

	for tagBotObj in tagBotObjs:
		rebuiltLogicString = '';	
		# Split logic string into IF THEN ELSE sections
		logicSections = tagBotObj.logic.split("_")

		for section in logicSections:
			
			if ":" in section:
				# Split sections into Key Value
				keyValPair = section.split(":")
				key = keyValPair[0]
				vals = keyValPair[1]
				# for the "if" condition wrap the
				# alphaCodes in curly braces
				if '_IF' in key:
					# remove init curly braces if any
					vals.replace("{","").replace("}", "")
					alphaCodes = vals.split(",")
					builtAlphaCodes = ''
					for alphaCode in alphaCodes:
						rebuiltCode = "{"+alphaCode+"},"
						builtAlphaCodes += rebuiltCode

					vals = builtAlphaCodes.rstrip(",")
				# reconstruction
				rebuiltLogicString += "_"+key+":" + vals


"""
Utility function for Data Preperation 

Idempotent string conversion to include curly braces

This function takes nomeclature data that has been
human entered without using { } around the filename
code and adds the {  } to the filename codes so it
can work with the logic.
eg. 
   In the dB table `tagBotMapping` column `nomentclature`:
   original string:  RMD,INS,~LOGIC   becomes
   rebuilt string:   {RMD},{INS},~LOGIC
"""
def nomenclatureSyntaxWriter(nomenclatureIn = ''):
	rebuiltNomenclatureList = []
	
	tagBotObjs = TagBotMapping.objects.all()
	for tagBotObj in tagBotObjs:
		nomen_parts = tagBotObj.nomenclature.split(",")
		rebuilt_nomenclature = '';
		for nomenpart in nomen_parts:
			print("NOMEN PART ="+nomenpart)
			# remove all {  and  }
			nomenpart = nomenpart.replace("{","").replace("}", "")
			print("NOMEN PART ="+nomenpart)
			# check to ignore ~LOGIC (case insensitive)
			if nomenpart.lower() != "~logic":
				#pass
				rebuilt_nomenpart = "{"+nomenpart+"}"
			else:
				rebuilt_nomenpart = nomenpart
			# reconstruct with commas
			rebuilt_nomenclature += rebuilt_nomenpart+","
		
		tagBotObj.nomenclature = rebuilt_nomenclature.rstrip(",")
		tagBotObj.save()

"""
Utility function for Data Preperation 

Idempotent remove \r resulting from CSV import
"""
def optionIdStringCleanser():
	tagBotObjs = TagBotMapping.objects.all()
	for tagBotObj in tagBotObjs:
		tagBotObj.optionIds = tagBotObj.optionIds.replace("\r", "")
		tagBotObj.save()
