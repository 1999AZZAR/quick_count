document.addEventListener('DOMContentLoaded', function () {
    const imageLinks = document.querySelectorAll('.image-link');

    imageLinks.forEach(function (link) {
        link.addEventListener('click', function (event) {
            // Continue with normal link behavior if the event is not prevented
            if (!event.defaultPrevented) {
                return;
            }

            event.preventDefault();
            const targetUrl = this.getAttribute('href');
            window.location.href = targetUrl; // Directly navigate to the specified page
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