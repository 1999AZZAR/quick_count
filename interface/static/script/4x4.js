document.addEventListener('DOMContentLoaded', function () {
    const overlay = document.createElement('div');
    overlay.classList.add('overlay');
    document.body.appendChild(overlay);

    const imageLinks = document.querySelectorAll('.image-link');

    imageLinks.forEach(function (link) {
        link.addEventListener('click', function (event) {
            event.preventDefault();
            const imageUrl = this.querySelector('img').src;
            const overlayImage = new Image();
            overlayImage.src = imageUrl;
            overlay.innerHTML = '';
            overlay.appendChild(overlayImage);
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

