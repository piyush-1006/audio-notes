import { useEffect, useRef, useState } from 'react'
import axios from 'axios'
import './App.css'

const Icon = ({ name, size = 20 }) => {
  const paths = {
    sparkles: <><path d="m12 3-1.4 4.6L6 9l4.6 1.4L12 15l1.4-4.6L18 9l-4.6-1.4L12 3Z" /><path d="m19 14-.7 2.3L16 17l2.3.7L19 20l.7-2.3L22 17l-2.3-.7L19 14Z" /><path d="m5 15-.7 2.3L2 18l2.3.7L5 21l.7-2.3L8 18l-2.3-.7L5 15Z" /></>,
    upload: <><path d="M12 16V3" /><path d="m7 8 5-5 5 5" /><path d="M20 15v4a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-4" /></>,
    audio: <><path d="M9 18V5l10-2v13" /><circle cx="6" cy="18" r="3" /><circle cx="16" cy="16" r="3" /></>,
    file: <><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z" /><path d="M14 2v6h6" /><path d="M8 13h8M8 17h5" /></>,
    check: <path d="m20 6-11 11-5-5" />,
    copy: <><rect x="9" y="9" width="13" height="13" rx="2" /><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" /></>,
    arrow: <><path d="M5 12h14" /><path d="m13 6 6 6-6 6" /></>,
  }
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]}</svg>
}

const formatFileSize = (bytes) => { if (!bytes) return ''; const u = ['B', 'KB', 'MB', 'GB']; const i = Math.floor(Math.log(bytes) / Math.log(1024)); return `${(bytes / 1024 ** i).toFixed(i ? 1 : 0)} ${u[i]}` }

function App() {
  const [file, setFile] = useState(null), [status, setStatus] = useState('idle'), [jobId, setJobId] = useState(null), [data, setData] = useState(null), [uploadError, setUploadError] = useState(null), [dragging, setDragging] = useState(false), [copied, setCopied] = useState(null)
  const inputRef = useRef(null)
  const selectFile = (next) => { if (!next) return; setFile(next); setData(null); setUploadError(null); setStatus('ready') }
  const handleDrop = (event) => { event.preventDefault(); setDragging(false); selectFile(event.dataTransfer.files?.[0]) }
  const handleUpload = async () => { if (!file) return; setStatus('uploading'); setData(null); setUploadError(null); const formData = new FormData(); formData.append('file', file); try { const res = await axios.post('http://127.0.0.1:8000/api/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } }); setJobId(res.data.job_id); setStatus('processing') } catch (error) { setStatus('failed'); setUploadError(error.response?.data?.detail || 'Unable to connect to the server. Please try again.') } }
  useEffect(() => { if (status !== 'processing' || !jobId) return undefined; const interval = setInterval(async () => { try { const res = await axios.get(`http://127.0.0.1:8000/api/jobs/${jobId}`); if (['completed', 'failed'].includes(res.data.status)) { setStatus(res.data.status); setData(res.data); clearInterval(interval) } } catch (error) { console.error('Polling Error:', error) } }, 3000); return () => clearInterval(interval) }, [status, jobId])
  const copyText = async (text, section) => { await navigator.clipboard.writeText(text); setCopied(section); setTimeout(() => setCopied(null), 1800) }
  const isBusy = status === 'uploading' || status === 'processing'
  const buttonText = status === 'uploading' ? 'Uploading audio…' : status === 'processing' ? 'Creating your notes…' : status === 'completed' ? 'Notes generated' : 'Generate notes'
  return <main className="page-wrapper">
    <div className="ambient ambient-one" /><div className="ambient ambient-two" />
    <nav className="topbar"><a className="brand" href="#top"><span className="brand-mark"><Icon name="sparkles" size={18} /></span>notely</a><span className="topbar-label">Audio intelligence</span></nav>
    <section className="hero" id="top"><div className="eyebrow"><span /> AI-powered transcription</div><h1>Turn every conversation<br /><em>into clarity.</em></h1><p className="hero-copy">Upload a recording and let Notely turn it into a polished summary and searchable transcript in moments.</p>
      <div className="workspace"><div className="workspace-head"><div><p className="section-kicker">New recording</p><h2>Make notes from audio</h2></div><div className={`status-pill ${status}`}><i />{status === 'completed' ? 'Complete' : isBusy ? 'In progress' : 'Ready when you are'}</div></div>
        <div className={`file-drop-area ${file ? 'has-file' : ''} ${dragging ? 'is-dragging' : ''} ${isBusy ? 'is-disabled' : ''}`} onDragEnter={e => { e.preventDefault(); if (!isBusy) setDragging(true) }} onDragOver={e => e.preventDefault()} onDragLeave={() => setDragging(false)} onDrop={isBusy ? undefined : handleDrop}>
          <input ref={inputRef} type="file" id="file-upload" accept="audio/*" onChange={e => selectFile(e.target.files?.[0])} disabled={isBusy} />
          <label htmlFor="file-upload" className="file-label"><span className="upload-orb">{file ? <Icon name="audio" size={26} /> : <Icon name="upload" size={26} />}</span>{file ? <span className="file-details"><strong>{file.name}</strong><small>{formatFileSize(file.size)} · Ready to analyze</small></span> : <span className="file-details"><strong>Drop your audio here</strong><small>or <b>browse files</b> from your computer</small></span>}{file && !isBusy && <button className="replace-file" type="button" onClick={e => { e.preventDefault(); inputRef.current?.click() }}>Replace</button>}</label>
        </div><div className="upload-footer"><span><Icon name="check" size={15} /> MP3, WAV, M4A and more</span><span><Icon name="check" size={15} /> Your audio stays private</span></div>
        <button className="process-btn" onClick={handleUpload} disabled={!file || isBusy || status === 'completed'}>{isBusy ? <span className="button-spinner" /> : <Icon name="sparkles" size={18} />}{buttonText}<Icon name="arrow" size={18} /></button>
        {uploadError && <div className="alert"><strong>Something went wrong.</strong> {uploadError}</div>}{data?.status === 'failed' && <div className="alert"><strong>AI processing failed.</strong> {data.error_message}</div>}
        {isBusy && <div className="processing-indicator"><div className="sound-bars"><i /><i /><i /><i /><i /></div><div><strong>{status === 'uploading' ? 'Sending your recording' : 'Listening for the important moments'}</strong><p>This usually takes just a minute.</p></div></div>}
      </div>
      {data?.status === 'completed' && <section className="results-container"><div className="results-heading"><div><p className="section-kicker">Your notes are ready</p><h2>Here’s what matters.</h2></div><span className="complete-badge"><Icon name="check" size={14} /> Complete</span></div><article className="result-card highlight"><div className="card-heading"><span className="card-icon lavender"><Icon name="sparkles" size={18} /></span><h3>Smart summary</h3><button onClick={() => copyText(data.summary, 'summary')} aria-label="Copy summary">{copied === 'summary' ? <Icon name="check" size={17} /> : <Icon name="copy" size={17} />}</button></div><p>{data.summary}</p></article><article className="result-card"><div className="card-heading"><span className="card-icon blue"><Icon name="file" size={18} /></span><h3>Full transcript</h3><button onClick={() => copyText(data.transcript, 'transcript')} aria-label="Copy transcript">{copied === 'transcript' ? <Icon name="check" size={17} /> : <Icon name="copy" size={17} />}</button></div><p>{data.transcript}</p></article></section>}
    </section><footer>Built for the conversations worth remembering <span>✦</span></footer>
  </main>
}
export default App
