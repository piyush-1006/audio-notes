import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

function App() {
  const [file, setFile] = useState(null)
  const [status, setStatus] = useState('idle') 
  const [jobId, setJobId] = useState(null)
  const [data, setData] = useState(null)
  const [uploadError, setUploadError] = useState(null)

  const handleFileChange = (e) => {
    if (e.target.files[0]) {
      setFile(e.target.files[0])
      setUploadError(null)
      setStatus('ready')
    }
  }

  const handleUpload = async () => {
    if (!file) return;
    setStatus('uploading')
    setData(null)
    setUploadError(null)
    
    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await axios.post('http://127.0.0.1:8000/api/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setJobId(res.data.job_id)
      setStatus('processing')
    } catch (error) {
      console.error("Upload Error:", error)
      setStatus('failed')
      setUploadError(error.response?.data?.detail || "Failed to connect to the server.")
    }
  }

  useEffect(() => {
    let interval;
    if (status === 'processing' && jobId) {
      interval = setInterval(async () => {
        try {
          const res = await axios.get(`http://127.0.0.1:8000/api/jobs/${jobId}`)
          if (res.data.status === 'completed' || res.data.status === 'failed') {
            setStatus(res.data.status)
            setData(res.data)
            clearInterval(interval)
          }
        } catch (error) {
          console.error("Polling Error:", error)
        }
      }, 3000)
    }
    return () => clearInterval(interval)
  }, [status, jobId])

  return (
    <div className="page-wrapper">
      <div className="app-container">
        <header className="app-header">
          <div className="logo-icon">🎙️</div>
          <h1>Audio Notes AI</h1>
          <p>Upload your audio to instantly generate a smart transcript and summary.</p>
        </header>
        
        <div className="upload-section">
          {/* Custom File Upload Area */}
          <div className={`file-drop-area ${file ? 'has-file' : ''}`}>
            <input 
              type="file" 
              id="file-upload" 
              accept="audio/*" 
              onChange={handleFileChange} 
              disabled={status === 'uploading' || status === 'processing'}
            />
            <label htmlFor="file-upload" className="file-label">
              <span className="upload-icon">{file ? '🎵' : '📁'}</span>
              <span className="file-text">
                {file ? file.name : 'Click to choose an audio file'}
              </span>
            </label>
          </div>

          <button 
            className={`process-btn ${status}`}
            onClick={handleUpload} 
            disabled={!file || status === 'uploading' || status === 'processing' || status === 'completed'}
          >
            {status === 'uploading' ? 'Uploading...' : 
             status === 'processing' ? 'AI is Processing...' : 
             status === 'completed' ? 'Process Complete' : 
             'Generate Notes'}
          </button>
        </div>

        {uploadError && (
          <div className="alert error-alert">
            <strong>❌ Error:</strong> {uploadError}
          </div>
        )}
        
        {(status === 'uploading' || status === 'processing') && (
          <div className="processing-indicator">
            <div className="pulse-ring"></div>
            <p>Analyzing audio with Gemini...</p>
          </div>
        )}

        {data && data.status === 'completed' && (
          <div className="results-container animate-fade-in">
            <div className="result-card highlight">
              <h2>✨ Smart Summary</h2>
              <p>{data.summary}</p>
            </div>
            <div className="result-card">
              <h2>📝 Full Transcript</h2>
              <p>{data.transcript}</p>
            </div>
          </div>
        )}

        {data && data.status === 'failed' && (
          <div className="alert error-alert">
            <strong>❌ AI Failed:</strong> {data.error_message}
          </div>
        )}
      </div>
    </div>
  )
}

export default App