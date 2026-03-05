import axios from 'axios';

const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

API.interceptors.request.use(
  (config) => config,
  (error) => Promise.reject(error)
);

API.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      console.error('API Error:', error.response.data);
      switch (error.response.status) {
        case 400:
          error.message =
            error.response.data?.token?.[0] ||
            error.response.data?.error ||
            'Bad request';
          break;
        case 401:
          error.message = 'Unauthorized. Please check your token.';
          break;
        case 404:
          error.message = 'Resource not found.';
          break;
        case 500:
          error.message = 'Server error. Please try again later.';
          break;
        default:
          error.message = error.response.data?.error || 'An error occurred';
      }
    } else if (error.request) {
      error.message = 'Cannot connect to server. Please check your connection.';
    }
    return Promise.reject(error);
  }
);

export const tokenAPI = {
  generateToken: async () => {
    const response = await API.post('/tokens/');
    return response.data;
  },
};

export const assignmentAPI = {
  generateAssignment: async (data) => {
    const response = await API.post('/generate/', {
      token: data.token,
      name: data.name,
      matric_number: data.matric,
      email: data.email,
    });
    return response.data; // { message, task_id }
  },

  // Matches backend: GET /status/<task_id>/
  checkStatus: async (taskId) => {
    const response = await API.get(`/status/${taskId}/`);
    return response.data; // { status: "pending"|"done"|"failed", file_links? }
  },
};

export default API;