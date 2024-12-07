function login() {
    const email = document.getElementById("loginEmail").value;
    const password = document.getElementById("loginPassword").value;

    
    if (email === "test@example.com" && password === "password") {
        alert("Login successful!");
        window.location.href = "dashboard.html";
    } else {
        alert("Invalid credentials!");
    }
}

function register() {
    const name = document.getElementById("registerName").value;
    const email = document.getElementById("registerEmail").value;
    const password = document.getElementById("registerPassword").value;

    alert(`Registered successfully as ${name}`);
    window.location.href = "index.html";
}

function search() {
    const query = document.getElementById("searchInput").value;
    const resultsContainer = document.getElementById("searchResults");

    resultsContainer.innerHTML = `<p>Searching for "${query}"...</p>`;
}
