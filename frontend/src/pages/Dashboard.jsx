import { useEffect, useState, useRef } from "react";

export default function Dashboard() {
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState("");
  const [file, setFile] = useState(null);
  const [files, setFiles] = useState([]);
  const [password, setPassword] = useState(""); 
  
  // Create a reference to the file input to clear it manually
  const fileInputRef = useRef(null);

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
      console.error("Failed to load files:", err);
    }
  }

  async function handleUpload() {
    if (!file || !password) {
      alert("❌ Please select a file AND enter your password for encryption!");
      return;
    }

    setMessage(""); // Clear old message
    setLoading(true);
    setProgress(30);

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
        setMessage("✅ File Encrypted & Stored Successfully!");
        
        // 🏁 THE FIX: Reset everything so you can upload again
        setFile(null);
        setPassword("");
        if (fileInputRef.current) fileInputRef.current.value = ""; 
        
        fetchFiles(); // Refresh list
      } else {
        alert("❌ Upload failed!");
      }
    } catch (err) {
      alert("❌ Connection error.");
    } finally {
      setTimeout(() => {
        setLoading(false);
        setProgress(0);
      }, 1000);
    }
  }

  async function handleDownload(fileId, fileName) {
    const pass = prompt("Enter your Vault Password to decrypt this file:");
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
        alert("❌ Decryption failed. Incorrect password?");
      }
    } catch (err) {
      alert("❌ Download error.");
    }
  }

  async function handleDelete(fileId) {
    if (!confirm("Are you sure you want to delete this file permanently?")) return;

    try {
      const response = await fetch(`http://localhost:5000/delete/${fileId}`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${token}` }
      });

      if (response.ok) {
        alert("✅ File deleted.");
        fetchFiles(); // Refresh
      }
    } catch (err) {
      alert("❌ Delete failed.");
    }
  }

  return (
    <div className="min-h-screen bg-black text-white p-6 font-sans">
      <div className="flex justify-between items-center mb-8 border-b border-gray-800 pb-4">
        <h1 className="text-3xl text-blue-400 font-bold tracking-tight">🔐 SECURE VAULT</h1>
        <div className="flex items-center gap-4">
            <span className="text-gray-400">Welcome, {localStorage.getItem("username")}</span>
            <button onClick={() => { localStorage.clear(); window.location.href = "/"; }} className="bg-red-500 hover:bg-red-600 px-4 py-2 rounded transition">Logout</button>
        </div>
      </div>

      <div className="bg-gray-900 p-8 rounded-2xl mb-8 border border-blue-900 shadow-2xl">
        <h2 className="text-xl mb-6 font-semibold">📤 Upload New Document</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
                <label className="block text-sm text-gray-400 mb-2">Encryption Key (Password)</label>
                <input type="password" placeholder="Enter password to encrypt file" value={password} onChange={(e) => setPassword(e.target.value)}
                  className="w-full p-3 rounded bg-gray-800 text-white border border-gray-700 focus:ring-2 focus:ring-blue-500 outline-none" />
            </div>
            <div>
                <label className="block text-sm text-gray-400 mb-2">Select File</label>
                <input type="file" ref={fileInputRef} onChange={(e) => setFile(e.target.files[0])} 
                  className="w-full p-2 bg-gray-800 rounded border border-gray-700" />
            </div>
        </div>
        <button onClick={handleUpload} className="w-full bg-blue-600 hover:bg-blue-700 py-3 rounded-xl font-bold transition">
           {loading ? "Processing..." : "Encrypt & Upload to Vault"}
        </button>
        {message && <p className="text-green-400 mt-4 text-center">{message}</p>}
      </div>

      <div className="bg-gray-900 p-8 rounded-2xl border border-gray-800">
        <h2 className="text-xl mb-6 font-semibold">📁 Your Encrypted Files</h2>
        {files.length === 0 ? (
            <p className="text-gray-500 text-center py-10 italic">No files found in your vault.</p>
        ) : (
            <div className="grid gap-4">
              {files.map((f) => (
                <div key={f.id} className="flex justify-between items-center bg-gray-800 p-5 rounded-xl border border-gray-700 hover:border-blue-500 transition group">
                  <div className="flex items-center gap-4">
                    <span className="text-2xl">📄</span>
                    <div>
                        <div className="font-medium text-blue-100">{f.name}</div>
                        <div className="text-xs text-gray-500">{f.size} • {f.date}</div>
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <button onClick={() => handleDownload(f.id, f.name)} className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg text-sm transition">Download</button>
                    <button onClick={() => handleDelete(f.id)} className="bg-gray-700 hover:bg-red-600 px-4 py-2 rounded-lg text-sm transition">Delete</button>
                  </div>
                </div>
              ))}
            </div>
        )}
      </div>
    </div>
  );
}
