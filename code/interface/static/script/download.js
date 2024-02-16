function downloadImages() {
    // Show the loading overlay
    document.getElementById('loadingOverlay').style.display = 'flex';

    var imageLinks = document.querySelectorAll('.image-link');
    var zip = new JSZip();
    var promises = [];

    imageLinks.forEach(function (link) {
        var image = link.querySelector('img');
        var imageUrl = image.src;

        // Exclude error images
        if (!imageUrl.includes('login_ico.png')) {
            var imageName = imageUrl.substring(imageUrl.lastIndexOf('/') + 1);
            var promise = fetch(imageUrl)
                .then(response => response.blob())
                .then(blob => zip.file(imageName, blob))
                .catch(error => console.error("Error downloading image:", error));

            promises.push(promise);
        }
    });

    // Wait for all promises to resolve before generating the zip
    Promise.all(promises)
        .then(() => {
            // Generate the zip file
            return zip.generateAsync({ type: 'blob' });
        })
        .then(function (content) {
            // Create a download link for the zip file
            var downloadLink = document.createElement('a');
            downloadLink.href = URL.createObjectURL(content);
            downloadLink.download = 'images.zip';
            downloadLink.click();

            // Hide the loading overlay after the download is complete
            document.getElementById('loadingOverlay').style.display = 'none';
        })
        .catch(error => {
            console.error("Error generating zip file:", error);
            // Hide the loading overlay in case of an error
            document.getElementById('loadingOverlay').style.display = 'none';
        });
}
