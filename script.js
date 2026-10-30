/**
 * Portfolio — interações da página.
 * Sem dependências: cada bloco sai cedo se o elemento não existir.
 */
(() => {
    'use strict';

    const $ = (selector, root = document) => root.querySelector(selector);
    const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const supportsObserver = 'IntersectionObserver' in window;

    /* ----------------------------------------------------------------------
     * Navegação mobile
     * -------------------------------------------------------------------- */
    const navbar = $('.navbar');
    const navToggle = $('.nav-toggle');
    const nav = $('#primary-nav');

    if (navToggle && nav) {
        const setNavState = (isOpen) => {
            nav.classList.toggle('is-open', isOpen);
            navToggle.setAttribute('aria-expanded', String(isOpen));
            navToggle.setAttribute(
                'aria-label',
                isOpen ? 'Fechar menu de navegação' : 'Abrir menu de navegação',
            );
        };

        navToggle.addEventListener('click', () => {
            setNavState(!nav.classList.contains('is-open'));
        });

        // Fecha ao escolher um destino
        nav.addEventListener('click', (event) => {
            if (event.target.closest('a')) {
                setNavState(false);
            }
        });

        // Fecha ao clicar fora do menu
        document.addEventListener('click', (event) => {
            if (!nav.classList.contains('is-open')) return;
            if (nav.contains(event.target) || navToggle.contains(event.target)) return;
            setNavState(false);
        });

        // Fecha com Escape e devolve o foco ao botão
        document.addEventListener('keydown', (event) => {
            if (event.key !== 'Escape' || !nav.classList.contains('is-open')) return;
            setNavState(false);
            navToggle.focus();
        });

        // Ao entrar no layout desktop o painel mobile deixa de existir
        const desktopQuery = window.matchMedia('(min-width: 768px)');
        desktopQuery.addEventListener('change', (event) => {
            if (event.matches) setNavState(false);
        });
    }

    /* ----------------------------------------------------------------------
     * Navbar compacta ao rolar (um único listener, limitado por rAF)
     * -------------------------------------------------------------------- */
    if (navbar) {
        let ticking = false;

        const updateNavbar = () => {
            navbar.classList.toggle('is-scrolled', window.scrollY > 50);
            ticking = false;
        };

        window.addEventListener(
            'scroll',
            () => {
                if (ticking) return;
                ticking = true;
                window.requestAnimationFrame(updateNavbar);
            },
            { passive: true },
        );

        updateNavbar();
    }

    /* ----------------------------------------------------------------------
     * Link ativo conforme a seção visível
     * -------------------------------------------------------------------- */
    const sections = $$('main section[id]');
    const navLinks = $$('.nav-links a');

    if (supportsObserver && sections.length && navLinks.length) {
        const setActiveLink = (id) => {
            navLinks.forEach((link) => {
                const isActive = link.getAttribute('href') === `#${id}`;
                if (isActive) {
                    link.setAttribute('aria-current', 'true');
                } else {
                    link.removeAttribute('aria-current');
                }
            });
        };

        const spy = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) setActiveLink(entry.target.id);
                });
            },
            { rootMargin: '-45% 0px -50% 0px', threshold: 0 },
        );

        sections.forEach((section) => spy.observe(section));
    }

    /* ----------------------------------------------------------------------
     * Revelar elementos ao entrar na viewport
     * -------------------------------------------------------------------- */
    const revealElements = $$('.reveal');

    if (revealElements.length) {
        if (reduceMotion || !supportsObserver) {
            revealElements.forEach((element) => element.classList.add('is-visible'));
        } else {
            const revealObserver = new IntersectionObserver(
                (entries, observer) => {
                    entries.forEach((entry) => {
                        if (!entry.isIntersecting) return;
                        entry.target.classList.add('is-visible');
                        observer.unobserve(entry.target);
                    });
                },
                { rootMargin: '0px 0px -40px 0px', threshold: 0.15 },
            );

            revealElements.forEach((element) => revealObserver.observe(element));
        }
    }

    /* ----------------------------------------------------------------------
     * Barras de skill (a largura vem de --level, definido no HTML)
     * -------------------------------------------------------------------- */
    const skillCards = $$('.skill-card');

    if (skillCards.length) {
        if (reduceMotion || !supportsObserver) {
            skillCards.forEach((card) => card.classList.add('is-filled'));
        } else {
            const skillObserver = new IntersectionObserver(
                (entries, observer) => {
                    entries.forEach((entry) => {
                        if (!entry.isIntersecting) return;
                        entry.target.classList.add('is-filled');
                        observer.unobserve(entry.target);
                    });
                },
                { threshold: 0.4 },
            );

            skillCards.forEach((card) => skillObserver.observe(card));
        }
    }

    /* ----------------------------------------------------------------------
     * Efeito de digitação no subtítulo do hero
     * O texto completo permanece no DOM via .sr-only, então leitores de tela
     * não são afetados pela animação.
     * -------------------------------------------------------------------- */
    const roleText = $('.hero-role-text');

    if (roleText && !reduceMotion) {
        const fullText = roleText.textContent.trim();
        let index = 0;

        roleText.textContent = '';
        roleText.classList.add('is-typing');

        const type = () => {
            index += 1;
            roleText.textContent = fullText.slice(0, index);

            if (index < fullText.length) {
                window.setTimeout(type, 55);
            } else {
                window.setTimeout(() => roleText.classList.remove('is-typing'), 1200);
            }
        };

        window.setTimeout(type, 900);
    }

    /* ----------------------------------------------------------------------
     * Formulário de contato (abre o cliente de e-mail, sem backend)
     * -------------------------------------------------------------------- */
    const form = $('#contact-form');

    if (form) {
        const status = $('.form-status', form);
        const submitButton = $('button[type="submit"]', form);
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        const showStatus = (message, type) => {
            if (!status) return;
            status.textContent = message;
            status.classList.remove('form-status--error', 'form-status--success');
            status.classList.add(`form-status--${type}`);
            status.hidden = false;
        };

        form.addEventListener('submit', (event) => {
            event.preventDefault();

            const data = Object.fromEntries(new FormData(form));
            const fields = ['name', 'email', 'subject', 'message'];
            let firstInvalid = null;

            fields.forEach((field) => {
                const input = form.elements[field];
                if (!input) return;

                const value = String(data[field] ?? '').trim();
                const isInvalid = value === '' || (field === 'email' && !emailPattern.test(value));

                if (isInvalid) {
                    input.setAttribute('aria-invalid', 'true');
                    firstInvalid = firstInvalid ?? input;
                } else {
                    input.removeAttribute('aria-invalid');
                }
            });

            if (firstInvalid) {
                showStatus('Preencha todos os campos com um e-mail válido.', 'error');
                firstInvalid.focus();
                return;
            }

            const subject = encodeURIComponent(String(data.subject).trim());
            const body = encodeURIComponent(
                `${String(data.message).trim()}\n\n— ${String(data.name).trim()} (${String(data.email).trim()})`,
            );

            window.location.href = `mailto:dionarley@gmail.com?subject=${subject}&body=${body}`;

            showStatus('Abrindo seu aplicativo de e-mail para concluir o envio…', 'success');
            form.reset();

            if (submitButton) submitButton.blur();
        });

        // Limpa o estado de erro assim que o usuário corrige o campo
        form.addEventListener('input', (event) => {
            if (event.target.matches('input, textarea')) {
                event.target.removeAttribute('aria-invalid');
            }
        });
    }

    /* ----------------------------------------------------------------------
     * Ano corrente no rodapé
     * -------------------------------------------------------------------- */
    const yearElement = $('#year');

    if (yearElement) {
        yearElement.textContent = String(new Date().getFullYear());
    }
})();
