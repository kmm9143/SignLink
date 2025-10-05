// DESCRIPTION:  This React component handles user authentication (login and signup) for the ASL Translator app.
//                It manages user form inputs, toggles between login and signup modes, validates responses,
//                and communicates with the FastAPI backend to authenticate users.
// LANGUAGE:     JAVASCRIPT (React.js)
// SOURCE(S):    [1] React Documentation. (n.d.). Using the State Hook. Retrieved October 4, 2025, from https://react.dev/reference/react/useState
//               [2] MDN Web Docs. (n.d.). Fetch API. Retrieved October 4, 2025, from https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API
//               [3] FastAPI Documentation. (n.d.). Request Body. Retrieved October 4, 2025, from https://fastapi.tiangolo.com/tutorial/body/
//               [4] React Documentation. (n.d.). Handling Forms. Retrieved October 4, 2025, from https://react.dev/learn/sharing-state-between-components

// -----------------------------------------------------------------------------
// Step 1: Import required dependency
// -----------------------------------------------------------------------------
import { useState } from "react";                    // Import React Hook for managing component state

// -----------------------------------------------------------------------------
// Step 2: Define Auth component
// -----------------------------------------------------------------------------
export default function Auth({ onLogin }) {          // Accepts a callback prop (onLogin) from parent to store authenticated user data
    // -------------------------------------------------------------------------
    // Authentication-related state variables
    // -------------------------------------------------------------------------
    const [username, setUsername] = useState("");    // Stores username input field value
    const [password, setPassword] = useState("");    // Stores password input field value
    const [isSignup, setIsSignup] = useState(false); // Boolean to toggle between Login and Signup modes
    const [error, setError] = useState(null);        // Stores any error message from backend or validation

    // -------------------------------------------------------------------------
    // Additional signup-only fields
    // -------------------------------------------------------------------------
    const [firstName, setFirstName] = useState("");  // Stores first name input during signup
    const [lastName, setLastName] = useState("");    // Stores last name input during signup
    const [email, setEmail] = useState("");          // Stores email input during signup

    // -------------------------------------------------------------------------
    // Step 3: Define handler for form submission
    // -------------------------------------------------------------------------
    const handleSubmit = async (e) => {
        e.preventDefault();                          // Prevent default form submission behavior (page reload)
        setError(null);                              // Reset previous error messages before new attempt

        try {
            const endpoint = isSignup ? "signup" : "login"; // Dynamically choose backend endpoint

            // Build request body depending on mode
            const body = isSignup
                ? { first_name: firstName, last_name: lastName, email, username, password } // Include extra signup fields
                : { username, password };              // Login requires only username and password

            // Send POST request to FastAPI authentication endpoint
            const res = await fetch(`http://127.0.0.1:8000/auth/${endpoint}`, {
                method: "POST",                       // HTTP POST request for creating or verifying user
                headers: { "Content-Type": "application/json" }, // Send JSON data
                body: JSON.stringify(body),           // Convert body object to JSON string
            });

            // Check if backend returned an error status
            if (!res.ok) {
                const errData = await res.json();     // Parse backend error message
                throw new Error(errData.detail || "Authentication failed"); // Throw detailed error
            }

            // Parse and store successful response (user info)
            const data = await res.json();

            onLogin(data);                            // Pass authenticated user info to App.jsx parent
        } catch (err) {
            console.error("Auth error:", err);        // Log error to console for debugging
            setError(err.message);                    // Update error state for UI feedback
        }
    };

    // -------------------------------------------------------------------------
    // Step 4: Render authentication UI
    // -------------------------------------------------------------------------
    return (
        <div
            style={{
                maxWidth: "400px",                    // Set form container width
                margin: "3rem auto",                  // Center horizontally with vertical spacing
                padding: "2rem",                      // Internal spacing
                border: "1px solid #ccc",             // Light border around form
                borderRadius: "8px",                  // Rounded corners
            }}
        >
            {/* Dynamic header changes based on mode */}
            <h2>{isSignup ? "Create Account" : "Login"}</h2>

            {/* Form submission triggers handleSubmit */}
            <form onSubmit={handleSubmit}>
                {/* -------------------------------------------------------------
                    Conditional rendering: show signup fields only if isSignup=true
                ------------------------------------------------------------- */}
                {isSignup && (
                    <>
                        {/* First Name input */}
                        <div style={{ marginBottom: "1rem" }}>
                            <label>First Name</label>
                            <input
                                type="text"
                                value={firstName}
                                onChange={(e) => setFirstName(e.target.value)} // Update state on change
                                required
                                style={{ width: "100%", padding: "0.5rem" }}
                            />
                        </div>

                        {/* Last Name input */}
                        <div style={{ marginBottom: "1rem" }}>
                            <label>Last Name</label>
                            <input
                                type="text"
                                value={lastName}
                                onChange={(e) => setLastName(e.target.value)} // Update state on change
                                required
                                style={{ width: "100%", padding: "0.5rem" }}
                            />
                        </div>

                        {/* Email input */}
                        <div style={{ marginBottom: "1rem" }}>
                            <label>Email</label>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)} // Update email state
                                required
                                style={{ width: "100%", padding: "0.5rem" }}
                            />
                        </div>
                    </>
                )}

                {/* -------------------------------------------------------------
                    Username input field (used for both login and signup)
                ------------------------------------------------------------- */}
                <div style={{ marginBottom: "1rem" }}>
                    <label>Username</label>
                    <input
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)} // Update username state
                        required
                        style={{ width: "100%", padding: "0.5rem" }}
                    />
                </div>

                {/* -------------------------------------------------------------
                    Password input field (used for both login and signup)
                ------------------------------------------------------------- */}
                <div style={{ marginBottom: "1rem" }}>
                    <label>Password</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)} // Update password state
                        required
                        style={{ width: "100%", padding: "0.5rem" }}
                    />
                </div>

                {/* -------------------------------------------------------------
                    Error message display
                ------------------------------------------------------------- */}
                {error && <p style={{ color: "red" }}>{error}</p>}

                {/* -------------------------------------------------------------
                    Submit button (Login or Sign Up)
                ------------------------------------------------------------- */}
                <button
                    type="submit"
                    style={{ padding: "0.5rem 1rem", marginRight: "1rem" }}
                >
                    {isSignup ? "Sign Up" : "Login"}  {/* Dynamic button label */}
                </button>

                {/* -------------------------------------------------------------
                    Toggle button to switch between login and signup modes
                ------------------------------------------------------------- */}
                <button
                    type="button"
                    onClick={() => setIsSignup(!isSignup)} // Toggle form mode
                    style={{ padding: "0.5rem 1rem" }}
                >
                    {isSignup ? "Have an account? Login" : "New here? Sign Up"}
                </button>
            </form>
        </div>
    );
}