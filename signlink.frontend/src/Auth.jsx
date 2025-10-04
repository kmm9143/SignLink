import { useState } from "react";

export default function Auth({ onLogin }) {
    // Existing login/signup fields
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [isSignup, setIsSignup] = useState(false);
    const [error, setError] = useState(null);

    // New signup fields
    const [firstName, setFirstName] = useState("");
    const [lastName, setLastName] = useState("");
    const [email, setEmail] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);

        try {
            const endpoint = isSignup ? "signup" : "login";

            // Build request body
            const body = isSignup
                ? { first_name: firstName, last_name: lastName, email, username, password }
                : { username, password };

            const res = await fetch(`http://127.0.0.1:8000/auth/${endpoint}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(body),
            });

            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.detail || "Authentication failed");
            }

            const data = await res.json();
            onLogin(data);  // pass user info to App.jsx
        } catch (err) {
            console.error("Auth error:", err);
            setError(err.message);
        }
    };

    return (
        <div style={{ maxWidth: "400px", margin: "3rem auto", padding: "2rem", border: "1px solid #ccc", borderRadius: "8px" }}>
            <h2>{isSignup ? "Create Account" : "Login"}</h2>

            <form onSubmit={handleSubmit}>
                {isSignup && (
                    <>
                        <div style={{ marginBottom: "1rem" }}>
                            <label>First Name</label>
                            <input
                                type="text"
                                value={firstName}
                                onChange={(e) => setFirstName(e.target.value)}
                                required
                                style={{ width: "100%", padding: "0.5rem" }}
                            />
                        </div>
                        <div style={{ marginBottom: "1rem" }}>
                            <label>Last Name</label>
                            <input
                                type="text"
                                value={lastName}
                                onChange={(e) => setLastName(e.target.value)}
                                required
                                style={{ width: "100%", padding: "0.5rem" }}
                            />
                        </div>
                        <div style={{ marginBottom: "1rem" }}>
                            <label>Email</label>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                                style={{ width: "100%", padding: "0.5rem" }}
                            />
                        </div>
                    </>
                )}

                <div style={{ marginBottom: "1rem" }}>
                    <label>Username</label>
                    <input
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                        style={{ width: "100%", padding: "0.5rem" }}
                    />
                </div>

                <div style={{ marginBottom: "1rem" }}>
                    <label>Password</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        style={{ width: "100%", padding: "0.5rem" }}
                    />
                </div>

                {error && <p style={{ color: "red" }}>{error}</p>}

                <button type="submit" style={{ padding: "0.5rem 1rem", marginRight: "1rem" }}>
                    {isSignup ? "Sign Up" : "Login"}
                </button>

                <button
                    type="button"
                    onClick={() => setIsSignup(!isSignup)}
                    style={{ padding: "0.5rem 1rem" }}
                >
                    {isSignup ? "Have an account? Login" : "New here? Sign Up"}
                </button>
            </form>
        </div>
    );
}
