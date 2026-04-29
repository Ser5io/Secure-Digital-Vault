import { useEffect, useState } from "react";

export default function Dashboard() {
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [file, setFile] = useState(null);
  const [files, setFiles] = useState([]);
  const [password, setPassword] = useState(""); // Needed for encryption key

  const token = localStorage.getItem("token");

  useEffect(() => {
    if (!token) window.location.href = "/";
    fetchFiles();
  }, []);

  async function fetchFiles() {
    try {
      const response = await fetch("http://localhost:5000/files", {
        headers: { "Authorization": `Bearer ${token}` }
      });
      const data = await response.json();
      if (response.ok) setFiles(data);
    } catch (err) {
      setError("Failed to load files.");
    }
  }

  async function handleUpload() {
    if (!file || !password) {
      setError("❌ Select a file and enter your password for encryption!");
      return;
    }

    setLoading(true);
    setProgress(20);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("password", password);

    try {
      const response = await fetch("http://localhost:5000/upload", {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}` },
        body: formData
      });

      if (response.ok) {
        setProgress(100);
        setMessage("✅ File Encrypted & Stored!");
        setFile(null);
        fetchFiles(); // Refresh list
      } else {
        setError("Upload failed.");
      }
    } catch (err) {
      setError("Server connection lost.");
    } finally {
      setLoading(false);
    }
  }

  async function handleDownload(fileId, fileName) {
    const pass = prompt("Enter your password to decrypt this file:");
    if (!pass) return;

    try {
      const response = await fetch(`http://localhost:5000/download/${fileId}`, {
        method: "POST",
        headers: { 
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ password: pass })
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = fileName;
        a.click();
      } else {
        alert("Incorrect password or download error.");
      }
    } catch (err) {
      alert("Download failed.");
    }
  }

  return (
    <div className="min-h-screen bg-black text-white p-6">
      {/* Header */}
      <div className="flex justify-between mb-8">
        <h1 className="text-3xl text-blue-400 font-bold">🔐 Secure Vault</h1>
        <button onClick={() => { localStorage.clear(); window.location.href = "/"; }} className="bg-red-500 px-4 py-2 rounded">Logout</button>
      </div>

      {/* Upload */}
      <div className="bg-gray-900 p-6 rounded-xl mb-6 border border-blue-500 shadow-lg">
        <h2 className="text-xl mb-4">Upload New File</h2>
        
        <input type="password" placeholder="Vault Password" value={password} onChange={(e) => setPassword(e.target.value)}
          className="w-full p-2 mb-4 rounded bg-gray-700 text-white border border-gray-600" />
        
        <div className="mt-4 flex gap-3">
          <input type="file" onChange={(e) => setFile(e.target.files[0])} />
          <button onClick={handleUpload} className="bg-blue-600 px-4 py-2 rounded">Upload & Encrypt</button>
        </div>

        {message && <p className="text-green-400 mt-2">{message}</p>}
        {error && <p className="text-red-400 mt-2">{error}</p>}
        {loading && <div className="mt-2 text-blue-400 animate-pulse">Encrypting... {progress}%</div>}
      </div>

      {/* Files List */}
      <div className="bg-gray-900 p-6 rounded-xl border border-gray-700">
        <h2 className="text-xl mb-4">Your Encrypted Vault</h2>
        <ul className="space-y-3">
          {files.map((f) => (
            <li key={f.id} className="flex justify-between items-center bg-gray-800 p-4 rounded border border-gray-700">
              <div>
                <span className="text-lg">📄 {f.name}</span>
                <span className="ml-3 text-gray-400 text-sm">({f.size})</span>
              </div>
              <button onClick={() => handleDownload(f.id, f.name)} className="bg-green-600 px-3 py-1 rounded">Download</button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
