const apiClient = axios.create({
    baseURL: '/', 
    headers: {
        'Content-Type': 'application/json'
    }
});

apiClient.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        if (error.response && error.response.status === 429) {
            alert('Rate limit reached or not enough token. Please try again next time or contact the system admnistrator.');
        } else {
            console.error('Error querying Osainta:', error);
        }
        return Promise.reject(error); 
    }
);

export const getMe = () => {
    return apiClient.get('/api/me')
        .then((response) => {
            return response
        }).catch((e) => {
            return ''
    })
}

export const addKnowledge = (data) => {
    return apiClient.post('/api/knowledge', data, {
        })
        .then((response) => {
            return response
        }).catch((e) => {
            return ''
    })
}

export const listKnowledges = () => {
    return apiClient.get('/api/knowledge-list')
        .then((response) => {
            return response
        }).catch((e) => {
            return ''
    })
}

export const deleteKnowledge = (oid) => {
    return apiClient.delete('/api/knowledge-delete', {params: {oid: oid}}   
        )
        .then((response) => {
            return response
        }).catch((e) => {
            return ''
    })
}