function setPattern(pattern) {
    document.getElementById('patternInput').value = pattern;
}

// Add file handling using the File System Access API
async function handleDirectorySelect() {
    try {
        const dirHandle = await window.showDirectoryPicker();
        // Handle directory access
    } catch (err) {
        console.error('Error accessing directory:', err);
    }
}

// Convert other tkinter functionality to web equivalents