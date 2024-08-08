import store from '../store.js';

import { getReport, deleteReport } from '../apiBackEnds/reportApi.js';


export default {
    data(){
        return {
            selectedReport: {},
            reportId: '',
            reportLoaded: false,
        }
    },
    created () {
        this.reportId = this.$route.params.rid; 
        this.fetchReport();
    },
    components: {
    },
    methods: {
        fetchReport() {
            getReport(this.reportId).then(function(response) {
                this.selectedReport = response.data.data;
                this.reportLoaded = true;
            }.bind(this));
        },
        toMarkDown(markData){
            return marked.parse(markData)
        },
        delReport(oid){
            deleteReport(oid).then(function(response){
                window.location.href = '/a'
            }.bind(this))
        }
    },
    template: /*html*/`
        <div class="m-2 p-4">
            <h1 class="pb-4"><span><i class="bi bi-file-earmark-text me-2"></i></span>{{ selectedReport.name }}</h1>
            <button type="button" @click="delReport(selectedReport.oid)" class="btn btn-outline-danger me-2">Delete report<i class="bi bi-trash ps-1"></i></button>
            <div class="row">
                <div v-if="reportLoaded" class="col-md-8 offset-md-2">
                    <div class="border rounded shadow p-5">
                        <div v-html="toMarkDown(selectedReport.content)"></div>
                    </div>
                </div>
            </div>
        </div>
    `
}
    
