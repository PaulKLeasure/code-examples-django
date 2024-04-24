
============================================================
  Assets may be searched with URL querieslike these:
  
  GET['q'] Stand for option optId
  Note the following syntax for options in the query
  
  A comma separated list of option opt_ids produces a set where all
  of the ids must be preseant for the asset to be included in set

  eg.
     ?q=xxx,yyy,zzz,eee
  READ: "xxx AND yyy AND zzz AND eee"
  
  Adding a negetive sign in front of an id means the id
  is excluded (must NOT be in the results)

  eg.
     ?q=xxx,-yyy,zzz,-eee
  READ: "xxx AND zzz BUT NOT yyy and NOT eee"
  
  Adding a ~ sign in from of an id means that id
  is an "AND'd OR" so all of the other ids must be
  present (or excluded) AND(ppp OR ddd OR qqq)
  eg.
     ?q=xxx,yyy,zzz,-eee,~ppp~ddd~qqq
  
  READ: "xxx AND yyy AND zzz 
        AND (ppp OR ddd OR qqq) BUT NOT eee"
  
   One can query for any value within and Option Group as follows.
   If you wish to look for any assets that contain any values
   form the 'Finish Categories' Option group or the 'Cabinets'
   Option group, the query Option group names are separated by
   a ^. A ^~ indicates the asset can have values from iether
   Option group (if more than one). Otherwise, it is assumed
   the assets must have any values from both all Options groups
   in the query.

  ?q=^Finish%20Categories^~Cabinets


  More Complicated example
     NOTE: When using ~ for AND'd ORs the digits within the 
           OR GROUP should only have a ~ between them.
           However, the OR GROUP should still be preceeded by
           a comma as the GROUP is being ANDED. If there are
           other AND'd or Excluded ids after the OR GROUP, then
           the OR GROUP needs to have a comma after it.
  
  
  ?q=^Finish%20Categories^~Cabinets,166,-171,~103~105,-142
  
  
============================================================
  The programm first breaks the query string into its comma 
  separated parts (CSP). The base query mode is defaulted to 
  "AND" meaning the CSPs are AND'd in the query. 
  Within each CSP IDs separated by ~ become "AND'd ORs".
  Excluding an ID is achieved with a - infornt of the ID.
  Excluding a group of "OR'd" IDs looks like this: ...,-|167-|567-|177,...
  This means that Assets can't have ANY of the exclusions. Put another way,
  the assets can not have 167 or 567 or 177 in the results.
  Assets with ANY of the exluded IDs will not show
  Excluding a group of "AND'd" IDs looks like this: 
  ...,-:167-:567-:177,.. <--same --> ...,-167,-567,-177...
  This means that Assets having ALL of the exclusion IDs will be excluded. 
  Assets with only some of the exclusion IDs WILL SHOW in results.
  Put another way, in order for the asset to not show, it must have
  167 and 567 and 177.
  BEST PRACTICE is to use the colon notation, ":", and avoid 
    having multiple comma separated neg IDs.
        BAD:   ...,-167,-567,-177... or ...,-167:-567,654,123,-177,..

        GOOD:  ...,-167-:567-:177,..






