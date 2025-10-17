// DESCRIPTION:  This React component handles user authentication (login and signup) for the ASL Translator app.
//                It manages user form inputs, toggles between login and signup modes, validates responses,
//                and communicates with the FastAPI backend to authenticate users.
// LANGUAGE:     JAVASCRIPT (React.js)
// SOURCE(S):    [1] React Documentation. (n.d.). Using the State Hook. Retrieved October 4, 2025, from https://react.dev/reference/react/useState
//               [2] MDN Web Docs. (n.d.). Fetch API. (n.d.). Retrieved October 4, 2025, from https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API
//               [3] FastAPI Documentation. (n.d.). Request Body. Retrieved October 4, 2025, from https://fastapi.tiangolo.com/tutorial/body/
//               [4] React Documentation. (n.d.). Handling Forms. Retrieved October 4, 2025, from https://react.dev/learn/sharing-state-between-components

import { useState } from "react";

export default function Auth({ onLogin }) {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [isSignup, setIsSignup] = useState(false);
    const [error, setError] = useState(null);

    const [firstName, setFirstName] = useState("");
    const [lastName, setLastName] = useState("");
    const [email, setEmail] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);

        try {
            const endpoint = isSignup ? "signup" : "login";

            const body = isSignup
                ? { first_name: firstName, last_name: lastName, email, username, password }
                : { username, password };

            // Use relative URL so Vite dev server proxy handles the request (avoids CORS)
            const res = await fetch(`/auth/${endpoint}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include", // include cookies if backend uses session cookies
                body: JSON.stringify(body),
            });

            if (!res.ok) {
                // Try to parse JSON error, fall back to text
                let errMsg = "Authentication failed";
                try {
                    const errData = await res.json();
                    errMsg = errData?.detail || JSON.stringify(errData) || errMsg;
                } catch {
                    const text = await res.text().catch(() => null);
                    if (text) errMsg = text;
                }
                throw new Error(errMsg);
            }

            const data = await res.json();
            onLogin(data);
        } catch (err) {
            console.error("Auth error:", err);
            setError(err.message);
        }
    };

    return (
        <div
            style={{
                maxWidth: "400px",
                margin: "3rem auto",
                padding: "2rem",
                border: "1px solid #ccc",
                borderRadius: "8px",
            }}
        >
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

                <button type="button" onClick={() => setIsSignup(!isSignup)} style={{ padding: "0.5rem 1rem" }}>
                    {isSignup ? "Have an account? Login" : "New here? Sign Up"}
                </button>
            </form>
        </div>
    );
}