// Debug script for background effects
console.log('Debug script loaded');

// Check if scripts are loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded');
    console.log('LetterGlitch available:', typeof LetterGlitch !== 'undefined');
    console.log('SquaresBackground available:', typeof SquaresBackground !== 'undefined');
    console.log('Current URL:', window.location.href);
    console.log('Background type from localStorage:', localStorage.getItem('backgroundType'));
    console.log('URL has bg=squares:', window.location.search.includes('bg=squares'));
    
    // Check for existing backgrounds
    setTimeout(() => {
        const canvases = document.querySelectorAll('canvas');
        console.log('Canvas elements found:', canvases.length);
        canvases.forEach((canvas, index) => {
            console.log(`Canvas ${index}:`, {
                width: canvas.width,
                height: canvas.height,
                style: canvas.style.cssText,
                parent: canvas.parentElement.tagName
            });
        });
        
        // Check if backgrounds are initialized
        console.log('Letter glitch instance:', window.letterGlitch);
        console.log('Squares background instance:', window.squaresBackground);
    }, 2000);
});
