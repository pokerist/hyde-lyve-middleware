// Global variables
let currentSection = 'health';
const API_BASE_URL = window.location.origin;

// Utility functions
function showLoading() {
    const modal = new bootstrap.Modal(document.getElementById('loadingModal'));
    modal.show();
}

function hideLoading() {
    const modal = bootstrap.Modal.getInstance(document.getElementById('loadingModal'));
    if (modal) {
        modal.hide();
    }
}

function getApiKey() {
    return document.getElementById('api-key').value || 'demo-key';
}

function getHeaders() {
    const requireAuth = document.getElementById('require-auth').checked;
    const headers = {
        'Content-Type': 'application/json'
    };
    
    if (requireAuth) {
        headers['X-API-Key'] = getApiKey();
    }
    
    return headers;
}

function displayResponse(elementId, data, isError = false) {
    const element = document.getElementById(elementId);
    if (isError) {
        element.innerHTML = `<div class="text-danger"><strong>Error:</strong> ${data}</div>`;
    } else {
        element.innerHTML = `<pre class="mb-0">${JSON.stringify(data, null, 2)}</pre>`;
    }
}

function showSection(sectionName) {
    // Hide all sections
    const sections = document.querySelectorAll('.api-section');
    sections.forEach(section => {
        section.style.display = 'none';
    });
    
    // Show selected section
    const selectedSection = document.getElementById(sectionName + '-section');
    if (selectedSection) {
        selectedSection.style.display = 'block';
        currentSection = sectionName;
    }
}

// API Test Functions
async function testHealth() {
    showLoading();
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        displayResponse('health-response', data);
        
        // Update connection status
        const statusElement = document.getElementById('connection-status');
        if (response.ok && data.status === 'healthy') {
            statusElement.className = 'badge bg-success';
            statusElement.textContent = 'Connected';
        } else {
            statusElement.className = 'badge bg-danger';
            statusElement.textContent = 'Error';
        }
    } catch (error) {
        displayResponse('health-response', error.message, true);
        document.getElementById('connection-status').className = 'badge bg-danger';
        document.getElementById('connection-status').textContent = 'Disconnected';
    } finally {
        hideLoading();
    }
}

async function testConfig() {
    showLoading();
    try {
        const response = await fetch(`${API_BASE_URL}/api/config`, {
            headers: getHeaders()
        });
        const data = await response.json();
        displayResponse('config-response', data);
    } catch (error) {
        displayResponse('config-response', error.message, true);
    } finally {
        hideLoading();
    }
}

async function testFaceValidation() {
    showLoading();
    try {
        const faceImage = document.getElementById('face-image').value;
        if (!faceImage) {
            displayResponse('face-validation-response', 'Please enter a face image', true);
            hideLoading();
            return;
        }
        
        const response = await fetch(`${API_BASE_URL}/api/face/validate`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify({ faceImage })
        });
        const data = await response.json();
        displayResponse('face-validation-response', data);
    } catch (error) {
        displayResponse('face-validation-response', error.message, true);
    } finally {
        hideLoading();
    }
}

async function testPersonCheck() {
    showLoading();
    try {
        const personId = document.getElementById('check-person-id').value;
        if (!personId) {
            displayResponse('person-check-response', 'Please enter a person ID', true);
            hideLoading();
            return;
        }
        
        const response = await fetch(`${API_BASE_URL}/api/person/check`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify({ personId })
        });
        const data = await response.json();
        displayResponse('person-check-response', data);
    } catch (error) {
        displayResponse('person-check-response', error.message, true);
    } finally {
        hideLoading();
    }
}

async function testPersonCreate() {
    showLoading();
    try {
        const personData = {
            personId: document.getElementById('create-person-id').value,
            name: document.getElementById('create-person-name').value,
            givenName: document.getElementById('create-person-given-name').value,
            phone: document.getElementById('create-person-phone').value,
            email: document.getElementById('create-person-email').value,
            gender: parseInt(document.getElementById('create-person-gender').value),
            certificateType: parseInt(document.getElementById('create-person-certificate-type').value),
            certificateNum: document.getElementById('create-person-certificate-num').value,
            faceImages: document.getElementById('create-person-faces').value ? [document.getElementById('create-person-faces').value] : [],
            beginTime: "2024-01-01T00:00:00",
            endTime: "2030-01-01T00:00:00"
        };
        
        if (!personData.personId || !personData.name) {
            displayResponse('person-create-response', 'Person ID and Name are required', true);
            hideLoading();
            return;
        }
        
        const response = await fetch(`${API_BASE_URL}/api/person/create`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify(personData)
        });
        const data = await response.json();
        displayResponse('person-create-response', data);
    } catch (error) {
        displayResponse('person-create-response', error.message, true);
    } finally {
        hideLoading();
    }
}

async function testPersonUpdate() {
    showLoading();
    try {
        const personData = {
            personId: document.getElementById('update-person-id').value,
            name: document.getElementById('update-person-name').value,
            phone: document.getElementById('update-person-phone').value,
            email: document.getElementById('update-person-email').value,
            faceImages: document.getElementById('update-person-faces').value ? [document.getElementById('update-person-faces').value] : []
        };
        
        if (!personData.personId) {
            displayResponse('person-update-response', 'Person ID is required', true);
            hideLoading();
            return;
        }
        
        // Remove empty fields
        Object.keys(personData).forEach(key => {
            if (personData[key] === '' || personData[key] === []) {
                delete personData[key];
            }
        });
        
        const response = await fetch(`${API_BASE_URL}/api/person/update`, {
            method: 'PUT',
            headers: getHeaders(),
            body: JSON.stringify(personData)
        });
        const data = await response.json();
        displayResponse('person-update-response', data);
    } catch (error) {
        displayResponse('person-update-response', error.message, true);
    } finally {
        hideLoading();
    }
}

async function testPersonDelete() {
    showLoading();
    try {
        const personId = document.getElementById('delete-person-id').value;
        if (!personId) {
            displayResponse('person-delete-response', 'Person ID is required', true);
            hideLoading();
            return;
        }
        
        if (!confirm(`Are you sure you want to delete person ${personId}?`)) {
            hideLoading();
            return;
        }
        
        const response = await fetch(`${API_BASE_URL}/api/person/delete`, {
            method: 'DELETE',
            headers: getHeaders(),
            body: JSON.stringify({ personId })
        });
        const data = await response.json();
        displayResponse('person-delete-response', data);
    } catch (error) {
        displayResponse('person-delete-response', error.message, true);
    } finally {
        hideLoading();
    }
}

async function testPersonSearch() {
    showLoading();
    try {
        const searchData = {
            name: document.getElementById('search-person-name').value,
            phone: document.getElementById('search-person-phone').value,
            email: document.getElementById('search-person-email').value,
            gender: document.getElementById('search-person-gender').value ? parseInt(document.getElementById('search-person-gender').value) : null,
            limit: parseInt(document.getElementById('search-person-limit').value),
            offset: parseInt(document.getElementById('search-person-offset').value)
        };
        
        // Remove empty/null fields
        Object.keys(searchData).forEach(key => {
            if (searchData[key] === '' || searchData[key] === null) {
                delete searchData[key];
            }
        });
        
        const response = await fetch(`${API_BASE_URL}/api/person/search`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify(searchData)
        });
        const data = await response.json();
        displayResponse('person-search-response', data);
    } catch (error) {
        displayResponse('person-search-response', error.message, true);
    } finally {
        hideLoading();
    }
}

async function testBatchCreate() {
    showLoading();
    try {
        const batchDataText = document.getElementById('batch-persons-data').value;
        if (!batchDataText) {
            displayResponse('batch-create-response', 'Please enter persons data', true);
            hideLoading();
            return;
        }
        
        let batchData;
        try {
            batchData = JSON.parse(batchDataText);
        } catch (e) {
            displayResponse('batch-create-response', 'Invalid JSON format', true);
            hideLoading();
            return;
        }
        
        if (!Array.isArray(batchData)) {
            displayResponse('batch-create-response', 'Persons data must be an array', true);
            hideLoading();
            return;
        }
        
        const response = await fetch(`${API_BASE_URL}/api/person/batch/create`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify({ persons: batchData })
        });
        const data = await response.json();
        displayResponse('batch-create-response', data);
    } catch (error) {
        displayResponse('batch-create-response', error.message, true);
    } finally {
        hideLoading();
    }
}

// Connection check function
async function checkConnection() {
    await testHealth();
}

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    // Show health section by default
    showSection('health');
    
    // Check connection on load
    checkConnection();
    
    // Add event listeners for Enter key
    const inputs = document.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const section = currentSection;
                const testFunction = window[`test${section.charAt(0).toUpperCase() + section.slice(1)}`];
                if (testFunction) {
                    testFunction();
                }
            }
        });
    });
});