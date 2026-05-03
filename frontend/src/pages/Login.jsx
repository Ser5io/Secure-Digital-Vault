import { useState } from "react";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [mfaCode, setMfaCode] = useState("");
  const [mfaRequired, setMfaRequired] = useState(false);
  const [userId, setUserId] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleLogin() {
    setError("");
    setLoading(true);
    try {
      const response = await fetch("http://localhost:5000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
      });

      const data = await response.json();

      if (response.ok) {
        if (data.status === "mfa_required") {
          setMfaRequired(true);
          setUserId(data.user_id);
          window.alert("✅ Verification code sent to your email!");
        } else if (data.status === "success") {
          localStorage.setItem("token", data.token);
          localStorage.setItem("user_id", data.user_id);
          localStorage.setItem("username", username);
          window.location.href = "/dashboard";
        }
      } else {
        window.alert("❌ " + (data.message || "Login failed"));
        setError(data.message || "Login failed");
      }
    } catch (err) {
      window.alert("❌ Cannot connect to server. Ensure Backend is running!");
      setError("Cannot connect to server.");
    } finally {
      setLoading(false);
    }
  }

  async function handleVerifyMFA() {
    setError("");
    setLoading(true);
    try {
      const response = await fetch("http://localhost:5000/verify-mfa", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId, code: mfaCode })
      });

      const data = await response.json();

      if (response.ok && data.status === "success") {
        localStorage.setItem("token", data.token);
        localStorage.setItem("user_id", data.user_id);
        localStorage.setItem("username", username);
        window.location.href = "/dashboard";
      } else {
        window.alert("❌ " + (data.message || "Verification failed"));
        setError(data.message || "Verification failed");
      }
    } catch (err) {
      window.alert("❌ Verification error.");
      setError("Connection error.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="h-screen flex items-center justify-center bg-gradient-to-br from-black via-gray-900 to-black text-white">
      <div className="bg-gray-800 p-8 rounded-2xl w-80 shadow-2xl border border-gray-700">
        <h2 className="text-2xl mb-6 text-center font-bold text-blue-400">
          Secure Digital Vault 🔐
        </h2>

        {error && <p className="text-red-400 text-sm mb-4 text-center">{error}</p>}

        {!mfaRequired ? (
          <>
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
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 p-2 rounded transition duration-300 disabled:opacity-50"
            >
              {loading ? "Processing..." : "Login"}
            </button>
          </>
        ) : (
          <>
            <p className="text-sm text-gray-400 mb-4 text-center">
              Enter the 6-digit code sent to your email.
            </p>
            <input
              placeholder="6-digit Code"
              value={mfaCode}
              maxLength={6}
              onChange={(e) => setMfaCode(e.target.value)}
              className="w-full p-2 mb-4 rounded bg-gray-700 text-white text-center text-xl tracking-widest focus:outline-none focus:ring-2 focus:ring-blue-500"
            />

            <button
              onClick={handleVerifyMFA}
              disabled={loading}
              className="w-full bg-green-600 hover:bg-green-700 p-2 rounded transition duration-300 disabled:opacity-50"
            >
              {loading ? "Verifying..." : "Verify & Access Vault"}
            </button>
            <button
              onClick={() => setMfaRequired(false)}
              className="w-full mt-2 text-sm text-gray-400 hover:text-white transition"
            >
              Back to Login
            </button>
          </>
        )}

        {!mfaRequired && (
          <p className="text-sm mt-4 text-center">
              Don't have an account?{" "}
              <span
                  className="text-blue-400 cursor-pointer"
                  onClick={() => (window.location.href = "/register")}
              >
                  Register
              </span>
          </p>
        )}
      </div>
    </div>
  );
}
