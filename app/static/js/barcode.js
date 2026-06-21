// Barcode scanning utility using Quagga2
document.addEventListener("DOMContentLoaded", function () {
    const startBtn = document.getElementById("start-scanner-btn");
    const stopBtn = document.getElementById("stop-scanner-btn");
    const scannerContainer = document.getElementById("scanner-interactive");
    const barcodeResultDiv = document.getElementById("barcode-result");
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    if (!startBtn) return; // Only run on pages with scanner elements

    let scannerIsRunning = false;

    startBtn.addEventListener("click", function () {
        if (scannerIsRunning) return;
        
        scannerContainer.style.display = "block";
        barcodeResultDiv.innerHTML = "<p>Initializing camera...</p>";
        
        // Check browser camera access
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(function (stream) {
                // Stop the local test stream immediately and let Quagga handle it
                stream.getTracks().forEach(track => track.stop());
                initQuagga();
            })
            .catch(function (err) {
                console.error("Camera access error:", err);
                barcodeResultDiv.innerHTML = `<p style="color: red;">Camera access denied. Please grant permission or type the barcode manually.</p>`;
            });
    });

    stopBtn.addEventListener("click", function () {
        if (!scannerIsRunning) return;
        stopQuagga();
    });

    function initQuagga() {
        Quagga.init({
            inputStream: {
                name: "Live",
                type: "LiveStream",
                target: scannerContainer,
                constraints: {
                    facingMode: "environment" // Prefer back camera
                },
            },
            decoder: {
                readers: [
                    "code_128_reader",
                    "ean_reader",
                    "ean_8_reader",
                    "code_39_reader",
                    "upc_reader"
                ]
            }
        }, function (err) {
            if (err) {
                console.error("Quagga initialization failed:", err);
                barcodeResultDiv.innerHTML = `<p style="color: red;">Error starting camera scanner: ${err.message}</p>`;
                return;
            }
            console.log("Quagga initialization finished. Ready to start.");
            Quagga.start();
            scannerIsRunning = true;
            startBtn.style.display = "none";
            stopBtn.style.display = "inline-block";
            barcodeResultDiv.innerHTML = "<p>Scanning... Hold barcode steady in front of the camera.</p>";
        });

        // Event listener for scanned codes
        Quagga.onDetected(onBarcodeDetected);
    }

    let throttleTimeout = null;

    function onBarcodeDetected(result) {
        if (!result || !result.codeResult || !result.codeResult.code) return;
        
        const code = result.codeResult.code;
        console.log("Barcode detected:", code);

        // Throttle to prevent multiple requests simultaneously
        if (throttleTimeout) return;
        throttleTimeout = setTimeout(() => { throttleTimeout = null; }, 3000);

        // Play subtle beep sound or audio cue if needed
        barcodeResultDiv.innerHTML = `<p>Detected: <strong>${code}</strong>. Looking up...</p>`;
        
        // Stop scanner to prevent further reads while processing
        stopQuagga();

        // Perform lookup
        fetch("/food/barcode/lookup", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRF-Token": csrfToken,
                "X-Requested-With": "XMLHttpRequest"
            },
            body: JSON.stringify({ barcode: code })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("Product not found");
            }
            return response.json();
        })
        .then(data => {
            // Success - Redirect user to log this food item
            barcodeResultDiv.innerHTML = `<p style="color: green;">Found: <strong>${data.name}</strong>! Redirecting to log...</p>`;
            setTimeout(() => {
                window.location.href = `/food/log?food_item_id=${data.id}`;
            }, 1000);
        })
        .catch(err => {
            console.error("Lookup error:", err);
            barcodeResultDiv.innerHTML = `
                <p style="color: red;">Product not found in Open Food Facts database.</p>
                <button class="btn-premium" onclick="window.location.href='/food/search'" style="margin-top: 1rem; padding: 0.75rem 1.5rem;">SEARCH MANUALLY</button>
            `;
            // Re-show start button so they can try again
            startBtn.style.display = "inline-block";
            stopBtn.style.display = "none";
        });
    }

    function stopQuagga() {
        Quagga.stop();
        scannerIsRunning = false;
        startBtn.style.display = "inline-block";
        stopBtn.style.display = "none";
        scannerContainer.style.display = "none";
        barcodeResultDiv.innerHTML = "<p>Scanner stopped.</p>";
    }
});
