// Squares Background Effect - Vanilla JavaScript
class SquaresBackground {
    constructor(options = {}) {
        this.direction = options.direction || 'right';
        this.speed = options.speed || 1;
        this.borderColor = options.borderColor || '#999';
        this.squareSize = options.squareSize || 40;
        this.hoverFillColor = options.hoverFillColor || '#222';
        this.className = options.className || '';
        
        this.canvas = null;
        this.context = null;
        this.animationId = null;
        this.numSquaresX = 0;
        this.numSquaresY = 0;
        this.gridOffset = { x: 0, y: 0 };
        this.hoveredSquare = null;
    }

    init(container) {
        this.canvas = document.createElement('canvas');
        this.context = this.canvas.getContext('2d');
        
        // Set up canvas styles
        this.canvas.style.width = '100%';
        this.canvas.style.height = '100%';
        this.canvas.style.border = 'none';
        this.canvas.style.display = 'block';
        this.canvas.style.position = 'absolute';
        this.canvas.style.top = '0';
        this.canvas.style.left = '0';
        this.canvas.style.zIndex = '-1';
        
        // Add canvas to container
        container.appendChild(this.canvas);
        
        this.resizeCanvas();
        this.setupEventListeners();
        this.animate();
    }

    resizeCanvas() {
        if (!this.canvas) return;
        
        this.canvas.width = this.canvas.offsetWidth;
        this.canvas.height = this.canvas.offsetHeight;
        this.numSquaresX = Math.ceil(this.canvas.width / this.squareSize) + 1;
        this.numSquaresY = Math.ceil(this.canvas.height / this.squareSize) + 1;
    }

    drawGrid() {
        if (!this.context || !this.canvas) return;
        
        const ctx = this.context;
        ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        const startX = Math.floor(this.gridOffset.x / this.squareSize) * this.squareSize;
        const startY = Math.floor(this.gridOffset.y / this.squareSize) * this.squareSize;

        for (let x = startX; x < this.canvas.width + this.squareSize; x += this.squareSize) {
            for (let y = startY; y < this.canvas.height + this.squareSize; y += this.squareSize) {
                const squareX = x - (this.gridOffset.x % this.squareSize);
                const squareY = y - (this.gridOffset.y % this.squareSize);

                if (
                    this.hoveredSquare &&
                    Math.floor((x - startX) / this.squareSize) === this.hoveredSquare.x &&
                    Math.floor((y - startY) / this.squareSize) === this.hoveredSquare.y
                ) {
                    ctx.fillStyle = this.hoverFillColor;
                    ctx.fillRect(squareX, squareY, this.squareSize, this.squareSize);
                }

                ctx.strokeStyle = this.borderColor;
                ctx.strokeRect(squareX, squareY, this.squareSize, this.squareSize);
            }
        }

        // Add radial gradient overlay
        const gradient = ctx.createRadialGradient(
            this.canvas.width / 2,
            this.canvas.height / 2,
            0,
            this.canvas.width / 2,
            this.canvas.height / 2,
            Math.sqrt(this.canvas.width ** 2 + this.canvas.height ** 2) / 2
        );
        gradient.addColorStop(0, 'rgba(0, 0, 0, 0)');
        gradient.addColorStop(1, 'rgba(0, 0, 0, 0.3)');

        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    }

    updateAnimation() {
        const effectiveSpeed = Math.max(this.speed, 0.1);
        
        switch (this.direction) {
            case 'right':
                this.gridOffset.x = (this.gridOffset.x - effectiveSpeed + this.squareSize) % this.squareSize;
                break;
            case 'left':
                this.gridOffset.x = (this.gridOffset.x + effectiveSpeed + this.squareSize) % this.squareSize;
                break;
            case 'up':
                this.gridOffset.y = (this.gridOffset.y + effectiveSpeed + this.squareSize) % this.squareSize;
                break;
            case 'down':
                this.gridOffset.y = (this.gridOffset.y - effectiveSpeed + this.squareSize) % this.squareSize;
                break;
            case 'diagonal':
                this.gridOffset.x = (this.gridOffset.x - effectiveSpeed + this.squareSize) % this.squareSize;
                this.gridOffset.y = (this.gridOffset.y - effectiveSpeed + this.squareSize) % this.squareSize;
                break;
            default:
                break;
        }

        this.drawGrid();
        this.animationId = requestAnimationFrame(() => this.updateAnimation());
    }

    handleMouseMove(event) {
        if (!this.canvas) return;
        
        const rect = this.canvas.getBoundingClientRect();
        const mouseX = event.clientX - rect.left;
        const mouseY = event.clientY - rect.top;

        const startX = Math.floor(this.gridOffset.x / this.squareSize) * this.squareSize;
        const startY = Math.floor(this.gridOffset.y / this.squareSize) * this.squareSize;

        const hoveredSquareX = Math.floor((mouseX + this.gridOffset.x - startX) / this.squareSize);
        const hoveredSquareY = Math.floor((mouseY + this.gridOffset.y - startY) / this.squareSize);

        if (
            !this.hoveredSquare ||
            this.hoveredSquare.x !== hoveredSquareX ||
            this.hoveredSquare.y !== hoveredSquareY
        ) {
            this.hoveredSquare = { x: hoveredSquareX, y: hoveredSquareY };
        }
    }

    handleMouseLeave() {
        this.hoveredSquare = null;
    }

    setupEventListeners() {
        if (!this.canvas) return;
        
        this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        this.canvas.addEventListener('mouseleave', () => this.handleMouseLeave());
        
        // Handle window resize
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                this.resizeCanvas();
            }, 100);
        });
    }

    animate() {
        this.updateAnimation();
    }

    stop() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
    }

    destroy() {
        this.stop();
        if (this.canvas && this.canvas.parentElement) {
            this.canvas.parentElement.removeChild(this.canvas);
        }
    }
}

// Initialize squares background when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check if we should use squares instead of letter glitch
    const useSquares = window.location.search.includes('bg=squares') || 
                      localStorage.getItem('backgroundType') === 'squares';
    
    if (useSquares) {
        // Remove existing letter glitch if present
        if (window.letterGlitch) {
            window.letterGlitch.destroy();
        }
        
        // Apply to body
        const body = document.body;
        
        // Create squares background instance
        const squaresBackground = new SquaresBackground({
            direction: 'diagonal',
            speed: 0.5,
            borderColor: '#333',
            squareSize: 50,
            hoverFillColor: '#444'
        });
        
        // Initialize the effect
        squaresBackground.init(body);
        
        // Store reference for potential cleanup
        window.squaresBackground = squaresBackground;
    }
});
