export const askirApi = (data) => {
    return axios.post('/api/askir', data, {
        headers: {
            'Content-Type': 'application/json'
            }
        })
        .then((response) => {
            return response
        }).catch((e) => {
            return ''
    })
}

export const genintsumApi = (data) => {
    return axios.post('/api/genintsum', data, {
        headers: {
            'Content-Type': 'application/json'
            }
        })
        .then((response) => {
            return response
        }).catch((e) => {
            return ''
    })
}