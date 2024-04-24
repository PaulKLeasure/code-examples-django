
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
                        elem = document.getElementById("upload-prog-"+ upload.incr );
                        elem.innerHTML = resp.data.resp_msg;
                        // Mark each file as uploaded if successful
                        self.batchUploads[idx]['uploaded'] = resp.data.uploaded;
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