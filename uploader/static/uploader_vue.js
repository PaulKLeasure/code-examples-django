// VUE for UPLOADER app

let preUploadData = [];
let selectOptionGroups = [];
if(document.getElementById('preUploadData')){
   preUploadData = JSON.parse(document.getElementById('preUploadData').textContent); 
   console.log('preUploadData', preUploadData[0]);
}
if(document.getElementById('selectOptionGroups')){
   selectOptionGroups = JSON.parse(document.getElementById('selectOptionGroups').textContent); 
   console.log('selectOptionGroups', selectOptionGroups);
}

console.log('preUploadData', preUploadData);
console.log('selectOptionGroups', selectOptionGroups);

//////////////////////////////////////////////////////////
// COMPONENTS
//////////////////////////////////////////////////////////
Vue.component('uploaderaccordian', {
    props: [
            'batch_update_preupload_options',
            'filedat', 
            'option_groups',
            'remove_upload',
            'configurator'
            ],
    template: `
        <div :id="'upload-'+seq" class="assetContainer" :class="'asset-'+filedat.id">
          <article>
            <div class="card">
              <div class="card-header" :id="'header-'+seq"  @click="toggle = ! toggle">
                <p  class="mb-0">
                   <span v-if="configurator && filedat.existing_asset" class="col-left-01 has-text-warning">
                    <i class="fas  fa-exclamation"></i>
                    <i class="fas  fa-caret-square-up"></i>
                   </span>
                   <span v-if="configurator && !filedat.existing_asset" class="col-left-01 has-text-info">
                    <i class="far  fa-caret-square-up"></i>
                   </span>
                   <span v-if="configurator" class="col-left-02" :data="seq" @click="deleteUpload(seq)" >
                    <i class="fa  fa-trash" aria-hidden="true"></i>
                   </span>
                   <span v-if="configurator" class="upload-file-incriment">({{ filedat.incr }})</span>
                   <span v-if="configurator" class="upload-file-id is-warning">({{ filedat.human_readable_id }})</span>
                   <span class="upload-file-name">File: {{ fileNameDisplay }} </span>
                   <span :id="uploadProgressIndicator" class="upload-progress">
                   <?xml version="1.0" encoding="UTF-8" standalone="no"?></span>
                </p>
              </div>
              <div :id="'msg-body-'+filedat.id" class="card-body message-body" v-show="toggle">
                <div v-if="!configurator" >
                  <a :href="filedat.s3_ivault_uri" ><img :src="filedat.s3_ivault_uri" height="50px" /></a>
                  <p>{{ filedat.search_string }}</p>
                </div>

                <div v-if="configurator" class="card-body asset-images">
                    <div v-if="filedat.existing_asset" class="float-sm-left  mx-3 my-3 existing-img">
                        <h2>Existingin Image</h2>
                        <img :src="existingImgSrc" :alt="filedat.id" />
                    </div>
                    <div class="float-sm-left  mx-3 my-3 new-img">
                        <h2>New Image</h2>
                        <img :src="upldImgSrc" :alt="filedat.id" />
                    </div>
                </div>
                <div v-if="configurator" class="card-body asset-values">

                  <ul class="list-group mx-1 my-3 w-100">
                    <li v-for="opt in filedat.options" :key="opt.id" class="w-100">
                      <span class="float-sm-left w-35">
                        <button class="remove-value-button btn btn-warning btn-sm" type="button" 
                                :value="'remove~'+opt.id+'~'+opt.groupName+'~'+opt.definition"
                                @click="update_local_preupload_options" > - </button>
                        <button class="batch-add-value-button btn btn-success btn-sm" type="button" 
                                :value="'add~'+opt.id+'~'+opt.groupName+'~'+opt.definition"
                                @click="batch_update_preupload_options" > Batch Add </button>
                        <button class="batch-remove-value-button btn btn-danger btn-sm" type="button" 
                                :value="'remove~'+opt.id+'~'+opt.groupName+'~'+opt.definition" 
                                @click="batch_update_preupload_options" > Batch Remove </button>
                      </span>
                      <span class="float-sm-left ml-2 option-def">
                        <span class="w-100" v-bind:class="{'is-batch-option':opt.isBatch, 'is-local-option':(!opt.isBatch)}">({{opt.id}})  {{ opt.groupName }}:  <span class="font-weight-bold"> {{ opt.definition }}</span></span>
                      </span> 
                    </li>
                  </ul>
                  <div :id="seq+'-add-option-'+filedat.id" class="add-option-container">
                    <br />
                    <label :for="'selectOptionGroups_'+filedat.id">Add options</label><br />
                    <select v-model="selectedOptionGroup" v-on:change="get_opt_grp_definintions" :id="seq+'_selectOptionGroups_'+filedat.id" class="selectOptionGroups form-control">
                      <option value="0">none</option>
                      <option v-for="grpOpt in option_groups" :value="grpOpt.groupName">{{ grpOpt.groupName }}</option>
                    </select>
                    <div :id="seq+'_optionDefinitionsContainer_'+filedat.id" class="optionDefinitionsContainer">
                      <ul class="list-group mx-1 my-3">
                        <li v-if="grp_defs" v-for="def in grp_defs" :key="def.id" >
                          <button class="add-value-button btn btn-success btn-sm" type="button" 
                                  :value="'add~'+def.id+'~'+def.groupName+'~'+def.definition" 
                                  @click="update_local_preupload_options" > + </button>
                          <button class="batch-add-value-button btn btn-success btn-sm" type="button" 
                                  :value="'add~'+def.id+'~'+def.groupName+'~'+def.definition"
                                  @click="batch_update_preupload_options" > Batch Add </button>
                          <button class="batch-remove-value-button btn btn-warning btn-sm" type="button" 
                                  :value="'remove~'+def.id+'~'+def.groupName+'~'+def.definition" 
                                  @click="batch_update_preupload_options" > Batch Remove </button>
                          <span>({{ def.id }})  <span class="font-weight-bold"> {{ def.definition }}</span></span>
                        </li>
                      </ul>
                    </div>
                    <div class="seq+'_selectedDefinitionsContainer'"></div>  
                   </div>
                </div><!-- card body -->
              </div>
            </div>
          </article>
        </div>`,
    data: function() {
        return {
            seq: this.filedat.incr,
            assetId: this.filedat.id,
            upldImgSrc: this.filedat.temp_img_path, 
            existingImgSrc: this.filedat.s3_ivault_uri,
            toggle:false,
            fileNameDisplay: this.filedat.fileName.replace('/media/',''),
            selectedOptionGroup: null, 
            groupDefsReady: false,
            uploadProgressIndicator: 'upload-prog-'+this.filedat.incr,
            uploaded: this.filedat.uploaded,
            grp_defs: []
        }
    },
    mounted: function() {
        //console.log('MOUNTED');
        this.sortFileDatOptions();
    },
    methods: {
        deleteUpload(seq){
            if(confirm('Delete row '+ seq +'! Are you sure!')){
                this.remove_upload(seq);
            }
            this.toggle = !this.toggle; // prevent accordian click from opening the div
        },
        async get_opt_grp_definintions(e){
            let self = this; // Avoid the "scope gatcha"
            const val = e.target.value;
            let qParam = '?optionGroupName='+ val;
            let url = 'ajax/opt-grp-values/'+qParam; 
            //fetch(url,{ method: "GET"})
            axios.get(url)
            .then(function(response){
                self.grp_defs = response.data;
            })
            .catch(function (error) {
                errMsg = 'Error! Could not reach the API. ' + error
                console.error('AJAX ERROR:', errMsg)
            });
        },
        update_local_preupload_options(e){
            // ///////////////////////////////////////////////////////
            // UPDATE in PREP for a FULLY COMMITED UPLAOD To S3.
            // ///////////////////////////////////////////////////////
            let self = this; // Avoid the "scope gatcha"
            const val = e.target.value;
            const params = e.target.value.split("~");
            const mode = params[0];// eg. add, remove, batch-add, batch-remove
            const optId = params[1];
            const optGrpName    = params[2];
            const optDefinition = params[3];
            console.log('SELECTED SINGLE DEF:('+mode+') ', e);
            const newOptionStr = '{"id":'+optId+', "groupName":"'+optGrpName+'", "definition":"'+optDefinition+'", "isBatch": 0}';
            const newOption  = JSON.parse(newOptionStr);
            if(mode ==='add'){
                // Ensure option list has not suplicates
                let isDuplicateOption = false;
                self.filedat.options.forEach(function(opt, i){
                    if(opt.id == newOption.id){isDuplicateOption = true}
                });
                if( !isDuplicateOption ){
                    self.filedat.options.push(newOption);
                    // Sort Options by groupName --> Definitions
                    self.sortFileDatOptions();
                    //self.filedat.options.sort(function(a,b){
                    //    let alpha = a.groupName + a.definition;
                    //    let beta  = b.groupName + b.definition;
                    //    return (alpha > beta) ? 1 : -1 ;
                    //});
                }
            }
            if(mode ==='remove'){
                self.filedat.options.forEach(function(opt, i){
                    if(parseInt(opt.id) == parseInt(optId)){
                        self.filedat.options.splice(i,1);
                    }    
                });
            }
        },
        sortFileDatOptions: function(){
            this.filedat.options.sort(function(a,b){
                let alpha = a.groupName + a.definition;
                let beta  = b.groupName + b.definition;
                return (alpha > beta) ? 1 : -1 ;
            })            
        }
    }

});


// APPS
const appUploader = new Vue({
    delimiters: ["[[","]]"],
    el: '#app-uploader',
    data: function() {
        return {
            batchUploads: preUploadData,
            selectOptionGroups: selectOptionGroups,
            configurator: true
            //upload_in_progress: true,
            //upload_bar_anima: ''
        }
    },
    methods: {
        async batch_update_preupload_options(e){
            // ADDs and REMOVES options from the entire batch
            // PRIOR to uploading
            let self = this; // Avoid the "scope gatcha"
            const val = e.target.value;
            //const dat = e.target.data;
            console.log("BATCH DATA:", e);
            const params = e.target.value.split("~");
            const mode = params[0];// eg. add, remove, batch-add, batch-remove
            const optId = params[1];
            const optGrpName    = params[2];
            const optDefinition = params[3];
            const newOptionStr = '{"id":'+optId+', "groupName":"'+optGrpName+'", "definition":"'+optDefinition+'", "isBatch": 1}';
            const newOption  = JSON.parse(newOptionStr);

            if(mode ==='add'){
                self.batchUploads.forEach(function(obj,idx){  
                    // Ensure option list has not suplicates
                    let isDuplicateOption = false;
                    self.batchUploads[idx].options.forEach(function(opt, i){
                        if(opt.id == newOption.id){ 
                            //isDuplicateOption = true;
                            self.batchUploads[idx].options.splice(i,1);
                        }
                    });
                    if( !isDuplicateOption ){
                        self.batchUploads[idx].options.push(newOption);
                        // Sort EACH upload's options by groupName --> Definitions
                        self.batchUploads[idx].options.sort(function(a,b){
                            let alpha = a.groupName + a.definition;
                            let beta  = b.groupName + b.definition;
                            return (alpha > beta) ? 1 : -1 ;
                        });
                    }
                });
                
            }
            if(mode ==='remove'){
                self.batchUploads.forEach(function(obj,idx){
                    //console.log('BEFORE SPLICE['+idx+']',self.batchUploads[idx].options);
                    self.batchUploads[idx].options.forEach(function(opt, i){
                        //console.log('COMPARE:',opt.id, optId );
                        if(parseInt(opt.id) == parseInt(optId)){
                            //remove from array   
                            //console.log('SPLICE ACTION  splice('+i+',1)')  ;
                            self.batchUploads[idx].options.splice(i,1);
                        }
                    });
                });
            }                
        },
        batch_cancel(){
            if(confirm('Cancel ALL uploads in batch?')){
                window.location.href = '/upload/';
                let self = this; // Avoid the "scope gatcha"
                axios.defaults.xsrfCookieName = 'csrftoken';
                axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
                const payload = {'mode':'delet_all_temp_files','path':''};
                const data = JSON.stringify(payload);
                axios({
                    method:'POST',
                    url:'ajax/cancel-batch/',
                    headers:{
                        'Accept': 'application/json',
                        "Content-type": "application/json; charset=UTF-8",
                    },
                    data: data
                })
                .then(function(resp){ 
                    console.log('CANCEL RESP:', resp)
                }) 
                .catch(function (error) {
                    errMsg = 'Error! Could not reach the API. ' + error
                    console.error('AJAX ERROR:', errMsg)
                });
                }
            return false;
        },
        async batch_commit_upload(e){ 
            if(confirm('You are about to upload the entire batch. Proceed?')){
                const val = e.target.value;
                const decoder = new TextDecoder('utf-8')
                const csrfElem = document.getElementsByName("csrfmiddlewaretoken");
                const csrftoken = csrfElem[0].value;
                const data = JSON.stringify(this.batchUploads);
                console.log('CSRF', csrftoken);
                //const dat = e.target.data;
                console.log("BATCH batch_commit_pload(eventObj:val):", e, val);
                console.log('batchUploads', this.batchUploads);
                const url = 'ajax/commit-batch/';
    
                let self = this; // Avoid the "scope gatcha"
                //self.upload_bar_anima = '<img src="/iVault2/static/loading-bar-blue.gif" >';
                axios.defaults.xsrfCookieName = 'csrftoken';
                axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
    
                self.batchUploads.forEach(function(upload, idx){
                    //let that = self
                    elem = document.getElementById("upload-prog-"+ upload.incr );
                    //elem.innerHTML = '<img src="/iVault2/static/loading-bar-blue.gif" >';
                    elem.innerHTML = '<span>Uploading...</span> <svg xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.0" width="213px" height="10px" viewBox="0 0 128 6" xml:space="preserve"><path fill="#c0c0c0" fill-opacity="0.25" d="M3.034,0.054H8.081A2.973,2.973,0,1,1,8.081,6H3.034A2.973,2.973,0,1,1,3.034.054Zm14.6,0h5.047a2.973,2.973,0,1,1,0,5.946H17.638A2.973,2.973,0,1,1,17.638.054Zm14.6,0h5.047a2.973,2.973,0,1,1,0,5.946H32.242A2.973,2.973,0,1,1,32.242.054Zm14.6,0h5.047a2.973,2.973,0,1,1,0,5.946H46.846A2.973,2.973,0,1,1,46.846.054Zm14.6,0H66.5A2.973,2.973,0,1,1,66.5,6H61.45A2.973,2.973,0,1,1,61.45.054Zm14.6,0H81.1A2.973,2.973,0,1,1,81.1,6H76.054A2.973,2.973,0,1,1,76.054.054Zm14.6,0H95.7A2.973,2.973,0,1,1,95.7,6H90.658A2.973,2.973,0,1,1,90.658.054Zm14.6,0h5.047a2.973,2.973,0,1,1,0,5.946h-5.047A2.973,2.973,0,1,1,105.262.054Zm14.6,0h5.047a2.973,2.973,0,1,1,0,5.946h-5.047A2.973,2.973,0,1,1,119.866.054Z"/><g><path fill="blue" fill-opacity="1" d="M-26.993,0H-7.235A3,3,0,0,1-4.228,3,3,3,0,0,1-7.235,6H-26.993A3,3,0,0,1-30,3,3,3,0,0,1-26.993,0Z"/><animateTransform attributeName="transform" type="translate" values="16 0;30 0;44.5 0;59 0;74 0;88.5 0;103 0;117.5 0;132 0;147 0;160.5 0" calcMode="discrete" dur="990ms" repeatCount="indefinite"/></g></svg>';

                    axios({
                        method:'POST',
                        url:'ajax/commit-batch/',
                        headers:{
                            'Accept': 'application/json',
                            "Content-type": "application/json; charset=UTF-8",
                        },
                        data: upload
                    })
                    .then(function(resp){
                        console.log('UPLOAD AJAX RESPO:', resp.data.resp_msg);
                        console.log('UPLOAD AJAX RESPO:', resp.data);
                        elem_prog_bar = document.getElementById("upload-prog-"+ upload.incr );
                        //elem_body = document.getElementById("msg-body-"+ upload.id );
                        elem_prog_bar.innerHTML = resp.data.resp_msg;
                        //elem_body.innerHTML = 'DONE';
                        // Mark each file as uploaded if successful
                        self.batchUploads[idx] = resp.data;
                        console.log('self.batchUploads[idx]', self.batchUploads[idx])
                        // Turn off main configurator buttons
                        self.configurator = false;                     
                    }.bind(self))
                    .catch(error => {
                        elem = document.getElementById("upload-prog-"+ upload.incr );
                        elem.innerHTML = '<span class="error">ERROR: Connection failed</span>';                   
                        console.error('AJAX ERROR in batch_commit_upload()', error);
                    });
                }); 
            }// End if( confirmed )                
            else{ return false; }
        },
        removeUpload(seq){
            self = this;
            self.batchUploads.forEach(function(fileUpload,idx){
                // idx and seq are not nessesarily the same
                // So locate by seq but slice by idx
                if(fileUpload.incr == seq){
                    //console.log('Sequence matched deleting upload!', fileUpload.incr , seq);
                    self.batchUploads.splice(idx, 1);
                }
            });
        },
        sortAssetOptionsByGroupDefinitions(index){
            self.batchUploads[index].options.sort(function(a,b){
                let alpha = a.groupName + a.definition;
                let beta  = b.groupName + b.definition;
                return (alpha > beta) ? 1 : -1 ;
            });
        }       
    },
    component:[
        'uploaderaccordian' 
    ]

});