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

export const getReport = (reportId) => {
    return apiClient.get('/api/report', {
        params: {
            id: reportId
        }
    })
    .then((response) => {
        return response
    }).catch((e) => {
        return ''
    })
}

export const deleteReport = (reportId) => {
    return apiClient.delete('/api/report-delete', {
        params: {
            oid: reportId
        }
    })
}

export const listReport = () => {
    return apiClient.get('/api/report-list')
        .then((response) => {
            return response
        }).catch((e) => {
            return ''
    })
}


