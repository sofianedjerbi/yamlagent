/**
 * Calc3D Scene Engine
 *
 * 3D rendering and animation using Three.js
 */

import { CONFIG } from './config.js';

export class Scene3D {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.particles = null;
        this.grid = null;
        this.animationId = null;
        this.time = 0;

        if (this.canvas) {
            this.init();
        }
    }

    /**
     * Initialize Three.js scene
     */
    init() {
        // Check if Three.js is available
        if (typeof THREE === 'undefined') {
            console.warn('Three.js not loaded, 3D scene disabled');
            return;
        }

        // Create scene
        this.scene = new THREE.Scene();
        this.scene.fog = new THREE.Fog(CONFIG.colors.darkBg, 10, 50);

        // Create camera
        this.camera = new THREE.PerspectiveCamera(
            CONFIG.scene.fov,
            this.canvas.clientWidth / this.canvas.clientHeight,
            CONFIG.scene.near,
            CONFIG.scene.far
        );
        this.camera.position.z = CONFIG.scene.cameraZ;

        // Create renderer
        this.renderer = new THREE.WebGLRenderer({
            canvas: this.canvas,
            alpha: true,
            antialias: true
        });
        this.renderer.setSize(this.canvas.clientWidth, this.canvas.clientHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);

        // Create lighting
        this.createLights();

        // Create particle system
        this.createParticles();

        // Create grid
        this.createGrid();

        // Handle window resize
        window.addEventListener('resize', () => this.handleResize());

        // Start animation
        this.animate();

        console.log('3D Scene initialized');
    }

    /**
     * Create scene lighting
     */
    createLights() {
        // Ambient light
        this.addLight('ambient', CONFIG.colors.ambientLight, 0.3);

        // Point lights for atmosphere
        this.addLight('point', CONFIG.colors.neonBlue, 1, [5, 5, 5], 50);
        this.addLight('point', CONFIG.colors.neonPurple, 1, [-5, -5, -5], 50);
    }

    /**
     * Add light to scene (DRY helper)
     * @param {string} type - Light type ('ambient' or 'point')
     * @param {string} color - Light color
     * @param {number} intensity - Light intensity
     * @param {Array} position - Light position [x, y, z] (for point lights)
     * @param {number} distance - Light distance (for point lights)
     * @private
     */
    addLight(type, color, intensity, position = null, distance = null) {
        let light;

        if (type === 'ambient') {
            light = new THREE.AmbientLight(color, intensity);
        } else if (type === 'point') {
            light = new THREE.PointLight(color, intensity, distance);
            if (position) {
                light.position.set(...position);
            }
        }

        if (light) {
            this.scene.add(light);
        }
    }

    /**
     * Create particle system
     */
    createParticles() {
        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(CONFIG.scene.particleCount * 3);
        const colors = new Float32Array(CONFIG.scene.particleCount * 3);

        const spread = CONFIG.scene.particleSpread;
        const color1 = new THREE.Color(CONFIG.colors.neonBlue);
        const color2 = new THREE.Color(CONFIG.colors.neonPurple);

        for (let i = 0; i < CONFIG.scene.particleCount; i++) {
            const i3 = i * 3;

            // Random positions
            positions[i3] = (Math.random() - 0.5) * spread;
            positions[i3 + 1] = (Math.random() - 0.5) * spread;
            positions[i3 + 2] = (Math.random() - 0.5) * spread;

            // Gradient colors
            const mixRatio = Math.random();
            const color = color1.clone().lerp(color2, mixRatio);

            colors[i3] = color.r;
            colors[i3 + 1] = color.g;
            colors[i3 + 2] = color.b;
        }

        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

        const material = new THREE.PointsMaterial({
            size: CONFIG.scene.particleSize,
            vertexColors: true,
            transparent: true,
            opacity: 0.6,
            blending: THREE.AdditiveBlending
        });

        this.particles = new THREE.Points(geometry, material);
        this.scene.add(this.particles);
    }

    /**
     * Create grid helper
     */
    createGrid() {
        const gridHelper = new THREE.GridHelper(
            CONFIG.scene.gridSize,
            CONFIG.scene.gridDivisions,
            CONFIG.colors.gridColor,
            CONFIG.colors.gridColor
        );
        gridHelper.material.opacity = 0.15;
        gridHelper.material.transparent = true;
        gridHelper.position.y = -5;
        this.grid = gridHelper;
        this.scene.add(gridHelper);
    }

    /**
     * Animation loop
     */
    animate() {
        this.animationId = requestAnimationFrame(() => this.animate());
        this.time += 0.01;

        // Rotate particles
        if (this.particles) {
            this.particles.rotation.y += CONFIG.scene.rotationSpeed * 10;
            this.particles.rotation.x += CONFIG.scene.rotationSpeed * 5;

            // Wave effect on particles
            const positions = this.particles.geometry.attributes.position.array;
            for (let i = 0; i < positions.length; i += 3) {
                const x = positions[i];
                const z = positions[i + 2];
                positions[i + 1] += Math.sin(this.time + x * 0.1 + z * 0.1) * 0.01;
            }
            this.particles.geometry.attributes.position.needsUpdate = true;
        }

        // Rotate grid
        if (this.grid) {
            this.grid.rotation.y += CONFIG.scene.rotationSpeed * 5;
        }

        // Render scene
        this.renderer.render(this.scene, this.camera);
    }

    /**
     * Handle window resize
     */
    handleResize() {
        if (!this.camera || !this.renderer || !this.canvas) return;

        const width = this.canvas.clientWidth;
        const height = this.canvas.clientHeight;

        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();

        this.renderer.setSize(width, height);
    }

    /**
     * Trigger pulse effect on calculation
     */
    pulse() {
        if (!this.particles) return;

        // Expand particles briefly
        const originalSize = CONFIG.scene.particleSize;
        const material = this.particles.material;

        material.size = originalSize * 1.5;

        setTimeout(() => {
            material.size = originalSize;
        }, 200);
    }

    /**
     * Change scene color based on operation
     * @param {string} type - Operation type (digit, operator, equals, etc.)
     */
    setMood(type) {
        if (!this.scene) return;

        // Update fog color based on operation
        const colors = {
            digit: CONFIG.colors.neonBlue,
            operator: CONFIG.colors.neonPink,
            equals: CONFIG.colors.neonGreen,
            clear: CONFIG.colors.neonPurple,
            error: CONFIG.colors.neonPink
        };

        const targetColor = colors[type] || CONFIG.colors.neonBlue;
        this.scene.fog.color.set(targetColor);
    }

    /**
     * Dispose of Three.js resources
     */
    dispose() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }

        if (this.renderer) {
            this.renderer.dispose();
        }

        if (this.particles) {
            this.particles.geometry.dispose();
            this.particles.material.dispose();
        }
    }
}
