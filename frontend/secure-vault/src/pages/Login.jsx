import { useState } from "react";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function handleLogin() {
    setError("");
    try {
      const response = await fetch("http://localhost:5000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
      });

      const data = await response.json();

      if (response.ok && data.status === "success") {
        localStorage.setItem("token", data.token);
        localStorage.setItem("user_id", data.user_id);
        localStorage.setItem("username", username);
        window.location.href = "/dashboard";
      } else {
        // Show specific error from backend (Incorrect password / User not found)
        alert("❌ " + (data.message || "Login failed"));
        setError(data.message || "Login failed");
      }
    } catch (err) {
      alert("❌ Cannot connect to server.");
      setError("Cannot connect to server.");
    }
  }

  return (
    <div className="h-screen flex items-center justify-center bg-gradient-to-br from-black via-gray-900 to-black text-white">
      <div className="bg-gray-800 p-8 rounded-2xl w-80 shadow-2xl border border-gray-700">
        <h2 className="text-2xl mb-6 text-center font-bold text-blue-400">
          Secure Digital Vault 🔐
        </h2>

        <input
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="w-full p-2 mb-4 rounded bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full p-2 mb-4 rounded bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        />

        <button
          onClick={handleLogin}
          className="w-full bg-blue-600 hover:bg-blue-700 p-2 rounded transition duration-300"
        >
          Login
        </button>

        <p className="text-sm mt-4 text-center">
            Don't have an account?{" "}
            <span
                className="text-blue-400 cursor-pointer"
                onClick={() => (window.location.href = "/register")}
            >
                Register
            </span>
        </p>
      </div>
    </div>
  );
}
