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

export const askirApi = (data) => {
    return apiClient.post('/api/askir', data, {
        })
        .then((response) => {
            return response
        }).catch((e) => {
            return ''
    })
}

export const genintsumApi = (data) => {
    return apiClient.post('/api/genintsum', data, {
        })
        .then((response) => {
            return response
        }).catch((e) => {
            return ''
    })
}

export const listProjects = () => {
    return apiClient.get('/api/project-list')
        .then((response) => {
            return response
        }).catch((e) => {
            return ''
    })
}

export const listInReqs = (projectId) => {
    return apiClient.get('/api/inreq-list?projectId='+projectId)
        .then((response) => {
            return response
        }).catch((e) => {
            return ''
    })
}

export const saveReport = (data) => {
    return apiClient.post('/api/report', data, {
        })
        .then((response) => {
            return response
        }).catch((e) => {
            return ''
    })
}


