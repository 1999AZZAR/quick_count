document.addEventListener('DOMContentLoaded', function () {
    const overlay = document.createElement('div');
    overlay.classList.add('overlay');
    document.body.appendChild(overlay);

    const imageLinks = document.querySelectorAll('.image-link');

    imageLinks.forEach(function (link) {
        link.addEventListener('click', function (event) {
            event.preventDefault();
            const imageUrl = this.querySelector('img').src;

            // Creating an image element
            const overlayImage = new Image();
            overlayImage.src = imageUrl;

            // Creating a download button with an icon
            const downloadButton = document.createElement('a');
            downloadButton.href = imageUrl;
            downloadButton.download = 'downloaded_image.png';

            // Adding a download icon with the specified image path
            const downloadIcon = document.createElement('img');
            downloadIcon.src = '/static/icons/down.png';
            downloadIcon.alt = 'Download Icon';

            // Appending image and download button with icon to the overlay
            overlay.innerHTML = '';
            overlay.appendChild(overlayImage);
            downloadButton.appendChild(downloadIcon);
            overlay.appendChild(downloadButton);
            overlay.style.display = 'flex';
        });
    });

    overlay.addEventListener('click', function () {
        overlay.style.display = 'none';
    });
});

function toggleSidePanel() {
    const sidePanel = document.querySelector('.side-panel');
    sidePanel.classList.toggle('collapsed');

    const overlay = document.querySelector('.overlay');
    overlay.style.display = 'block';
}

function closeOverlay() {
    const sidePanel = document.querySelector('.side-panel');
    sidePanel.classList.remove('collapsed');

    const overlay = document.querySelector('.overlay');
    overlay.style.display = 'none';
}

var grafikUmum = document.querySelector('.grafik_umum');
var img = grafikUmum.querySelector('img');

img.onload = function() {
    var imgWidth = img.width;
    grafikUmum.style.width = Math.min(imgWidth, 640) + 'px'; 
};

img.onerror = function() {
    grafikUmum.style.width = '470px';
};

function handleImageError(img, defaultSrc) {
    img.onerror = null; 
    img.src = defaultSrc; 
}