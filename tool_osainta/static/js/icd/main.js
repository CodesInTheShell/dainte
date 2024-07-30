import store from './store.js';
import { askirApi, genintsumApi } from './backend.js';


const app = Vue.createApp({
    data(){
        return {
            geminiApiKey: '',
            irs: [
            ],
            queryInput: '',
            embeddingRag: [],
            // [{
            //     text: '',
            //     embedding: [],
            // }]
            contextText: '',
            intsum:'',
            showSpinAskOsainta: false,
            showIntSumSpinner: false,
        }
    },
    created () {
    },
    components: {
    },
    methods: {
        queryOsainta(){
            this.showSpinAskOsainta = true
            if (this.queryInput === '') {
                console.error('queryInput is empty.')
                this.showSpinAskOsainta = false
                return
            }
            askirApi(JSON.stringify({context: this.contextText, user_query: this.queryInput})).then(function(response) {
                this.irs.push(response.data)
                this.queryInput = ''
                this.showSpinAskOsainta = false
            }.bind(this))
        },
        generateEmmbeddingRag() {
            console.log('contextText:', this.contextText) 
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
        }
    },
    template: /*html*/`
    <div class="mb-5">
        <hr class="my-5 py-1">
        <h4 class="bg-warning p-2 rounded" >Start asking Osainta. Add context (optional) </h4>

        <div class="mb-3">
            <label for="contextText" class="form-label">Add context to help Osainta answer your questions then click Ask Osainta button with your query.</label>
            <textarea v-model="contextText" class="form-control" id="contextText" name="contextText" rows="10" required placeholder="Paste an article here."></textarea>
        </div>
        
        <div class="border bg-light p-2 rounded mb-3">
            <div class="mb-3">
                <label for="query_input" class="form-label">Ask for your intelligence requirements:</label>
                <textarea v-model="queryInput" class="form-control" id="query_input" rows="3" name="query_input" placeholder="What is OSINT? Give me a SWOT analysis of OSINT." required></textarea>
            </div>
            <div v-if="showSpinAskOsainta" class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <div>
                <button @click="queryOsainta" type="button" class="btn btn-dark">Ask Osainta</button>
                <p class="text-muted">Please check below responded IRs and you ask.</p>
            </div>
        </div>

        <hr class="my-5">

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
                        <p class="text-muted text-small p-3">Reference: {{ ir.irReference }}</p>
                    </div>
                </div>
            </div>
        </div>

        <hr class="my-5">

        <h4 class="bg-warning p-2 rounded" >Intelligence summary</h4>
        <div v-if="showIntSumSpinner" class="spinner-border text-success" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
        <div>
            <p class="text-muted">Generate an intelligence summary. This will consider all of your IRs above. The greater the IRs and its reponse is the greater the intsum result.</p>
            <button @click="generateIntSum" type="button" class="btn btn-success">Generate INTSUM</button>
        </div>
        
        <div class="p-4 m-4 border rounded">
            <div  v-html="toMarkDown(intsum)"></div>
        </div>

        <hr class="my-5">



    </div>
    `
})
app.use().mount('#icd_app')