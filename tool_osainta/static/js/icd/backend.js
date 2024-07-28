export const askirApi = (data) => {
    return axios.post('/api/askir', data)
        .then((response) => {
            return response
        }).catch((e) => {
            return ''
    })
}