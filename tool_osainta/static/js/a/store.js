import { getMe } from './backend.js';



function newVueStore() {
    return {
        testStoreText: "From store",
        me: {}
    }
}

const store = {
    
    state: Vue.reactive(newVueStore()), 

    gettestStoreText() {
        return this.state.testStoreText
    },
    setMe(me){
        this.state.me = me
    },
    getMe(m){
        return this.state.me
    },
    refreshMe(){
        getMe().then(function(response) {
            this.state.me = response.data.data
        }.bind(this))
    }
}
export default store