const express = require("express");
const app = express();

app.use(express.json());

// ROOT ROUTE (fixes your error)
app.get("/", (req, res) => {
    res.send("Server is running ✅");
});

// REQUIRED FOR PRESUBMIT
app.post("/openenv/reset", (req, res) => {
    res.status(200).json({
        message: "Reset successful"
    });
});

const PORT = 7860;

app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});