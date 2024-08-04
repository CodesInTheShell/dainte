import store from '../store.js';
import { addKnowledge, listKnowledges, deleteKnowledge} from '../backend.js';


export default {
    data(){
        return {
            knowledges: [
            ],
            selectedKnowledge: {},
            newName: '',
            newDescription: '',
            newData: '',
            showErrorSave: false,
            showSpinAddknowledge: false,
            showSpinDelknowledge: false,
        }
    },
    created () {
        this.initKnowledges()

    },
    components: {
    },
    methods: {
        initKnowledges(){
            listKnowledges().then(function(response) {
                this.knowledges = response.data.data
            }.bind(this))
        },
        setKnowledge(knowledge){
            this.selectedKnowledge = knowledge
        },
        countWords(str) {
            const words = str.match(/\b\w+\b/g);
            return words ? words.length : 0;
        },
        isEmptyObject(obj) {
            return Object.keys(obj).length === 0 && obj.constructor === Object;
        },
        saveKnowledge() {
            if (this.newName === '' || this.newDescription === '' || this.newData === '') {
                this.showErrorSave = true
                setTimeout(() => {
                    this.showErrorSave = false;
                }, 3000);
                return
            }
            this.showSpinAddknowledge = true

            addKnowledge(JSON.stringify({
                knowledgeName: this.newName, 
                knowledgeDescription: this.newDescription, 
                knowledgeData: this.newData})).then(function(response) {

                this.newName = ''
                this.newDescription = ''
                this.newData = ''
                this.showSpinAddknowledge = false
                this.initKnowledges()
            }.bind(this))
        },
        delKnowledge(oid){
            this.showSpinDelknowledge = true
            deleteKnowledge(oid).then(function(response){
                this.showSpinDelknowledge = false
                this.initKnowledges()
                this.setKnowledge({})
            }.bind(this))
        }
    },
    template: /*html*/`
        <div class="container m-2 pt-4">
            <h1 class="pb-4"><span><i class="bi bi-book pe-2" style="font-size: 3rem; color: cornflowerblue;"></i></span>Your knowledge base</h1>
            
            <p>Here is where you can add stock knowledges that can help Osainta to search for references to significantly improve response. The more information stocked, the better.</p>

            <div class="row mt-4">
                <div class="col-4">
                    <p><strong>Knowledges</strong></p>
                    <button @click="setKnowledge({})" type="button" class="btn btn-primary mb-4">Add new <i class="bi bi-file-earmark-plus"></i></button>
                    <ul class="list-group" style="max-height: 300px; overflow-y: auto;">
                        <li v-for="knowledge in knowledges" class="list-group-item" :class="selectedKnowledge.oid == knowledge.oid ? 'active' : ''" @click="setKnowledge(knowledge)" >{{knowledge.name}}</li>
                    </ul>
                </div>
                <template v-if="isEmptyObject(selectedKnowledge)" >
                    <div class="col-8">
                        <h5>Add new knowledge</h5>
                        <div class="my-3">
                            <label for="inputName" class="form-label">Knowledge name:</label>
                            <input  v-model="newName" type="text" class="form-control" id="inputName" placeholder="OSINT wiki">
                        </div>
                        <div class="mb-3">
                            <label for="descriptionArea" class="form-label">Description:</label>
                            <textarea v-model="newDescription" class="form-control" id="descriptionArea" rows="3"></textarea>
                        </div>
                        <div class="mb-3">
                            <label for="dataArea" class="form-label">Data:</label>
                            <textarea v-model="newData" class="form-control" id="dataArea" rows="13"></textarea>
                        </div>
                        <h6>Estimated word count <span class="badge bg-warning text-dark">{{countWords(newData)}}</span></h6>
                        <button @click="saveKnowledge" type="button" class="btn btn-primary">Save <i class="bi bi-save"></i></button>
                        <div v-if="showSpinAddknowledge">
                            <span  class="badge bg-info text-dark mx-2">Please wait...</span>
                        </div>
                        <p class="text-danger p-1" v-if="showErrorSave" >All fields are required</p>
                    </div>
                </template>
                <template v-else >
                    <div class="col-8">
                    <h5>Knowledge details</h5>
                        <div class="my-3">
                            <label for="inputName" class="form-label">Knowledge name:</label>
                            <input v-model="selectedKnowledge.name" type="text" class="form-control" id="inputName" placeholder="OSINT wiki">
                        </div>
                        <div class="mb-3">
                            <label for="descriptionArea" class="form-label">Description:</label>
                            <textarea v-model="selectedKnowledge.description" class="form-control" id="descriptionArea" rows="3"></textarea>
                        </div>
                        <button type="button" @click="delKnowledge(selectedKnowledge.oid)" class="btn btn-danger">Delete <i class="bi bi-trash"></i></button>
                        <div v-if="showSpinDelknowledge" class="m-2">
                            <span  class="badge bg-info text-dark">Please wait...</span>
                        </div>
                    </div>
                </template>
            </div>
        </div>
    `
}
    