document.addEventListener('DOMContentLoaded', () => {
    // Add page load animation
    document.body.style.opacity = '0';
    document.body.style.transition = 'opacity 0.6s ease-in';
    
    setTimeout(() => {
        document.body.style.opacity = '1';
    }, 100);
    
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const messageDiv = document.getElementById('message');

    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.dataset.tab;
            const targetTab = document.getElementById(tabName);
            
            // Don't switch if already active
            if (btn.classList.contains('active')) return;
            
            // Add smooth transition effect
            btn.style.transform = 'scale(0.95)';
            setTimeout(() => {
                btn.style.transform = 'scale(1)';
            }, 150);
            
            // Hide current active tab with animation
            const currentActiveTab = document.querySelector('.tab-content.active');
            if (currentActiveTab) {
                currentActiveTab.style.opacity = '0';
                currentActiveTab.style.transform = 'translateY(-20px)';
                
                setTimeout(() => {
                    tabButtons.forEach(b => b.classList.remove('active'));
                    tabContents.forEach(c => c.classList.remove('active'));
                    
                    btn.classList.add('active');
                    targetTab.classList.add('active');
                    
                    // Show new tab with animation
                    setTimeout(() => {
                        targetTab.style.opacity = '1';
                        targetTab.style.transform = 'translateY(0)';
                    }, 50);
                }, 150);
            }
            
            messageDiv.classList.remove('show');
        });
    });

    function showMessage(text, isError = false) {
        // Hide any existing message first
        messageDiv.classList.remove('show');
        
        setTimeout(() => {
            messageDiv.textContent = text;
            messageDiv.className = 'message ' + (isError ? 'error' : 'success');
            
            // Trigger animation
            setTimeout(() => {
                messageDiv.classList.add('show');
            }, 10);
        }, 300);
    }

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const submitBtn = e.target.querySelector('.btn-primary');
        const username = document.getElementById('loginUsername').value;
        const password = document.getElementById('loginPassword').value;

        // Add loading animation to button
        submitBtn.style.transform = 'scale(0.95)';
        submitBtn.textContent = 'Signing In...';
        submitBtn.disabled = true;

        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();
            
            if (data.success) {
                // Success animation
                submitBtn.style.background = '#28a745';
                submitBtn.textContent = 'Success!';
                
                // Add smooth page transition
                document.body.style.transition = 'opacity 0.5s ease-out';
                document.body.style.opacity = '0';
                
                setTimeout(() => {
                    window.location.href = '/feed';
                }, 500);
            } else {
                // Reset button and show error
                submitBtn.style.transform = 'scale(1)';
                submitBtn.textContent = 'Sign In →';
                submitBtn.disabled = false;
                showMessage(data.message || 'Login failed', true);
            }
        } catch (error) {
            // Reset button and show error
            submitBtn.style.transform = 'scale(1)';
            submitBtn.textContent = 'Sign In →';
            submitBtn.disabled = false;
            showMessage('Network error. Please try again.', true);
        }
    });

    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const submitBtn = e.target.querySelector('.btn-primary');
        const fullName = document.getElementById('regFullName').value;
        const username = document.getElementById('regUsername').value;
        const email = document.getElementById('regEmail').value;
        const password = document.getElementById('regPassword').value;

        // Add loading animation to button
        submitBtn.style.transform = 'scale(0.95)';
        submitBtn.textContent = 'Creating Account...';
        submitBtn.disabled = true;

        try {
            const response = await fetch('/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ fullName, username, email, password })
            });

            const data = await response.json();
            
            if (data.success) {
                // Success animation
                submitBtn.style.background = '#28a745';
                submitBtn.textContent = 'Success!';
                
                // Add smooth page transition
                document.body.style.transition = 'opacity 0.5s ease-out';
                document.body.style.opacity = '0';
                
                setTimeout(() => {
                    window.location.href = '/feed';
                }, 500);
            } else {
                // Reset button and show error
                submitBtn.style.transform = 'scale(1)';
                submitBtn.textContent = 'Sign Up →';
                submitBtn.disabled = false;
                showMessage(data.message || 'Registration failed', true);
            }
        } catch (error) {
            // Reset button and show error
            submitBtn.style.transform = 'scale(1)';
            submitBtn.textContent = 'Sign Up →';
            submitBtn.disabled = false;
            showMessage('Network error. Please try again.', true);
        }
    });
});
