<script>
    let videoElement;
    let canvasElement;
    let context;
    let videoStream;

    function startCamera() {
        if (!videoElement) {
            videoElement = document.createElement('video');
            videoElement.setAttribute('autoplay', '');
            videoElement.setAttribute('playsinline', '');
            videoElement.style.width = '480px';
            videoElement.style.height = '480px';
            document.body.appendChild(videoElement);

            canvasElement = document.createElement('canvas');
            canvasElement.style.display = 'none';
            context = canvasElement.getContext('2d');
        }

        navigator.mediaDevices.getUserMedia({ video: true })
            .then(stream => {
                videoStream = stream;
                videoElement.srcObject = stream;
            })
            .catch(err => console.error('Error accessing webcam:', err));
    }

    function stopCamera() {
        if (videoStream) {
            videoStream.getTracks().forEach(track => track.stop());
        }
        if (videoElement) {
            videoElement.remove();
            videoElement = null;
        }
        if (canvasElement) {
            canvasElement.remove();
            canvasElement = null;
        }
    }

    function captureImage() {
        if (videoElement) {
            canvasElement.width = videoElement.videoWidth;
            canvasElement.height = videoElement.videoHeight;
            context.drawImage(videoElement, 0, 0, canvasElement.width, canvasElement.height);
            const dataURL = canvasElement.toDataURL('image/jpeg');
            google.colab.kernel.invokeFunction('notebook.capture_image', [dataURL], {});
        } else {
            alert('Camera is not active.');
        }
    }

    // יצירת כפתורים
    const startButton = document.createElement('button');
    startButton.innerText = 'Start Camera';
    startButton.onclick = startCamera;
    document.body.appendChild(startButton);

    const stopButton = document.createElement('button');
    stopButton.innerText = 'Stop Camera';
    stopButton.onclick = stopCamera;
    document.body.appendChild(stopButton);

    const captureButton = document.createElement('button');
    captureButton.innerText = 'Capture Image';
    captureButton.onclick = captureImage;
    document.body.appendChild(captureButton);
</script>
