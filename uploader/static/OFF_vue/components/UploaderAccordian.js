

Vue.component('uploaderaccordian', {
    props: [
            'batch_update_preupload_options',
            'filedat', 
            'option_groups',
            'remove_upload',
            'configurator'
            ],
    template: `
        <div :id="'upload-'+seq" class="assetContainer" :class="'asset-'+assetId">
          <article>
            <div :id="'header-'+seq" class="message-header" @click="toggle = ! toggle">
                <p>
                  <span v-if="! filedat.uploaded && filedat.existing_asset" class="col-left-01 has-text-warning">
                    <i class="fas  fa-exclamation"></i>
                    <i class="fas  fa-caret-square-up"></i>
                  </span>
                  <span v-if="! filedat.uploaded && !filedat.existing_asset" class="col-left-01 has-text-info">
                    <i class="far  fa-caret-square-up"></i>
                  </span>
                  <span v-if="! filedat.uploaded" class="col-left-02" :data="seq" @click="deleteUpload(seq)" >
                    <i class="fa  fa-trash" aria-hidden="true"></i>
                  </span>
                  <span class="upload-file-incriment">({{ seq }})</span>
                  <span class="upload-file-id is-warning">({{ filedat.human_readable_id }})</span>
                  <span class="upload-file-name">File: {{ fileNameDisplay }} </span>
                  <span :id="uploadProgressIndicator" class="upload-progress">
                  <?xml version="1.0" encoding="UTF-8" standalone="no"?></span>
                </p>
            </div>
            <div :id="'msg-body-'+assetId" class="message-body" v-show="toggle">

                <div v-if="! filedat.uploaded" class="asset-images">
                    <div v-if="filedat.existing_asset" class="existing-img">
                        <h2>Existingin Image</h2>
                        <img :src="existingImgSrc" :alt="assetId" />
                    </div>
                    <div class="new-img">
                        <h2>New Image</h2>
                        <img :src="upldImgSrc" :alt="assetId" />
                    </div>
                </div>

                <div v-if="! filedat.uploaded" class="asset-values">
                  <ul>
                    <li v-for="opt in filedat.options" :key="opt.id">
                        <button class="remove-value-button" type="button" 
                                :value="'remove~'+opt.id+'~'+opt.groupName+'~'+opt.definition"
                                @click="update_local_preupload_options" > - </button>
                        <button class="batch-add-value-button" type="button" 
                                :value="'add~'+opt.id+'~'+opt.groupName+'~'+opt.definition"
                                @click="batch_update_preupload_options" > Batch Add </button>
                        <button class="batch-remove-value-button" type="button" 
                                :value="'remove~'+opt.id+'~'+opt.groupName+'~'+opt.definition" 
                                @click="batch_update_preupload_options" > Batch Remove </button>
                        <span v-bind:class="{'is-batch-option':opt.isBatch, 'is-local-option':(!opt.isBatch)}">({{opt.id}}) {{ opt.groupName }}: {{ opt.definition }}</span>
                    </li>
                  </ul>
                  <div :id="seq+'-add-option-'+assetId" class="add-option-container">
                    <br />
                    <label :for="'selectOptionGroups_'+assetId">Add options</label><br />
                    <select v-model="selectedOptionGroup" v-on:change="get_opt_grp_definintions" :id="seq+'_selectOptionGroups_'+assetId" class="selectOptionGroups">
                      <option value="0">none</option>
                      <option v-for="grpOpt in option_groups" :value="grpOpt.groupName">{{ grpOpt.groupName }}</option>
                    </select>
                    <div :id="seq+'_optionDefinitionsContainer_'+assetId" class="optionDefinitionsContainer">
                      <ul>
                      <li v-if="grp_defs" v-for="def in grp_defs" :key="def.id" >
                        <button class="add-value-button" type="button" 
                                :value="'add~'+def.id+'~'+def.groupName+'~'+def.definition" 
                                @click="update_local_preupload_options" > + </button>
                        <button class="batch-add-value-button" type="button" 
                                :value="'add~'+def.id+'~'+def.groupName+'~'+def.definition"
                                @click="batch_update_preupload_options" > Batch Add </button>
                        <button class="batch-remove-value-button" type="button" 
                                :value="'remove~'+def.id+'~'+def.groupName+'~'+def.definition" 
                                @click="batch_update_preupload_options" > Batch Remove </button>
                        <span>({{ def.id }}) {{ def.definition }}</span>
                      </li>
                      </ul>
                    </div>
                    <div class="seq+'_selectedDefinitionsContainer'"></div>  
                   </div>
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
            fileNameDisplay: this.filedat.fileName.replace('/iVault2/media/',''),
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
            });
        },
        update_local_preupload_options(e){
            // ///////////////////////////////////////////////////////
            // UPDATE in PREP for a FULLY COMMITED UPLAOD.
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
