


## iVault TextBot API

## How textBot alt Text works

- Templates are created using token that are named exactly after option Headers. Each template is filtered by the following:
  - Path: Each template must be associated with a client-side website URI path
  - Recursive Path: Set as True or Fasle, a recursive path means to include all paths recursivly under the specified path.
  - Required IDs: Optionaly a template may require that an asset must be associated with a list of specified option ids.
  - Group Header: Optionaly requires that there must be at least one option within a specified Group Header.
- On a client-side website, when iVault is used to filter and search for assets, the developer must include the client-side website URI path from which the search is performed so that it may be associated with a template.
- To prevent slowing the application, cron scripts run to calculate the alt texts in advance and then are cached.
- The website url path from which the image is pulled is passed in via the request object. 
  -  eg. ?id=<asset-id>&path=<some-path> 
- The methods fetchAssetAltTextById(<id>, <path>)  and  fetchAssetsAltTexts(<list of Dicts>, <path>) are used to fetch cached alt text.
- Alt text is fetched only if it exists in cache. False is returned if nothing in cache.


## API Endpoints:

**Fetch Template(s):**

    /api/alttext/template  get all templates data 
    /api/alttext/template/?id=<id>  get specific templates data 

**Fetch Alt Text:**
  
    /api/alttext/text?assetId=<asset id>&path=<path>&overrideCache=<boole default false>
    /api/alttext/text?assetId=595310&path=/cabinet-finishes-browser

**Test Alt Text By Image (returns all templates that apply to image):**
  
    /api/alttext/template-test?assetId=<ID>
    /api/alttext/template-test?assetId=<Filename>

**Build Cache:**
  
    /api/textbot/build-alttext-cache  (defaults to ALL templates)
    /api/textbot/build-alttext-cache/?templateId=<id> (specific template)
  
    RECOMMENDATIONS:
    
    - Run this in its own util instance so that it can refresh cache often without casuing latency on the primary iVault Service API

# Testing



### Use the iVault Admin UI Alt Text Testor

```
   https://ivaulr-admin.wellbornservices.com/alt-text-template?mode=template-tester

   Enter the filename of the asset and click the "Run test" button.

```

### Testing from the iVault Admin UI Search Console

```
- When performing a seacrh from the search console, include a parameter named "testAltTextPath" in the URL address bar.

    eq.
        https://ivaulr-admin.wellbornservices.com/search/?testAltTextPath=/order-cabinet-sample-chip
```



## Database

### **Table:**  altTextBot_alttexttemplate
### **Columns:**
```
  - path*
    - The "slug" or path from root where this template applies
    - Must be at least "/"
    - eg.    /path-to-page

  - recursive 
    - If "truthy"  then recursivley search the path for a match, otherwise must match exact path.
    - eg. (boolean 1 or 0)

  - required_ids 
    - eg. [1275,1011, 167]
    - The image asset must have these ids assigned to it in the database
   
  - grp_header (optional) eg.  Product Lines
    - Matches any images with IDs that are within a valid Group Heder.
    - In case the same image has to diff grp_header values -- then what??
    - eg.  Product Lines  or Sample Chips

  - template
    - This is the text that uses the token syntax to insert the values from within a given Group of options.
    - If mutiple values then they will be "grammeratized".
    - eg. This is template text that uses a {{Valid Toke}} such as {{Finishes}}
```
### **Table:**  altTextBot_alttextcache
### **Columns:**
```
  - ssetId
    - The id of the asset associated with the cached alt text.

  - fileNamepath
    - The filename of the asset associated with the cached alt text.

  - path
    - The "slug" or path from root where this template appliesh.

  - altText
    - The cached alt text.

  - templateId
    - The id of the template associated with the cached alt text.
```

...
