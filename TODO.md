# To-Do
- [ ] Test the error dialog boxes.
- [ ] Multiple Operations: 
	- For each store, loop and execute the single operation, example., if we have to create a webhook the callback url will be same, so exectute the same code for all/selected stores in loop.
	- Another example for particular store, bulk publishing/unpublishing
- [ ] Increase row count in table [Dynamic]
* Webhook creation in bulk => Update feature is working, but lagging && Next Page function is working && Prev Page function is working
* Combobox for owner_resource => editing this value is not possible? Check if create works with this
* Remove old code/files not required

## Other Stuff
- What is the status of Scripts/Assets
- What is the issue with Image Upload in Smart Collection? 

- Select all checkbox when checkbox header is clicked => Not Working => But double clicking the header checks/unchecks all the boxes

- Some fields are "numbers". Upgrade Field class for that. => Now there is a NumberField base class: DoubleField, IntField are derived classes. Unused yet. => Customers, orders tables use it



# NOT WORKING:
- script tag and assets => Script Tags are working => Asset value field is empty on tables, because it is not sent by the server => Asset creation is not tested => Asset creation does not work


- Smart Collection adding image => Check its functions => Check ImageField at assets also => Cannot upload images, "Image upload failed. Could not generate an image extension name."

- <s> Order creation is more complex than editor allows </s>

TO BE DETERMINED:
* Do bulk operations in bulk if possible => Does not seem possible on shopify objects, but maybe classes
-> In Webhooks Creation Table, why do you have 2 buttons Create and Save? => Create button can be used for creating duplicates.
-> Customer & Order Editor not working => From Customer and Order Tables/Editors, object fields are removed because they cause a crash => Customer creator has "bad request" crashes => Found no such crash, test further


DONE:
In Editing table for Metafields/Webhooks, we do not require these fields
As these are not editable, and can be viewed in the table directly

-> updated_at
-> created_at
-> owner_id
-> admin_graphql_id
STATUS: I removed "admin_graphql_api_id" also

Also Remove these from Webhooks Table,
-> fields
-> metafield_namespaces
-> private_metafield_namespaces
STATUS: Removed

* Add dialog boxes to show errors. => Implemented, not tested => It now prints traceback for exceptions
* Update tables on every change => Editors and Rule Editor does so. Create button of tables and publish button does not. => Publishing updates the table
* Vertically align TextField text => Now it shows only one line anyway
-> Format Date and Time when you display it in table (dd/mm/yy & hh:mm:ss) => Converted to IST => converted to (dd/mm/yy & hh:mm:ss) format
* CollectionListings and Pages do not have Editors yet => Pages do not require one. => CollectionListings has a working editor, needs to be modified => All working
-> Existing values of Image SRC and Alt text should be placed in the field => Done
-> Does delete button work? => It does
* On creation of fields on editors, add a middle function which filters field characteristics AND fix create keys / readonly keys stuff => Editor create mode is fixed and filters applied
* Disable Mock buttons => No mock buttons left

* Make table responsive
- [ ] Getting this error ***cannot unpack non-iterable NoneType object***, when exporting specific columns to csv.
- [ ] The functionality of Update Button should also work when we DOUBLE CLICK
- [ ] Clean code and put .ui files in seperate folders 
- [ ] App is crashing and shutting down if not able to retrieve data from shopify api, it is due to the pagination code. Check if the object is None, if it is not None, then only call the pagination code
- [ ] Instead of create and save two buttons, keep only Save button. Don't need duplicate content.


# Pages Table & CollectionListings Table
-> Instead of having another popup to publish/unpublish. Make something like: 
   User selects multiple rows, and clicks a button PUBLISH or unpublish
   Then loop through the rows and publish / unpublish accordingly.
   So remove create 	and edit button and replace with publish/unpublish.
   STATUS: Pages Table is done. CollectionListings do not support such a feature => CollectionListing editor works

* Bulk edit => Assets && Stores are not done => Asset bulk edit is working => Only stores do not support bulk edit => All supports.
-> Add checkboxes for each row	=> Delete operation done => Publish operations are also done => Bulk edit is on wait => Bulk edit works on everywhere but stores => It works on stores too
* Select all checkbox when checkbox header is clicked => Done
* Check Pagination => Pagination loads all the pages now, and that may be a problem => Next Page, Prev Page buttons for all sorts of tables
* Some fields are "numbers". Upgrade Field class for that. => Now there is a NumberField base class: DoubleField, IntField are derived classes. Unused yet. => Customers, orders tables use it
* StoresTable does not support exporting as CSV anymore (fix getAllItemsPaginated method) => Fixed
* Make it tabbed. => When a tab is clicked for the first time, it is updated so it loads
