import axios from 'axios';

const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  headers: { 'Content-Type': 'application/json' },
  timeout: 360000, // 6 minutes — must be longer than the slowest task
});

API.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      let msg = error.response.data?.error || 'An error occurred';
      if (error.response.status === 400) msg = error.response.data?.token?.[0] || msg;
      else if (error.response.status === 401) msg = 'Unauthorized. Check your token.';
      else if (error.response.status === 404) msg = 'Resource not found.';
      else if (error.response.status === 500) msg = 'Server error. Try again later.';
      error.message = msg;
    } else if (error.code === 'ECONNABORTED') {
      error.message = 'Request timed out. Please try again.';
    } else if (error.request) {
      error.message = 'Cannot connect to server. Check your connection.';
    }
    return Promise.reject(error);
  }
);

export const tokenAPI = {
  generateToken201: () => API.post('/tokens/').then(r => r.data),
  getAllTokens201:   () => API.get('/tokens/').then(r => r.data),
  generateToken205: () => API.post('/205/tokens/').then(r => r.data),
  getAllTokens205:   () => API.get('/205/tokens/').then(r => r.data),
};

export const assignmentAPI = {
  // COS201 — blocks until task.get() resolves, returns { message, file_links }
  generateAssignment: (data) => API.post('/generate/', {
    token: data.token,
    name: data.name,
    matric_number: data.matric,
    email: data.email,
  }).then(r => r.data),

  // COS205 — same blocking pattern, returns { message, file_links }
  generateAssignment205: (data) => API.post('/205/generate/', {
    token: data.token,
    name: data.name,
    matric_number: data.matric,
    email: data.email,
  }).then(r => r.data),
};

export default API;