import store from './store.js';
import { askirApi, genintsumApi, listProjects, listInReqs, saveReport } from './backend.js';


const app = Vue.createApp({
    data(){
        return {
            irs: [
            ],
            queryInput: '',
            contextText: '',
            intsum:'',
            showSpinAskOsainta: false,
            showIntSumSpinner: false,
            selectedReference: {},
            selectedProject: {},
            projects: [],
            projectId: '',
            reportName: '',
            showSaveReportBadge: false,
        }
    },
    created () {
        this.projectId = this.getProjectIdParam()
        this.initIcpPage()
        this.initIrs(this.projectId)
    },
    
    components: {
    },
    methods: {
        queryOsainta(){
            this.showSpinAskOsainta = true
            if (this.queryInput === '' || this.projectId === '') {
                console.error('queryInput is empty or projectId is empty.')
                this.showSpinAskOsainta = false
                return
            }
            askirApi(JSON.stringify({context: this.contextText, user_query: this.queryInput, projectId: this.projectId})).then(function(response) {
                this.irs.push(response.data)
                this.queryInput = ''
                this.showSpinAskOsainta = false
            }.bind(this))
        },
        generateIntSum(){
            this.showIntSumSpinner = true
            genintsumApi(JSON.stringify({context: this.contextText, irs: this.irs})).then(function(response) {
                this.intsum = response.data.intSum
                this.showIntSumSpinner = false
            }.bind(this))
        },
        toMarkDown(markData){
            return marked.parse(markData)
        },
        setSelectedRefence(reference){
            this.selectedReference = reference
            this.$refs.referenceModalBtn.click()
        },
        hasUrlParam(paramName) {
            const urlParams = new URLSearchParams(window.location.search);
            return urlParams.has(paramName);
        },
        getProjectIdParam(){
            if (this.hasUrlParam('projectId')) {
                const projectId = new URLSearchParams(window.location.search).get('projectId');
                return projectId
            } else {
                console.error('No projectId parameter found.');
                return ''
            }
        },
        initIcpPage(){
            listProjects().then(function(response) {
                this.projects = response.data.data
                var proj = this.findProjectByOid(this.projectId)
                if (proj !== null) {
                    this.selectedProject = proj
                }
            }.bind(this))
        },
        initIrs(projectId){
            listInReqs(projectId).then(function(response) {
                this.irs = response.data.data
            }.bind(this))
        },
        setProject(project){
            window.location.href = `/icp?projectId=${project.oid}`;
        },
        isEmptyObject(obj) {
            return Object.keys(obj).length === 0 && obj.constructor === Object;
        },
        findProjectByOid(oid){
            let result = null;
            for (let i = 0; i < this.projects.length; i++) {
                if (this.projects[i].oid === oid) {
                    result = this.projects[i];
                    break;
                }
            }
            return result
        },
        saveAsReport(){
            this.showSaveReportBadge = true
            if (this.reportName === '') {
                console.error('reportName is empty.')
                this.showSaveReportBadge = false
                return
            }
            saveReport(JSON.stringify({reportName: this.reportName, reportContent: this.intsum, reportProjectId: this.projectId})).then(function(response) {
                setTimeout(() => {
                    this.showSaveReportBadge = false;
                }, 3000); // Set timeout to 3 seconds
            }.bind(this))            
        }
    },
    template: /*html*/`
    <div class="mb-5">
        <p class="">Create project on <a href="/a">Dashboard</a> or select below</p>
        <template  v-if="projects.length > 0">
            <div class="btn-group">
                <button class="btn btn-outline-primary dropdown-toggle px-4" type="button" data-bs-toggle="dropdown" aria-expanded="false">
                    {{ selectedProject && selectedProject.name ? selectedProject.name : 'Select Project' }}
                </button>
                <ul class="dropdown-menu" style="max-height: 200px; overflow-y: auto;">
                    <li v-for="project in projects" class="dropdown-item" :class="selectedProject.oid == project.oid ? 'active' : ''" @click="setProject(project)" >{{project.name}}</li>
                </ul>
            </div>
            <span class="text-muted ms-2 p-1">Selecting project will save questions and answers to the project and you will be able to view them again.</span>
            
        </template>

        <template v-if="!isEmptyObject(selectedProject)">
            <hr class="my-5 py-1">
            <h4 class="bg-warning p-2 rounded" >Start asking Osainta. Add context (optional) </h4>
            <p class="text-muted">Add knowledge base to help Osainta improve its responses <span><a href="/a/knowledges">Knowledge base page</a></span> </p>

            <div class="mb-3">
                <label for="contextText" class="form-label">(Optional) Add context to help Osainta answer your questions then click Ask Osainta button with your query.</label>
                <textarea v-model="contextText" class="form-control" id="contextText" name="contextText" rows="10" required placeholder="Paste an article here."></textarea>
            </div>
            
            <div class="border bg-light p-2 rounded mb-3">
                <div class="mb-3">
                    <label for="query_input" class="form-label">Ask for your intelligence requirements:</label>
                    <textarea v-model="queryInput" class="form-control" id="query_input" rows="3" name="query_input" placeholder="What is OSINT? Give me a SWOT analysis of OSINT." required></textarea>
                </div>
                <div v-if="showSpinAskOsainta">
                    <span  class="badge bg-info text-dark mx-2">Please wait...</span>
                </div>
                <div>
                    <button @click="queryOsainta" type="button" class="btn btn-dark">Ask Osainta</button>
                    <p class="text-muted">Please check below responded IRs and you ask.</p>
                </div>
            </div>

            <hr class="my-5 py-1 rounded-pill"/>

            <h4 class="bg-warning p-2 rounded" >Response for IRs</h4>
            <div class="border p-4 rounded">
                <h4>Browse below for responded IRs:</h4>
                <p class="text-muted">Response will continue to be added below.</p>
                <div class="accordion" id="accordionExample">
                    <div v-for="(ir, index) in irs" :key="index" class="accordion-item">
                        <h2 class="accordion-header" :id="'heading' + index">
                            <button class="accordion-button" type="button" data-bs-toggle="collapse" :data-bs-target="'#collapse' + index" aria-expanded="true" :aria-controls="'collapse' + index">
                                {{ ir.irQuery }}
                            </button>
                        </h2>
                        <div :id="'collapse' + index" class="accordion-collapse collapse show" :aria-labelledby="'heading' + index" data-bs-parent="#accordionExample">
                            <div class="accordion-body">
                                <div v-html="toMarkDown(ir.irAnswer)"></div>
                            </div>
                            <div class="bg-light p-2 rounded">
                                <p class="ms-3">References (if any) click to show more: <span v-for="(ref, index) in ir.irReference" :key="index" class="text-decoration-underline text-small text-primary ms-3" @click="setSelectedRefence(ref)">{{ref.knowledgeName}}</span></p>
                            </div>
                            
                        </div>
                    </div>
                </div>
            </div>

            <hr class="my-5 py-1 rounded-pill"/>

            <h4 class="bg-warning p-2 rounded" >Intelligence summary</h4>
            <div v-if="showIntSumSpinner">
                    <span  class="badge bg-info text-dark mx-2">Please wait...</span>
                </div>
            <div>
                <p class="text-muted">Generate an intelligence summary. This will consider all of your IRs above. The greater the IRs and its reponses are the better the intsum result is.</p>
                <button @click="generateIntSum" type="button" class="btn btn-success">Generate INTSUM</button>
            </div>
            
            <div class="p-4 m-4 border rounded">
                <div  v-html="toMarkDown(intsum)"></div>
                <template v-if="intsum !== ''">
                    <div class="border rounded shadow-sm mt-4 p-4">
                        <div class="input-group mb-3">
                            <span class="input-group-text" id="basic-addon1">Report name: (required)</span>
                            <input v-model="reportName" type="text" style="max-width: 500px;" class="form-control" placeholder="Report name" aria-label="Report name" aria-describedby="basic-addon1">
                        </div>
                        <button @click="saveAsReport" type="button" class="btn btn-outline-info">Save as report</button>
                        <p  class="text-muted">Save this as report under the same project. You can view this report on <a href="/a">dashboard project page.</a></p>
                        <div v-if="showSaveReportBadge">
                            <span  class="badge bg-info text-dark mx-2">Saving report. Please wait...</span>
                        </div>
                    </div>
                </template>
                
            </div>
        </template>

        <hr class="my-5 py-1 rounded-pill"/>
    

        <!-- Button trigger modal -->
        <button hidden ref="referenceModalBtn" type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#referencesModal">
            Launch demo modal
        </button>
        <!-- Modal -->
        <div class="modal fade" id="referencesModal" tabindex="-1" aria-labelledby="referencesModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="referencesModalLabel">{{selectedReference.knowledgeName}}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        {{selectedReference.chunk}}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    `
})
app.use().mount('#icd_app')