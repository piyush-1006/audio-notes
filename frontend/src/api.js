import axios from 'axios'

// Vite only exposes variables prefixed with VITE_.
const baseURL = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')

export const api = axios.create({ baseURL, timeout: 30000 })
