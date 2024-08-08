import store from '../store.js';
import { addProject, listProjects, deleteProject} from './apiProject.js';
import { listReport } from '../apiBackEnds/reportApi.js';

export default {
    data(){
        return {
            projects: [
            ],
            selectedProject: {},
            newName: '',
            newDescription: '',
            newData: '',
            showErrorSave: false,
            showSpinAddProject: false,
            showSpinDelProject: false,
            reports: [],
        }
    },
    created () {
        this.initProjects()
        this.initReports()

    },
    components: {
    },
    computed: {
        myDetails () {
            return store.getMe()
        },
        filteredReportsByProjectId(){
            let filteredData = this.reports.filter(item => item.projectId === this.selectedProject.oid);
            return filteredData
        }
    },
    methods: {
        initProjects(){
            listProjects().then(function(response) {
                this.projects = response.data.data
            }.bind(this))
        },
        isEmptyObject(obj) {
            return Object.keys(obj).length === 0 && obj.constructor === Object;
        },
        setProject(project){
            this.selectedProject = project
        },
        saveProject() {
            if (this.newName === '' || this.newDescription === '') {
                this.showErrorSave = true
                setTimeout(() => {
                    this.showErrorSave = false;
                }, 3000);
                return
            }
            this.showSpinAddProject = true

            addProject(JSON.stringify({
                projectName: this.newName, 
                projectDescription: this.newDescription, 
                })).then(function(response) {

                this.newName = ''
                this.newDescription = ''
                this.showSpinAddProject = false
                this.initProjects()
                store.refreshMe()
            }.bind(this))
        },
        delProject(oid){
            this.showSpinDeldelProject = true
            deleteProject(oid).then(function(response){
                this.showSpinDelProject = false
                this.initProjects()
                this.setProject({})
            }.bind(this))
        },
        openIcp(oid){
            window.location.href = `/icp?projectId=${oid}`
        },
        initReports(){
            listReport().then(function(response) {
                this.reports = response.data.data
            }.bind(this))
        }
    },
    template: /*html*/`
        <div class="m-2 p-4">
            <h1 class="pb-4"><span><i class="bi bi-clipboard-plus me-2"></i></span>Dashboard</h1>
            <div class="shadow border rounded mt-1 p-3">
                <h3 class="" >Monitor your usage</h3>
                <div>
                    <p class="text-muted">Token available: <span class="text-dark fw-bold fs-1 p-1">{{myDetails?.tokenAvailable?.toLocaleString()}}</span></p>
                </div>
            </div>
            <hr class="my-5 py-1 rounded-pill"/>
            <h3 class="mt-4 p-2">Your projects</h3>
            <p>Manage your research by creating project, you can associate other objects such as ICP, IRs, report and more to a project.</p>
            <div class="row mt-4">
                <div class="col-4">
                    <button @click="setProject({})" type="button" class="btn btn-primary mb-4">Add new <i class="bi bi-file-earmark-plus"></i></button>
                    <ul class="list-group" style="max-height: 400px; overflow-y: auto;">
                        <li v-for="project in projects" class="list-group-item" :class="selectedProject.oid == project.oid ? 'active' : ''" @click="setProject(project)" >{{project.name}}</li>
                    </ul>
                </div>
                <div class="col-8">
                    <template v-if="isEmptyObject(selectedProject)" >
                        <div class="shadow-sm border rounded mt-5 p-3">
                            <h5>Add new project</h5>
                            <div class="my-3">
                                <label for="inputName" class="form-label">Project name:</label>
                                <input  v-model="newName" type="text" class="form-control" id="inputName" placeholder="Project OSINT">
                            </div>
                            <div class="mb-3">
                                <label for="descriptionArea" class="form-label">Description:</label>
                                <textarea v-model="newDescription" class="form-control" id="descriptionArea" rows="3"></textarea>
                            </div>
                            
                            <button @click="saveProject" type="button" class="btn btn-primary">Save <i class="bi bi-save"></i></button>
                            <div v-if="showSpinAddProject">
                                <span  class="badge bg-info text-dark mx-2">Please wait...</span>
                            </div>
                            <p class="text-danger p-1" v-if="showErrorSave" >All fields are required</p>
                        </div>
                    </template>
                    <template v-else >
                
                        <h5>Project details</h5>
                        <div class="my-3">
                            <label for="inputName" class="form-label">Project name:</label>
                            <input v-model="selectedProject.name" type="text" class="form-control" id="inputName" placeholder="Project OSINT">
                        </div>
                        <div class="mb-3">
                            <label for="descriptionArea" class="form-label">Description:</label>
                            <textarea v-model="selectedProject.description" class="form-control" id="descriptionArea" rows="3"></textarea>
                        </div>
                        <button type="button" @click="delProject(selectedProject.oid)" class="btn btn-danger me-2">Delete <i class="bi bi-trash"></i></button>
                        <button type="button" @click="openIcp(selectedProject.oid)" class="btn btn-success">Go to ICP <i class="bi bi-arrow-right-square-fill"></i></button>
                        <div v-if="showSpinDelProject" class="m-2">
                            <span  class="badge bg-info text-dark">Please wait...</span>
                        </div>

                        <div class="border rounded shadow-sm mt-4 p-2">
                            <strong class="">Suggested search links</strong>
                            <p v-for="slink in selectedProject.suggestedSearchLinks" class="mb-0 ms-2"><a :href="slink" target="_blank" class="link-dark link-offset-2 link-underline-opacity-25 link-underline-opacity-100-hover">{{slink}}</a></p>
                            
                        </div>
                        <div class="border rounded shadow-sm mt-4 p-2">
                            <strong class="mt-4">Associated reports</strong>
                            <p v-for="report in filteredReportsByProjectId" class="mb-0 ms-2"><a :href="'/a/report/' + report.oid" target="_blank" class="link-dark link-offset-2 link-underline-opacity-25 link-underline-opacity-100-hover">{{report.name}}</a></p>
                        </div>

                    </template>
                    
                </div>
            </div>

        </div>
    `
}
    