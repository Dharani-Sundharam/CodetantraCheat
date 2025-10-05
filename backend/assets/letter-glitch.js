// Letter Glitch Background Effect - Vanilla JavaScript
class LetterGlitch {
    constructor(options = {}) {
        this.glitchColors = options.glitchColors || ['#2b4539', '#61dca3', '#61b3dc'];
        this.glitchSpeed = options.glitchSpeed || 50;
        this.centerVignette = options.centerVignette || false;
        this.outerVignette = options.outerVignette || true;
        this.smooth = options.smooth !== false;
        this.characters = options.characters || 'ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$&*()-_+=/[]{};:<>.,0123456789';
        
        this.canvas = null;
        this.context = null;
        this.animationId = null;
        this.letters = [];
        this.grid = { columns: 0, rows: 0 };
        this.lastGlitchTime = Date.now();
        
        this.fontSize = 16;
        this.charWidth = 10;
        this.charHeight = 20;
        
        this.lettersAndSymbols = Array.from(this.characters);
    }

    init(container) {
        this.canvas = document.createElement('canvas');
        this.context = this.canvas.getContext('2d');
        
        // Set up canvas styles
        this.canvas.style.display = 'block';
        this.canvas.style.width = '100%';
        this.canvas.style.height = '100%';
        this.canvas.style.position = 'fixed';
        this.canvas.style.top = '0';
        this.canvas.style.left = '0';
        this.canvas.style.zIndex = '-1';
        this.canvas.style.pointerEvents = 'none';
        
        // Create container styles
        container.style.position = 'relative';
        container.style.overflow = 'hidden';
        
        // Add canvas to container
        container.appendChild(this.canvas);
        
        // Add vignette effects
        if (this.outerVignette) {
            const outerVignette = document.createElement('div');
            outerVignette.style.position = 'absolute';
            outerVignette.style.top = '0';
            outerVignette.style.left = '0';
            outerVignette.style.width = '100%';
            outerVignette.style.height = '100%';
            outerVignette.style.pointerEvents = 'none';
            outerVignette.style.zIndex = '1';
            outerVignette.style.background = 'radial-gradient(circle, rgba(0,0,0,0) 60%, rgba(0,0,0,1) 100%)';
            container.appendChild(outerVignette);
        }
        
        if (this.centerVignette) {
            const centerVignette = document.createElement('div');
            centerVignette.style.position = 'absolute';
            centerVignette.style.top = '0';
            centerVignette.style.left = '0';
            centerVignette.style.width = '100%';
            centerVignette.style.height = '100%';
            centerVignette.style.pointerEvents = 'none';
            centerVignette.style.zIndex = '1';
            centerVignette.style.background = 'radial-gradient(circle, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0) 60%)';
            container.appendChild(centerVignette);
        }
        
        this.resizeCanvas();
        this.animate();
        
        // Handle window resize
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                this.stop();
                this.resizeCanvas();
                this.animate();
            }, 100);
        });
    }

    getRandomChar() {
        return this.lettersAndSymbols[Math.floor(Math.random() * this.lettersAndSymbols.length)];
    }

    getRandomColor() {
        return this.glitchColors[Math.floor(Math.random() * this.glitchColors.length)];
    }

    hexToRgb(hex) {
        const shorthandRegex = /^#?([a-f\d])([a-f\d])([a-f\d])$/i;
        hex = hex.replace(shorthandRegex, (m, r, g, b) => {
            return r + r + g + g + b + b;
        });

        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result
            ? {
                r: parseInt(result[1], 16),
                g: parseInt(result[2], 16),
                b: parseInt(result[3], 16)
            }
            : null;
    }

    interpolateColor(start, end, factor) {
        const result = {
            r: Math.round(start.r + (end.r - start.r) * factor),
            g: Math.round(start.g + (end.g - start.g) * factor),
            b: Math.round(start.b + (end.b - start.b) * factor)
        };
        return `rgb(${result.r}, ${result.g}, ${result.b})`;
    }

    calculateGrid(width, height) {
        const columns = Math.ceil(width / this.charWidth);
        const rows = Math.ceil(height / this.charHeight);
        return { columns, rows };
    }

    initializeLetters(columns, rows) {
        this.grid = { columns, rows };
        const totalLetters = columns * rows;
        this.letters = Array.from({ length: totalLetters }, () => ({
            char: this.getRandomChar(),
            color: this.getRandomColor(),
            targetColor: this.getRandomColor(),
            colorProgress: 1
        }));
    }

    resizeCanvas() {
        if (!this.canvas) return;

        const dpr = window.devicePixelRatio || 1;
        const width = window.innerWidth;
        const height = window.innerHeight;

        this.canvas.width = width * dpr;
        this.canvas.height = height * dpr;

        this.canvas.style.width = `${width}px`;
        this.canvas.style.height = `${height}px`;

        if (this.context) {
            this.context.setTransform(dpr, 0, 0, dpr, 0, 0);
        }

        const { columns, rows } = this.calculateGrid(width, height);
        this.initializeLetters(columns, rows);

        this.drawLetters();
    }

    drawLetters() {
        if (!this.context || this.letters.length === 0) return;
        const ctx = this.context;
        const width = this.canvas.width / (window.devicePixelRatio || 1);
        const height = this.canvas.height / (window.devicePixelRatio || 1);
        ctx.clearRect(0, 0, width, height);
        ctx.font = `${this.fontSize}px monospace`;
        ctx.textBaseline = 'top';

        this.letters.forEach((letter, index) => {
            const x = (index % this.grid.columns) * this.charWidth;
            const y = Math.floor(index / this.grid.columns) * this.charHeight;
            ctx.fillStyle = letter.color;
            ctx.fillText(letter.char, x, y);
        });
    }

    updateLetters() {
        if (!this.letters || this.letters.length === 0) return;

        const updateCount = Math.max(1, Math.floor(this.letters.length * 0.05));

        for (let i = 0; i < updateCount; i++) {
            const index = Math.floor(Math.random() * this.letters.length);
            if (!this.letters[index]) continue;

            this.letters[index].char = this.getRandomChar();
            this.letters[index].targetColor = this.getRandomColor();

            if (!this.smooth) {
                this.letters[index].color = this.letters[index].targetColor;
                this.letters[index].colorProgress = 1;
            } else {
                this.letters[index].colorProgress = 0;
            }
        }
    }

    handleSmoothTransitions() {
        let needsRedraw = false;
        this.letters.forEach(letter => {
            if (letter.colorProgress < 1) {
                letter.colorProgress += 0.05;
                if (letter.colorProgress > 1) letter.colorProgress = 1;

                const startRgb = this.hexToRgb(letter.color);
                const endRgb = this.hexToRgb(letter.targetColor);
                if (startRgb && endRgb) {
                    letter.color = this.interpolateColor(startRgb, endRgb, letter.colorProgress);
                    needsRedraw = true;
                }
            }
        });

        if (needsRedraw) {
            this.drawLetters();
        }
    }

    animate() {
        const now = Date.now();
        if (now - this.lastGlitchTime >= this.glitchSpeed) {
            this.updateLetters();
            this.drawLetters();
            this.lastGlitchTime = now;
        }

        if (this.smooth) {
            this.handleSmoothTransitions();
        }

        this.animationId = requestAnimationFrame(() => this.animate());
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

// Initialize letter glitch background when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check if we should use letter glitch (all pages except login, signup, dashboard)
    const currentPath = window.location.pathname;
    const useLetters = !currentPath.includes('login.html') && 
                      !currentPath.includes('signup.html') && 
                      !currentPath.includes('dashboard.html') &&
                      !window.location.search.includes('bg=squares');
    
    if (useLetters) {
        // Wait a bit for page to fully load
        setTimeout(() => {
            // Apply to body or specific container
            const body = document.body;
            
        // Create letter glitch instance
        const letterGlitch = new LetterGlitch({
            glitchColors: ['#2b4539', '#61dca3', '#61b3dc'],
            glitchSpeed: 150,
            centerVignette: false,
            outerVignette: true,
            smooth: true
        });
            
            // Initialize the effect
            letterGlitch.init(body);
            
            // Store reference for potential cleanup
            window.letterGlitch = letterGlitch;
            
            console.log('Letter glitch initialized on page:', window.location.pathname);
        }, 100);
    }
});
