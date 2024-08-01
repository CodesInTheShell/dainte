import knowledges from './pages/knowledge.js'
import pageNotFound from './pages/pageNotFound.js'
import dashboard from './pages/dashboard.js'

export const router = VueRouter.createRouter({
    history: VueRouter.createWebHistory(),
    routes: [
        { path: '/a/:pathMatch(.*)*', name: 'pageNotFound', component: pageNotFound},
        { path: '/a', name: 'a', component: dashboard},
        { path: '/a/knowledges', name: 'knowledges', component: knowledges},
    ]
})