document.addEventListener('DOMContentLoaded', function() {
    // Scrollspy inicializálása manuálisan
    const scrollSpy = new bootstrap.ScrollSpy(document.body, {
        target: '#navbar-docs'
    });

    // Navigációs linkek aktívvá tétele görgetéskor
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Scroll animáció a kiválasztott szekcióhoz
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                window.scrollTo({
                    top: targetSection.offsetTop - 70, // Offset a fixed navbar miatt
                    behavior: 'smooth'
                });
            }
            
            // Kiválasztott link aktívvá tétele
            navLinks.forEach(innerLink => {
                innerLink.classList.remove('active');
            });
            this.classList.add('active');
        });
    });

    // Kódblokkok másolása a vágólapra
    const codeBlocks = document.querySelectorAll('pre code');
    
    codeBlocks.forEach(block => {
        // Másolás gomb létrehozása
        const copyButton = document.createElement('button');
        copyButton.className = 'btn btn-sm btn-outline-primary copy-button';
        copyButton.innerText = 'Másolás';
        copyButton.style.position = 'absolute';
        copyButton.style.top = '5px';
        copyButton.style.right = '5px';
        copyButton.style.opacity = '0';
        copyButton.style.transition = 'opacity 0.3s';
        
        // Gomb hozzáadása a kódblokkhoz
        block.parentNode.style.position = 'relative';
        block.parentNode.appendChild(copyButton);
        
        // Hover eseménykezelés
        block.parentNode.addEventListener('mouseenter', () => {
            copyButton.style.opacity = '1';
        });
        
        block.parentNode.addEventListener('mouseleave', () => {
            copyButton.style.opacity = '0';
        });
        
        // Kattintás esemény
        copyButton.addEventListener('click', () => {
            const code = block.innerText;
            navigator.clipboard.writeText(code).then(() => {
                copyButton.innerText = 'Másolva!';
                copyButton.classList.remove('btn-outline-primary');
                copyButton.classList.add('btn-success');
                
                setTimeout(() => {
                    copyButton.innerText = 'Másolás';
                    copyButton.classList.remove('btn-success');
                    copyButton.classList.add('btn-outline-primary');
                }, 2000);
            }).catch(err => {
                console.error('Nem sikerült másolni:', err);
                copyButton.innerText = 'Hiba!';
                copyButton.classList.remove('btn-outline-primary');
                copyButton.classList.add('btn-danger');
                
                setTimeout(() => {
                    copyButton.innerText = 'Másolás';
                    copyButton.classList.remove('btn-danger');
                    copyButton.classList.add('btn-outline-primary');
                }, 2000);
            });
        });
    });

    // Mobilon a menü összecsukása a linkre kattintáskor
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth < 992) {
                    const bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse);
                    if (bsCollapse) {
                        bsCollapse.hide();
                    }
                }
            });
        });
    }
});