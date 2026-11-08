import axios from 'axios'

// Todas as chamadas ao backend ficam neste ficheiro.
const api = axios.create({ baseURL: 'http://localhost:5000/api' })
export const airService = {
  async getSensores() { return (await api.get('/sensores')).data },
  async getLeituras(sensor = 'todos') { return (await api.get('/leituras', { params: { sensor } })).data },
  async uploadCSV(files) {
    const form = new FormData()
    for (const file of files) form.append('ficheiros', file)
    return (await api.post('/upload', form)).data // Axios define o boundary automaticamente.
  },
  async limparDados() { return (await api.delete('/dados')).data }
}
