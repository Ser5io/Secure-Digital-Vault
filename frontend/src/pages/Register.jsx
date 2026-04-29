import { useState } from "react";

export default function Register() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  async function handleRegister() {
    // 1. Validation: Prevent empty entries
    if (!username.trim() || !password.trim()) {
      alert("❌ Please fill in all fields!");
      return;
    }

    try {
      // 2. Talk to the Python Backend
      const response = await fetch("http://localhost:5000/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password })
      });

      const data = await response.json();

      if (response.ok && data.status === "success") {
        alert("✅ Account created successfully!");
        window.location.href = "/"; // Go to login page
      } else {
        // 3. Show specific error (e.g. "the username is used")
        alert("❌ " + (data.message || "Registration failed"));
      }
    } catch (err) {
      alert("❌ Cannot connect to server. Ensure VaultBackend.py is running!");
    }
  }

  return (
    <div className="h-screen flex items-center justify-center bg-gradient-to-br from-black via-gray-900 to-black text-white">
      <div className="bg-gray-800 p-8 rounded-2xl w-80 shadow-2xl border border-gray-700">
        <h2 className="text-2xl mb-6 text-center font-bold text-blue-400">
          Create Account ✨
        </h2>

        <input
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="w-full p-2 mb-4 rounded bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        />

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
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
          onClick={handleRegister}
          className="w-full bg-green-600 hover:bg-green-700 p-2 rounded transition"
        >
          Register
        </button>

        <p className="text-sm mt-4 text-center">
          Already have an account?{" "}
          <span
            className="text-blue-400 cursor-pointer"
            onClick={() => (window.location.href = "/")}
          >
            Login
          </span>
        </p>
      </div>
    </div>
  );
}
