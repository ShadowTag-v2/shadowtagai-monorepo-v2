/**
 * NEXUSUS AI - Interactive Effects
 * Particle system and dynamic animations
 */

class ParticleSystem {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.particles = [];
    this.particleCount = 80;
    this.mouse = { x: null, y: null, radius: 150 };

    this.resize();
    this.init();
    this.animate();

    window.addEventListener('resize', () => this.resize());
    window.addEventListener('mousemove', (e) => {
      this.mouse.x = e.clientX;
      this.mouse.y = e.clientY;
    });
  }

  resize() {
    this.canvas.width = window.innerWidth;
    this.canvas.height = window.innerHeight;
  }

  init() {
    this.particles = [];
    for (let i = 0; i < this.particleCount; i++) {
      this.particles.push({
        x: Math.random() * this.canvas.width,
        y: Math.random() * this.canvas.height,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5,
        size: Math.random() * 2 + 1,
        opacity: Math.random() * 0.5 + 0.2,
      });
    }
  }

  animate() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    this.particles.forEach((p, i) => {
      // Move particle
      p.x += p.vx;
      p.y += p.vy;

      // Boundary wrap
      if (p.x < 0) p.x = this.canvas.width;
      if (p.x > this.canvas.width) p.x = 0;
      if (p.y < 0) p.y = this.canvas.height;
      if (p.y > this.canvas.height) p.y = 0;

      // Mouse interaction
      if (this.mouse.x && this.mouse.y) {
        const dx = p.x - this.mouse.x;
        const dy = p.y - this.mouse.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < this.mouse.radius) {
          const force = (this.mouse.radius - dist) / this.mouse.radius;
          p.x += dx * force * 0.02;
          p.y += dy * force * 0.02;
        }
      }

      // Draw particle
      this.ctx.beginPath();
      this.ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      this.ctx.fillStyle = `rgba(0, 255, 255, ${p.opacity})`;
      this.ctx.fill();

      // Draw connections
      this.particles.slice(i + 1).forEach((p2) => {
        const dx = p.x - p2.x;
        const dy = p.y - p2.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < 120) {
          this.ctx.beginPath();
          this.ctx.moveTo(p.x, p.y);
          this.ctx.lineTo(p2.x, p2.y);
          this.ctx.strokeStyle = `rgba(0, 255, 255, ${0.1 * (1 - dist / 120)})`;
          this.ctx.stroke();
        }
      });
    });

    requestAnimationFrame(() => this.animate());
  }
}

// Dynamic Stats Rotation
class StatsManager {
  constructor() {
    this.stats = {
      sync: [
        { value: '98.7%', label: 'NEURAL SYNC' },
        { value: '99.2%', label: 'ACCURACY' },
        { value: '97.1%', label: 'STABILITY' },
      ],
      players: [
        { value: '2.4M', label: 'ACTIVE PLAYERS' },
        { value: '847K', label: 'IN COMBAT' },
        { value: '12K', label: 'TOURNAMENTS' },
      ],
      latency: [
        { value: '12ms', label: 'AVG LATENCY' },
        { value: '99.9%', label: 'UPTIME' },
        { value: '156', label: 'EDGE NODES' },
      ],
    };

    this.indices = { sync: 0, players: 0, latency: 0 };
    this.startRotation();
  }

  startRotation() {
    setInterval(() => {
      Object.keys(this.stats).forEach((key) => {
        const circle = document.querySelector(`[data-stat="${key}"]`);
        if (!circle) return;

        // Fade out
        circle.style.opacity = '0';

        setTimeout(() => {
          // Update value
          this.indices[key] = (this.indices[key] + 1) % this.stats[key].length;
          const stat = this.stats[key][this.indices[key]];

          const valueEl = circle.querySelector('.stat-value');
          const labelEl = circle.querySelector('.stat-label');

          if (valueEl) valueEl.textContent = stat.value;
          if (labelEl) labelEl.textContent = stat.label;

          // Fade in
          circle.style.opacity = '1';
        }, 300);
      });
    }, 5000);
  }
}

// Smooth scroll for navigation
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });
}

// Active nav link on scroll
function initScrollSpy() {
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav-links a');

  window.addEventListener('scroll', () => {
    let current = '';

    sections.forEach((section) => {
      const sectionTop = section.offsetTop - 200;
      if (window.scrollY >= sectionTop) {
        current = section.getAttribute('id');
      }
    });

    navLinks.forEach((link) => {
      link.classList.remove('active');
      if (link.getAttribute('href') === `#${current}`) {
        link.classList.add('active');
      }
    });
  });
}

// Entrance animations on scroll
function initScrollAnimations() {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate-in');
        }
      });
    },
    { threshold: 0.1 },
  );

  document.querySelectorAll('.feature-card').forEach((card) => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(30px)';
    card.style.transition = 'all 0.6s ease';
    observer.observe(card);
  });
}

// Add animate-in styles
const style = document.createElement('style');
style.textContent = `
    .animate-in {
        opacity: 1 !important;
        transform: translateY(0) !important;
    }
`;
document.head.appendChild(style);

// Initialize everything
document.addEventListener('DOMContentLoaded', () => {
  const canvas = document.getElementById('particle-canvas');
  if (canvas) {
    new ParticleSystem(canvas);
  }

  new StatsManager();
  initSmoothScroll();
  initScrollSpy();
  initScrollAnimations();

  console.log(
    '%c NEXUSUS AI ',
    'background: #00ffff; color: #000; font-weight: bold; padding: 4px 8px;',
  );
  console.log('%c Neural Combat Evolution - Powered by GamePort ', 'color: #888;');
});
