# code-examples
Paul Leasure

### NOTES
This repository contains some individual module files that were part of an Asset Management API. Select the modules from within the repository to view the code.

## A few examples of Django modules for an Asset Management API

__core:__  Provided the core CRUD functionality for assets, asset options, and option groups.

__search:__ Provided the ability to perform complex searches.

__searchTemplates:__ Provided the ability for admin to memorize complex searches.

__uploader:__ Provided the ability to perform batch uploads of assets to an S3 bucket. This worked along with TagBot.

__tagBot:__ TagBot worked with the Uploader module to automate handling complex assignments of option tags to assets.

__batchTagger:__ Enables the ability to edit search result batches of assets at a time.

__altTextBot:__ A system for creating text based on individual asset options while being sensitive to specific contexts.

__assetFilterNav:__ A backend admin for configuring customized filters for context specific search menus. 
