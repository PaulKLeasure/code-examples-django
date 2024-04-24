
let selectOptionGroups = [];

// Get variable passed into <script id="..." 
// from dJango Template Language
if(document.getElementById('selectOptionGroups')){
   selectOptionGroups = JSON.parse(document.getElementById('selectOptionGroups').textContent); 
   console.log('selectOptionGroups', selectOptionGroups);
}


// APP
const searchUi = new Vue({
    delimiters: ["[[","]]"],
    el: '#app-search-ui',
    data: function() {
        return {
            selectOptionGroups: selectOptionGroups, 
            grp_defs: [],
            is_anded_or: false,
            query: [
                        {
                         "group":
                            { "and":[], "andOr":[], "exclude":[] },
                         "def":
                            { "and":[], "andOr":[], "exclude":[] }
                        }
                    ],
            url_qry_str: '',
            per_page_limit: 30,
            host: '',
            urlPath: '',
            urlQryInit: window.location.href,
            verbalize_query: ''
        }
    },
    mounted: function () {

            let self = this;
            this.host = window.location.host;
            this.urlPath = window.location.pathname;
            let segments = window.location.search.split('&');
            // Set self.url_qry_str based on address bar
            segments.forEach(function(seg, i){
                console.log('SEGS:('+i+')', seg );
                if(seg.startsWith('?q=')){
                    self.url_qry_str = seg.replace('?q=','');
                    console.log('QRY STR BASED ON ADDRESS:', self.url_qry_str);
                }
            });
            // Redpopulate this.query Obj based on address str
            // Group Headers First
            // Split off the comma sep'd stuff
            let segs = self.url_qry_str.split(',');
            let groups_str = segs[0];
            // Shift the Group Headers off the array
            segs.shift();
            console.log('SEGS:',segs);
            let groupHeaders = groups_str.split('^');
            console.log('groupHeaders',groupHeaders);
            // Group Headers First
            groupHeaders.forEach(function(hdr, i){
                if(hdr != ''){
                    if(hdr.charAt(0) =='~'){
                        self.query[0].group.andOr.push(hdr.replace('~',''));
                    }else{
                        self.query[0].group.and.push(hdr.replace('~',''));
                    }
                }
            });
            // Then definitons 
            segs.forEach(function(def,i){
                if(def !== ''){
                    if(def.charAt(0) == '~'){
                        let andedOrDefs = def.split('~')
                        that = self
                        andedOrDefs.forEach(function(ddef, ii){
                            if(ddef.length > 1){
                                that.query[0].def.andOr.push(ddef.replace('~',''));
                            }
                        });
                    }
                    if(def.charAt(0) == '-'){
                        self.query[0].def.exclude.push(def.replace('-',''));
                    }
                    if(def.charAt(0) != '~' && def.charAt(0) != '-'){
                        self.query[0].def.and.push(def);
                    }
                }   
            });
            console.log('Rebuilt QueryObjectGROUP', self.query[0].group);
            console.log('Rebuilt QueryObjectDEF', self.query[0].def);
            // per page limit based on address bar
            segments.forEach(function(seg, i){
                if(seg.startsWith('limit=')){
                    self.per_page_limit = seg.replace('limit=','');
                }
            });
            this.urlQueryVerbalizer();
    },
    methods: {
        perform_search(){
            const protocol =  window.location.protocol;
            //let host = 'http://127.0.0.1:8000/';
            let pagePath = 'search/';
            let url = protocol+"//" + this.host + this.urlPath + '?q=' + this.url_qry_str + '&limit=' + this.per_page_limit;
            location.href = url;
            //console.log('perform_search()', protocol, this.host, url);
        },
        perform_reset(){
            this.url_qry_str = '';
            this.verbalize_query = '';
            this.query = [{"group":{"and":[],"andOr":[],"exclude":[]},
                           "def":{"and":[],"andOr":[],"exclude":[]} }];
            console.log('RESET:', this.url_qry_str);
        },
        urlQueryStringBuilder(){
            str = '';
            self = this;
            this.query.forEach(function(union, i){
                // String up the ANDed(^) Option Group Headers by Name
                // eg. ^Finish%20Categories^Cabinets
                if(union.group.and.length > 0){ 
                    union.group.and.forEach(function(grpName, inx){
                        str += '^'+ grpName;
                    });
                }
                // String up the EXCLUDED (^-) Option Group Headers by Name
                // (Stubbed out not working yet in backend logic)
                // eg. ^Finish%20Categories^~Cabinets 
                //if(union.group.exclude.length > 0){ 
                //    union.group.exclude.forEach(function(grpName, inx){
                //        str += '^-'+ grpName;
                //    });
                //}
                // String up the ANDed OR (^~) Option Group Headers by Name
                // eg. ^Finish%20Categories^~Cabinets 
                if(union.group.andOr.length > 0){ 
                    union.group.andOr.forEach(function(grpName, inx){
                        str += '^~'+ grpName;
                    });
                }
                // String up the ANDed (,) definition IDs
                // eg. ,45,687,1456,987
                if(union.def.and.length > 0){                
                    union.def.and.forEach(function( defId, inx){
                        str +=  ',' + defId;
                    });
                };  
                if(union.def.andOr.length > 0){ 
                    str +=  ','
                    union.def.andOr.forEach(function( defId, inx){
                        str +=  '~' + defId;
                    });
                };
                // String up the EXCLUDED (,-) definition IDs
                // eg.  ,-123,-468,-890
                if(union.def.exclude.length > 0){ 
                    union.def.exclude.forEach(function( defId, inx){
                        str +=  ',' + '-' + defId;
                    });
                };
            });
            
            // remove leading comma if any
            str = (str.charAt(0) === ',')? str.substring(1): str;
            console.log('QYERY STRING (before):', this.url_qry_str);
            this.url_qry_str = str;
            console.log('QYERY STRING (after):', this.url_qry_str);
            this.urlQueryVerbalizer();
        },
        urlQueryVerbalizer(){
            self = this;
            this.query.forEach(function(union, i){
                let verb = 'Select file assets ';
                let vAnd = '';

                if(union.group.and.length > 0){ 
                    union.group.and.forEach(function(grpName, inx){
                        vprim = (inx == 0)? 'with ANY options in ': '';
                        vAnd = (inx > 0)? ' AND ': '';
                        const grpNamePieces = grpName.split('%20');
                        const cleanGroupName = grpNamePieces.join(' ');
                        verb += vprim + vAnd + "'" + cleanGroupName + "'";
                        vprim = '';
                    });
                }
                if(union.group.andOr.length > 0){ 
                    verb += (union.group.and.length > 0)?  " AND (" : " with ANY options in " ;
                    union.group.andOr.forEach(function(grpName, inx){
                        vOR = (inx > 0)? ' OR ': ''; 
                        const grpNamePieces = grpName.split('%20');
                        const cleanGroupName = grpNamePieces.join(' ');
                        verb += vprim + vOR + "'"+ cleanGroupName+ "'";
                        vprim = '';
                    });
                    verb += (union.group.and.length > 0)?  ")" : "" ;
                    
                }
                // String up the ANDed (,) definition IDs
                // eg. ,45,687,1456,987
                if(union.def.and.length > 0){  
                    union.def.and.forEach(function( defId, inx){
                        if(inx == 0){
                            vprim = ' with definition ID(s) '; 
                            if(union.group.and.length > 0 || union.group.and.length > 0){
                               vprim = (inx == 0)? ' AND with definition ID(s) ': ''; 
                            }
                        }             
                        vAnd = (inx > 0)? ' AND ': '';
                        verb += vprim + vAnd + defId;
                        vprim = '';
                    });
                };  
                // String up the ANDed (,~) OR definition IDs
                // eg.  ,~123~468~890
                if(union.def.andOr.length > 0){    
                    verb += " AND (";
                    union.def.andOr.forEach(function( defId, inx){
                        console.log('VERBALIZER ANDED ORS', defId);
                        vprim = (inx == 0)? '': '';
                        vOR = (inx > 0)? ' OR ': '';
                        verb += vprim + vOR + defId;
                        vprim = '';
                    });
                    verb += " ) ";
                    
                };
                // String up the EXCLUDED (,-) definition IDs
                // eg.  ,-123,-468,-890
                if(union.def.exclude.length > 0){ 
                    verb += " but excludeing (";
                    union.def.exclude.forEach(function( defId, inx){
                        vAnd = (inx > 0)? ' AND ': '';
                        verb += vprim + vAnd + defId;
                        vprim = '';
                    });
                    verb += " ) ";
                    
                };
                console.log('VERBAL QYERY:', verb);
                self.verbalize_query = verb;
            });
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
        update_search_query(arr){
            // Add section as needed to the oobject then parse to dreat the string
            let unionIdx = arr[0];
            let dataType = arr[1];
            let qryAction = arr[2];
            let qryActionVal = arr[3];

            if( dataType == 'group'){
                if(qryAction == 'add'){
                    if(this.is_anded_or){
                        this.query[unionIdx].group.andOr.push(qryActionVal);
                        deDupifier(arrIn)
                    }else{
                        this.query[unionIdx].group.and.push(qryActionVal);
                    }
                }
                if(qryAction == 'exclude'){
                   this.query[unionIdx].group.exclude.push(qryActionVal);
                }
                if(qryAction == 'clear'){
                    var index = this.query[unionIdx].group.and.indexOf(qryActionVal);
                    if(index > -1){
                       this.query[unionIdx].group.and.splice(index, 1); 
                    }   
                    var index = this.query[unionIdx].group.andOr.indexOf(qryActionVal);
                    if(index > -1){
                       this.query[unionIdx].group.andOr.splice(index, 1); 
                    } 
                    var index = this.query[unionIdx].group.exclude.indexOf(qryActionVal);
                    if(index > -1){
                       this.query[unionIdx].group.exclude.splice(index, 1);
                    } 
                }
            }

            if( dataType == 'def'){
                if(qryAction == 'add'){
                    if(this.is_anded_or){
                        this.query[unionIdx].def.andOr.push(qryActionVal);
                    }else{
                        this.query[unionIdx].def.and.push(qryActionVal);
                    }
                }
                if(qryAction == 'exclude'){
                   this.query[unionIdx].def.exclude.push(qryActionVal);
                }
                if(qryAction == 'clear'){
                    var index = this.query[unionIdx].def.and.indexOf(qryActionVal);
                    if(index > -1){
                       this.query[unionIdx].def.and.splice(index, 1); 
                    }   
                    var index = this.query[unionIdx].def.andOr.indexOf(qryActionVal);
                    if(index > -1){
                       this.query[unionIdx].def.andOr.splice(index, 1); 
                    } 
                    var index = this.query[unionIdx].def.exclude.indexOf(qryActionVal);
                    if(index > -1){
                       this.query[unionIdx].def.exclude.splice(index, 1);
                    } 
                }
            }
            console.log('Q', this.query[unionIdx]);
            this.deDupifier(unionIdx);
            this.urlQueryStringBuilder();
        },
        deDupifier(idx){
            let tempSet = new Set(this.query[idx].group.and);
            this.query[idx].group.and = [...tempSet];
            tempSet = new Set(this.query[idx].group.andOr);
            this.query[idx].group.andOr = [...tempSet];
            tempSet = new Set(this.query[idx].def.and);
            this.query[idx].def.and = [...tempSet];
            tempSet = new Set(this.query[idx].def.andOr);
            this.query[idx].def.andOr = [...tempSet];
            tempSet = new Set(this.query[idx].def.exclude);
            this.query[idx].def.exclude = [...tempSet];
        }
    }
});