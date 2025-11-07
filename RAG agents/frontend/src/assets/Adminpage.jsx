import React, { useState, useRef } from 'react';
import './Adminpage.css';

const AdminPanel = () => {
  const [files, setFiles] = useState([
    {
      id: 1,
      name: 'company_docs.pdf',
      size: 2.3,
      uploadTime: '2 hours ago'
    }
  ]);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileSelect = (e) => {
    const selectedFiles = Array.from(e.target.files);
    addFiles(selectedFiles);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const droppedFiles = Array.from(e.dataTransfer.files);
    addFiles(droppedFiles);
  };

  const addFiles = async (newFiles) => {
  for (const file of newFiles) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('collection_name', 'IT_datas');  // or 'Finance_datas'
    
    try {
      const response = await fetch('http://localhost:8000/api/upload', {
        method: 'POST',
        body: formData  // Don't set Content-Type header - browser sets it automatically
      });
      
      if (!response.ok) {
        throw new Error(`Upload failed: ${response.status}`);
      }
      
      const data = await response.json();
      
      const fileObject = {
        id: Date.now(),
        name: data.filename,
        size: (data.size / (1024 * 1024)).toFixed(2) + ' MB',
        uploadTime: new Date().toLocaleTimeString(),
        collection: data.collection_name
      };
      
      setFiles(prev => [...prev, fileObject]);
      
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Failed to upload: ' + error.message);
    }
  }
};


  return (
    <div className="admin-container">
      <div className="admin-header">
        <h1>Knowledge Base Management</h1>
        <p>Upload and manage documents for your RAG agent</p>
      </div>

      <div className="admin-body">
        <div className="upload-section">
          <div className="upload-card">
            <div
              className={`upload-zone ${dragOver ? 'drag-over' : ''}`}
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <svg className="upload-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
              </svg>
              <h3>Drop files here or click to browse</h3>
              <p>Supports PDF, TXT, DOCX, CSV, and more</p>
              <input
                type="file"
                ref={fileInputRef}
                className="file-input"
                multiple
                accept=".pdf,.txt,.doc,.docx,.csv"
                onChange={handleFileSelect}
              />
              <button className="upload-btn" onClick={(e) => { e.stopPropagation(); fileInputRef.current?.click(); }}>
                <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4"></path>
                </svg>
                Select Files
              </button>
            </div>

            <div className="file-list">
              <h3>Uploaded Files ({files.length})</h3>
              <div className="file-items">
                {files.map((file) => (
                  <div key={file.id} className="file-item">
                    <div className="file-info">
                      <div className="file-icon">
                        <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z"></path>
                          <path d="M14 2v6h6"></path>
                        </svg>
                      </div>
                      <div className="file-details">
                        <div className="file-name">{file.name}</div>
                        <div className="file-meta">{file.size} MB • Uploaded {file.uploadTime}</div>
                      </div>
                    </div>
                    <div className="file-actions">
                      <button className="btn-icon" title="View">
                        <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                        </svg>
                      </button>
                      <button className="btn-icon delete" title="Delete" onClick={() => deleteFile(file.id)}>
                        <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                        </svg>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminPanel;