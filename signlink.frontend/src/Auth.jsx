// DESCRIPTION:  This React component handles user authentication (login and signup) for the ASL Translator app.
//                Updated for US8: ARIA labels, screen reader support, keyboard activation,
//                proper form structure, and accessible error feedback.
// LANGUAGE:     JAVASCRIPT (React.js)

import { useState } from "react";

export default function Auth({ onLogin }) {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [isSignup, setIsSignup] = useState(false);
    const [error, setError] = useState(null);

    const [firstName, setFirstName] = useState("");
    const [lastName, setLastName] = useState("");
    const [email, setEmail] = useState("");

    // Handle Enter or Space key activation (US8)
    const handleKeyActivate = (event, action) => {
        if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            action();
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);

        try {
            const endpoint = isSignup ? "signup" : "login";

            const body = isSignup
                ? { first_name: firstName, last_name: lastName, email, username, password }
                : { username, password };

            const res = await fetch(`/auth/${endpoint}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify(body),
            });

            if (!res.ok) {
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
            role="region"
            aria-label="User Authentication Panel"
            style={{
                maxWidth: "400px",
                margin: "3rem auto",
                padding: "2rem",
                border: "1px solid #ccc",
                borderRadius: "8px",
            }}
            tabIndex="0"
        >
            <h2
                tabIndex="0"
                aria-label={isSignup ? "Create Account Form" : "Login Form"}
            >
                {isSignup ? "Create Account" : "Login"}
            </h2>

            <form
                onSubmit={handleSubmit}
                role="form"
                aria-label={isSignup ? "Signup form" : "Login form"}
            >
                {isSignup && (
                    <>
                        {/* First Name */}
                        <div style={{ marginBottom: "1rem" }}>
                            <label htmlFor="firstNameInput">First Name</label>
                            <input
                                id="firstNameInput"
                                aria-label="First Name input field"
                                type="text"
                                value={firstName}
                                onChange={(e) => setFirstName(e.target.value)}
                                required
                                style={{ width: "100%", padding: "0.5rem" }}
                            />
                        </div>

                        {/* Last Name */}
                        <div style={{ marginBottom: "1rem" }}>
                            <label htmlFor="lastNameInput">Last Name</label>
                            <input
                                id="lastNameInput"
                                aria-label="Last Name input field"
                                type="text"
                                value={lastName}
                                onChange={(e) => setLastName(e.target.value)}
                                required
                                style={{ width: "100%", padding: "0.5rem" }}
                            />
                        </div>

                        {/* Email */}
                        <div style={{ marginBottom: "1rem" }}>
                            <label htmlFor="emailInput">Email</label>
                            <input
                                id="emailInput"
                                aria-label="Email input field"
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                                style={{ width: "100%", padding: "0.5rem" }}
                            />
                        </div>
                    </>
                )}

                {/* Username */}
                <div style={{ marginBottom: "1rem" }}>
                    <label htmlFor="usernameInput">Username</label>
                    <input
                        id="usernameInput"
                        aria-label="Username input field"
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                        style={{ width: "100%", padding: "0.5rem" }}
                    />
                </div>

                {/* Password */}
                <div style={{ marginBottom: "1rem" }}>
                    <label htmlFor="passwordInput">Password</label>
                    <input
                        id="passwordInput"
                        aria-label="Password input field"
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        style={{ width: "100%", padding: "0.5rem" }}
                    />
                </div>

                {/* Error Message */}
                {error && (
                    <p
                        role="alert"
                        aria-live="assertive"
                        style={{ color: "red" }}
                        tabIndex="0"
                    >
                        {error}
                    </p>
                )}

                {/* Submit button */}
                <button
                    type="submit"
                    className="a11y-btn"
                    aria-label={isSignup ? "Submit Sign Up form" : "Submit Login form"}
                    style={{ padding: "0.5rem 1rem", marginRight: "1rem" }}
                    onKeyDown={(e) => handleKeyActivate(e, () => { })}
                >
                    {isSignup ? "Sign Up" : "Login"}
                </button>

                {/* Toggle Login/Signup */}
                <button
                    type="button"
                    className="a11y-btn"
                    aria-label={
                        isSignup
                            ? "Switch to login mode"
                            : "Switch to sign up mode"
                    }
                    style={{ padding: "0.5rem 1rem" }}
                    onClick={() => setIsSignup(!isSignup)}
                    onKeyDown={(e) =>
                        handleKeyActivate(e, () => setIsSignup(!isSignup))
                    }
                >
                    {isSignup ? "Have an account? Login" : "New here? Sign Up"}
                </button>
            </form>
        </div>
    );
}
