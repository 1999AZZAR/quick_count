
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
    grafikUmum.style.width = Math.min(imgWidth, 640) + 'px'; // Set width based on loaded image's width, capped at 640px
};

img.onerror = function() {
    // Handle error (optional): For example, you can keep the initial width or set a default width.
    grafikUmum.style.width = '470px';
};
