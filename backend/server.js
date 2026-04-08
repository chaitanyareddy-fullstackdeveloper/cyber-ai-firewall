const express = require("express");
const app = express();

app.use(express.json());

// Root
app.get("/", (req, res) => {
    res.send("Server is running ✅");
});

// ✅ RESET
app.post("/reset", (req, res) => {
    res.status(200).json({
        success: true,
        message: "Environment reset"
    });
});

// ✅ STEP
app.post("/step", (req, res) => {
    res.status(200).json({
        success: true,
        message: "Step executed"
    });
});

// ✅ STATE
app.get("/state", (req, res) => {
    res.status(200).json({
        state: "running"
    });
});

const PORT = 3000;

app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});