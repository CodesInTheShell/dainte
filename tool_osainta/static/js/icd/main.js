import store from './store.js';

const app = Vue.createApp({
    data(){
        return {
            geminiApiKey: '',
            irs: [
                {
                    'irQuery':'Sample IR query?',
                    'irAnswer':'<div><strong>Sample IR answer</strong> that was answered by <code>Osainta</code></div>',
                    'irReference': 'Some reference',
                },
                {
                    'irQuery':'What is Osainta?',
                    'irAnswer':'<div><strong>Osainta</strong> is an app for osint powered by AI</div>',
                    'irReference': 'Some Ostainta reference',
                }
            ],
            queryInput: '',
            embeddingRag: [],
            // [{
            //     text: '',
            //     embedding: [],
            // }]
            contextRag: '',
        }
    },
    created () {
    },
    components: {
    },
    methods: {
        queryOsainta(){
            console.log('queryInput:', this.queryInput)
        },
        generateEmmbeddingRag() {
            console.log('contextRag:', this.contextRag)
        }
    },
    template: /*html*/`
    <div class="mb-5">
        <hr class="my-5 py-1">

        <div class="mb-3">
            <label for="contextRag" class="form-label">Add context to help Osainta answer your questions then click Ask Osainta button with your query.</label>
            <textarea v-model="contextRag" class="form-control" id="contextRag" name="contextRag" rows="10" required placeholder="Paste an article here."></textarea>
        </div>
        

        <hr class="my-5 py-1">
        
        <div class="border bg-light p-2 rounded mb-3">
            <div class="mb-3">
                <label for="query_input" class="form-label">Ask for your intelligence requirements:</label>
                <input v-model="queryInput" type="text" class="form-control" id="query_input" name="query_input" placeholder="What is OSINT?" required>
            </div>
            <button @click="queryOsainta" type="button" class="btn btn-dark">Ask Osainta</button>
        </div>

        <hr class="my-5 py-1">

        <div class="border p-4 rounded">
            <h4>Browse below for responded IRs:</h4>
            <div class="accordion" id="accordionExample">
                <div v-for="(ir, index) in irs" :key="index" class="accordion-item">
                    <h2 class="accordion-header" :id="'heading' + index">
                        <button class="accordion-button" type="button" data-bs-toggle="collapse" :data-bs-target="'#collapse' + index" aria-expanded="true" :aria-controls="'collapse' + index">
                            {{ ir.irQuery }}
                        </button>
                    </h2>
                    <div :id="'collapse' + index" class="accordion-collapse collapse show" :aria-labelledby="'heading' + index" data-bs-parent="#accordionExample">
                        <div class="accordion-body">
                            <div v-html="ir.irAnswer"></div>
                        </div>
                        <p class="text-muted text-small p-3">Reference: {{ ir.irReference }}</p>
                    </div>
                </div>
            </div>
        </div>

        


    </div>
    `
})
app.use().mount('#icd_app')