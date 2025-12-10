// Intersection Observer for scroll reveal animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
        }
    });
}, observerOptions);

// Observe all scroll reveal elements
document.addEventListener('DOMContentLoaded', () => {
    // Smooth scroll for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Enhanced button interactions
    const buttons = document.querySelectorAll('.btn-primary, .btn-secondary, .feature-cta');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', () => {
            button.style.transform = 'translateY(-2px) scale(1.02)';
        });
        
        button.addEventListener('mouseleave', () => {
            button.style.transform = 'translateY(0) scale(1)';
        });
        
        button.addEventListener('mousedown', () => {
            button.style.transform = 'translateY(0) scale(0.98)';
        });
        
        button.addEventListener('mouseup', () => {
            button.style.transform = 'translateY(-2px) scale(1.02)';
        });
    });

    // Enhanced feature card interactions
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-8px) scale(1.02)';
            card.style.boxShadow = '0 20px 50px rgba(0, 180, 216, 0.2)';
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0) scale(1)';
            card.style.boxShadow = 'none';
        });
    });

    // Enhanced pricing card interactions
    const pricingCards = document.querySelectorAll('.pricing-card');
    pricingCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            if (!card.classList.contains('featured')) {
                card.style.transform = 'translateY(-5px) scale(1.02)';
                card.style.boxShadow = '0 15px 40px rgba(0, 180, 216, 0.15)';
            }
        });
        
        card.addEventListener('mouseleave', () => {
            if (!card.classList.contains('featured')) {
                card.style.transform = 'translateY(0) scale(1)';
                card.style.boxShadow = 'none';
            }
        });
    });
    
    // Count up animation for metrics
    const metricNumbers = document.querySelectorAll('.metric-number[data-count]');
    const countUpObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.classList.contains('counted')) {
                const target = parseFloat(entry.target.getAttribute('data-count'));
                const duration = 1200; // ms
                const increment = target / (duration / 16); // 60fps
                let current = 0;
                
                const timer = setInterval(() => {
                    current += increment;
                    if (current >= target) {
                        entry.target.textContent = entry.target.getAttribute('data-count');
                        clearInterval(timer);
                        entry.target.classList.add('counted');
                    } else {
                        if (target >= 100) {
                            entry.target.textContent = Math.floor(current).toLocaleString();
                        } else {
                            entry.target.textContent = current.toFixed(1);
                        }
                    }
                }, 16);
            }
        });
    }, { threshold: 0.5 });
    
    metricNumbers.forEach(number => {
        countUpObserver.observe(number);
    });
    
    // Enhanced testimonial carousel with smooth transitions
    const testimonialCards = document.querySelectorAll('.testimonial-card');
    let currentTestimonial = 0;
    
    const showTestimonial = (index) => {
        testimonialCards.forEach((card, i) => {
            if (i === index) {
                card.style.display = 'block';
                card.style.opacity = '0';
                card.style.transform = 'translateX(30px)';
                
                // Trigger animation after display change
                setTimeout(() => {
                    card.style.opacity = '1';
                    card.style.transform = 'translateX(0)';
                }, 10);
            } else {
                card.style.display = 'none';
                card.style.opacity = '0';
                card.style.transform = 'translateX(-30px)';
            }
        });
    };
    
    const nextTestimonial = () => {
        currentTestimonial = (currentTestimonial + 1) % testimonialCards.length;
        showTestimonial(currentTestimonial);
    };
    
    // Auto-advance testimonials every 6 seconds
    setInterval(nextTestimonial, 6000);
    
    // Add click handlers for manual navigation (optional)
    testimonialCards.forEach((card, index) => {
        card.addEventListener('click', () => {
            currentTestimonial = index;
            showTestimonial(currentTestimonial);
        });
    });
    
    // Reset animation on page load for reduced motion
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        document.querySelectorAll('.loop-item').forEach(item => {
            item.style.animation = 'none';
        });
        
        // Disable all animations for reduced motion
        document.querySelectorAll('*').forEach(element => {
            element.style.animationDuration = '0.01ms';
            element.style.transitionDuration = '0.01ms';
        });
    }
    
    // Smooth page transitions for navigation
    const navigationLinks = document.querySelectorAll('a[href="/landing"], a[href="/feed"]');
    navigationLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Add fade-out animation
            document.body.style.transition = 'opacity 0.5s ease-out';
            document.body.style.opacity = '0';
            
            // Navigate after animation completes
            setTimeout(() => {
                window.location.href = link.getAttribute('href');
            }, 500);
        });
    });
    
    // Add page load animation
    window.addEventListener('load', () => {
        document.body.style.opacity = '0';
        document.body.style.transition = 'opacity 0.6s ease-in';
        
        setTimeout(() => {
            document.body.style.opacity = '1';
        }, 100);
    });
    
    // Add scroll-based animations for better performance
    let ticking = false;
    const updateScrollAnimations = () => {
        const scrolled = window.pageYOffset;
        const parallax = scrolled * 0.5;
        
        // Parallax effect for hero watermark
        const watermark = document.querySelector('.hero-watermark');
        if (watermark) {
            watermark.style.transform = `translate(-50%, -50%) translateY(${parallax * 0.1}px)`;
        }
        
        ticking = false;
    };
    
    const requestScrollUpdate = () => {
        if (!ticking) {
            requestAnimationFrame(updateScrollAnimations);
            ticking = true;
        }
    };
    
    window.addEventListener('scroll', requestScrollUpdate);
});
