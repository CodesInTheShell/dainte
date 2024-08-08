function newVueStore() {
    return {
        testStoreText: "From store",
    }
}

const store = {
    
    state: Vue.reactive(newVueStore()), 

    gettestStoreText() {
        return this.state.testStoreText
    },
}
export default store