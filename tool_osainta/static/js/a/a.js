import store from './store.js';
import { router } from './routes.js';
import { getMe } from './backend.js';


const app = Vue.createApp({
    router,
    data(){
        return {
            username: '',
        }
    },
    created () {
        getMe().then(function(response) {
            console.log('response: ', response.data)
            this.username = response.data.data.username
        }.bind(this))
        
    },
    components: {
    },
    methods: {
    },
    template: /*html*/`
        <div class="mb-5">
            <nav class="navbar navbar-expand-lg navbar-light bg-light">
                <div class="container-fluid">
                    <a class="navbar-brand" href="#">OSAINTA</a>
                    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                        <span class="navbar-toggler-icon"></span>
                    </button>
                    <div class="collapse navbar-collapse" id="navbarNav">
                        <ul class="navbar-nav me-auto">
                            <li class="nav-item">
                                <a class="nav-link" href="/">Home</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href="/icp">ICP</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href="/a/knowledges">Knowledges</a>
                            </li>
                        </ul>
                        <ul class="navbar-nav ms-auto">
                            <li class="nav-item bg-dark rounded me-2 px-2">
                                <a class="nav-link text-warning" href="#">Hello, {{username}}</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href="/logout">Logout</a>
                            </li>
                        </ul>
                    </div>
                </div>
            </nav>  



            <router-view></router-view>

            <footer class="footer mt-auto py-3 bg-light border-top">
                <div class="container">
                    <p class="mb-1">Osainta can make mistakes. Please very informations.</p>
                    <p class="mb-0">Osainta AI for OSINT is developed by <a href="https://dantebytes.com/" target="_blank">dantebytes</a></p>
                </div>
            </footer>
        </div>
    `
})
app.use(router).mount('#app')