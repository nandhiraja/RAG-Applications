import React, { useState, useRef, useEffect } from 'react';
import './Styles/Adminpage.css';
import './Styles/Login.css';
import { AiFillDelete } from "react-icons/ai";
import { MdPreview } from "react-icons/md";
import { FaFileAlt } from "react-icons/fa";
import { IoMdRefresh } from "react-icons/io";

// Login Component (unchanged)
const Login = ({ onLogin }) => {
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials)
      });
      
      const data = await response.json();
      
      if (response.ok) {
        localStorage.setItem('adminToken', data.token);
        onLogin(true);
      } else {
        setError(data.detail || 'Invalid credentials');
      }
    } catch (error) {
      setError('Login failed. Please check your connection.');
    } finally {
      setLoading(false);
      console.log("finallyy donee..")
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h2>Admin Login</h2>
        <p className="login-subtitle">RAG Agent Management</p>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Username"
            value={credentials.username}
            onChange={(e) => setCredentials({...credentials, username: e.target.value})}
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={credentials.password}
            onChange={(e) => setCredentials({...credentials, password: e.target.value})}
            required
          />
          {error && <p className="error">{error}</p>}
          <button type="submit" disabled={loading}>
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
      </div>
    </div>
  );
};

// Main Admin Panel Component
const AdminPanel = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [selectedDomain, setSelectedDomain] = useState('');
  const [domains, setDomains] = useState([]);
  const [files, setFiles] = useState([]);
  const [dragOver, setDragOver] = useState(false);
  const [viewModal, setViewModal] = useState({ show: false, content: '', filename: '' });
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);

  // Helper function
  const getAuthHeaders = () => ({
    'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
  });

  // Fetch domains
  const fetchDomains = async () => {
    try {
      console.log('Fetching domains...');
      const response = await fetch('http://localhost:8000/api/domains', {
        headers: getAuthHeaders()
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('Domains:', data);
        setDomains(data.domains || []);
      }
    } catch (error) {
      console.error('Failed to fetch domains:', error);
    }
  };

  // Fetch domain files
  const fetchDomainFiles = async (domain) => {
    try {
      console.log('Fetching files for:', domain);
      const response = await fetch(`http://localhost:8000/api/files/${domain}`, {
        headers: getAuthHeaders()
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('Files:', data);
        setFiles(data.files || []);
      } else if (response.status === 401) {
        handleLogout();
      }
    } catch (error) {
      console.error('Failed to fetch files:', error);
      alert('Failed to load files. Please try again.');
    }
  };

  // Handle file selection
  const handleFileSelect = (e) => {
    if (!selectedDomain) {
      alert('Please select a domain first!');
      return;
    }
    const selectedFiles = Array.from(e.target.files);
    addFiles(selectedFiles);
  };

  // Handle drag and drop - FIXED
  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    
    if (!selectedDomain) {
      alert('Please select a domain first!');
      return;
    }
    
    const droppedFiles = Array.from(e.dataTransfer.files);
    addFiles(droppedFiles);
  };

  // Add files
  const addFiles = async (newFiles) => {
    setUploading(true);
    
    for (const file of newFiles) {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('domain', selectedDomain);
      
      try {
        const response = await fetch('http://localhost:8000/api/upload', {
          method: 'POST',
          headers: getAuthHeaders(),
          body: formData
        });
        
        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.detail || 'Upload failed');
        }
        
        const data = await response.json();
        console.log('Upload successful:', data);
        
      } catch (error) {
        console.error('Upload failed:', error);
        alert(`Failed to upload ${file.name}: ${error.message}`);
      }
    }
    
    setUploading(false);
    await fetchDomainFiles(selectedDomain);
  };

  // Delete file
  const deleteFile = async (filename) => {
    if (!window.confirm(`Are you sure you want to delete "${filename}"?`)) {
      return;
    }
    
    try {
      const response = await fetch(
        `http://localhost:8000/api/files/${selectedDomain}/${filename}`,
        {
          method: 'DELETE',
          headers: getAuthHeaders()
        }
      );
      
      if (response.ok) {
        setFiles(files.filter(f => f.name !== filename));
        alert('File deleted successfully!');
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Delete failed');
      }
    } catch (error) {
      console.error('Delete failed:', error);
      alert('Failed to delete file: ' + error.message);
    }
  };

  // View file
  const viewFile = async (filename) => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/files/${selectedDomain}/${filename}/content`,
        {
          headers: getAuthHeaders()
        }
      );
      
      if (response.ok) {
        const data = await response.json();
        setViewModal({ show: true, content: data.content, filename });
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to load file');
      }
    } catch (error) {
      alert('Failed to load file: ' + error.message);
    }
  };

  // Logout
  const handleLogout = () => {
    localStorage.removeItem('adminToken');
    setIsAuthenticated(false);
    setSelectedDomain('');
    setFiles([]);
    setDomains([]);
  };

  // Check authentication on mount
  useEffect(() => {
    const token = localStorage.getItem('adminToken');
    console.log("Getting domain",token)

    if (token) {
      console.log("Getting domain",token)
      setIsAuthenticated(true);
      fetchDomains();
    }
  }, []);

  // Fetch files when domain changes
  useEffect(() => {
    if (selectedDomain && isAuthenticated) {
      fetchDomainFiles(selectedDomain);
    }
  }, [selectedDomain, isAuthenticated]);

useEffect(()=>{
    if (isAuthenticated) {
      fetchDomains();
    }
},[])
  // Show login if not authenticated
  if (!isAuthenticated) {
    return <Login onLogin={setIsAuthenticated} />;
  }

  return (
    <div className="admin-container">
      <div className="admin-header">
        <div>
          <h1>Source Management (Admin)</h1>
          <p className="admin-subtitle">Manage domain-specific knowledge bases</p>
        </div>
        <button className="logout-btn" onClick={handleLogout}>
          <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
          </svg>
          Logout
        </button>
      </div>

      <div className="domain-selector">
        <div className="domain-select-wrapper">
          <label>Select Domain:</label>
          <select 
            onClick={()=>{fetchDomains()}}
            value={selectedDomain} 
            onChange={(e) => setSelectedDomain(e.target.value)}
            className="domain-select"
          >
            <option value="">Choose</option>
            {domains.map(d => (
              <option key={d.name} value={d.name}>
                {d.name} ({d.fileCount} files)
              </option>
            ))}
          </select>
        </div>
        {!selectedDomain && (
          <p className="domain-hint"> Please select a domain to manage files</p>
        )}
      </div>

      {selectedDomain && (
        <div className="admin-body">
          <div className="upload-section">
            <div className="upload-card">
              <div
                className={`upload-zone ${dragOver ? 'drag-over' : ''} ${uploading ? 'uploading' : ''}`}
                onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                onDragLeave={() => setDragOver(false)}
                onDrop={handleDrop}
                onClick={() => !uploading && fileInputRef.current?.click()}
              >
                {uploading ? (
                  <div className="upload-progress">
                    <div className="spinner"></div>
                    <h3>Uploading & Processing...</h3>
                  </div>
                ) : (
                  <>
                    <svg className="upload-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                    </svg>
                    <h3>Upload to {selectedDomain} Domain</h3>
                    <p>Supports PDF, TXT, DOCX, CSV files</p>
                    <input
                      type="file"
                      ref={fileInputRef}
                      className="file-input"
                      multiple
                      accept=".pdf,.txt,.doc,.docx,.csv"
                      onChange={handleFileSelect}
                      disabled={uploading}
                    />
                    <button 
                      className="upload-btn" 
                      onClick={(e) => { 
                        e.stopPropagation(); 
                        fileInputRef.current?.click(); 
                      }}
                      disabled={uploading}
                    >
                      Select Files
                    </button>
                  </>
                )}
              </div>

              <div className="file-list">
                <div className="file-list-header">
                  <h3>{selectedDomain} Files ({files.length})</h3>
                  <button 
                    className="refresh-btn" 
                    onClick={() => fetchDomainFiles(selectedDomain)}
                    title="Refresh file list"
                  >
                   <IoMdRefresh  size={30}/>
                  </button>
                </div>
                
                <div className="file-items">
                  {files.length === 0 ? (
                    <div className="no-files">
                      <p>No files uploaded yet</p>
                    </div>
                  ) : (
                    files.map((file) => (
                      <div key={file.id} className="file-item">
                        <div className="file-info">
                          <div className="file-icon"><FaFileAlt/></div>
                          <div className="file-details">
                            <div className="file-name">{file.name}</div>
                            <div className="file-meta">{file.size} • {file.uploadTime}</div>
                          </div>
                        </div>
                        <div className="file-actions">
                          <button 
                            className="btn-icon view" 
                            title="View file" 
                            onClick={() => viewFile(file.name)}
                          >
                            <MdPreview/>
                          </button>
                          <button 
                            className="btn-icon delete" 
                            title="Delete file" 
                            onClick={() => deleteFile(file.name)}
                          >
                            <AiFillDelete />
                          </button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {viewModal.show && (
        <div className="modal-overlay" onClick={() => setViewModal({ show: false, content: '', filename: '' })}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>📄 {viewModal.filename}</h3>
              <button 
                className="modal-close" 
                onClick={() => setViewModal({ show: false, content: '', filename: '' })}
              >
                ✕
              </button>
            </div>
            <div className="modal-body">
              <pre>{viewModal.content}</pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminPanel;
