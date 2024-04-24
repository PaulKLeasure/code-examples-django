

NOTE:

Working on cache_functions_mongo.py

 -  Saving to cache  (local so far)
 -  Pulling from cache -- needs work
 - Then set it up for DocumentDB

ISSUE CACHEing SCRIPTS:  
    504 Timeout issue  and server hangup
RESOLVED SO FAR WITH: 
    Use a seperate utility server to run the caching scripts.
    http://34.198.224.179/api/textbot/build-alttext-cache?templateId=5
    Use a Docker SERVER with no nginx load balancer
    Up the time on the Load Balancer Attribue:    Idle timeout: 1800 seconds
    NOTE: May have to manually start the python server (checking on this)
    



THEN DEPLOY to DEV for QA


"""  
Fetch Template(s):
  api/alttext/template  get all templates data 
  api/alttext/template/?id=<id>  get specific templates data 

Fetch Alt Text:
  api/alttext/text?assetId=<asset id>&path=<path>&overrideCache=<boole default false>
  api/alttext/text?assetId=595310&path=/cabinet-finishes-browser

Test Alt Text By Image (returns all templates that apply to image):
  /api/alttext/template-test?assetId=<ID>
  /api/alttext/template-test?assetId=<Filename>

Build Cache:
  api/textbot/build-alttext-cache  (defaults to ALL templates)
  api/textbot/build-alttext-cache/?templateId=<id> (specific template)
  RECOMMENDATIONS:
  - Run this in its own util instance so that it can refresh cache often 
    without casuing latency on the primary iVault Service API
