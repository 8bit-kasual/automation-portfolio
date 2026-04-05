/* ============================================================
   main.js — Portfolio site interactions
   Minimal vanilla JS. No dependencies.
   ============================================================ */

(function () {
  'use strict';

  // ----------------------------------------------------------
  // Mobile nav toggle
  // ----------------------------------------------------------
  const hamburger = document.querySelector('.nav__hamburger');
  const mobileMenu = document.querySelector('.nav__mobile');

  if (hamburger && mobileMenu) {
    hamburger.addEventListener('click', function () {
      const isOpen = mobileMenu.classList.contains('is-open');
      mobileMenu.classList.toggle('is-open', !isOpen);
      hamburger.setAttribute('aria-expanded', String(!isOpen));
      mobileMenu.setAttribute('aria-hidden', String(isOpen));
    });

    // Close menu when a link is clicked
    mobileMenu.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        mobileMenu.classList.remove('is-open');
        hamburger.setAttribute('aria-expanded', 'false');
        mobileMenu.setAttribute('aria-hidden', 'true');
      });
    });
  }

  // ----------------------------------------------------------
  // Card scroll-in animation (IntersectionObserver)
  // ----------------------------------------------------------
  const cards = document.querySelectorAll('.card');

  if ('IntersectionObserver' in window && cards.length) {
    const observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry, i) {
          if (entry.isIntersecting) {
            // Stagger cards slightly
            const delay = (entry.target.dataset.index || 0) * 80;
            setTimeout(function () {
              entry.target.classList.add('is-visible');
            }, delay);
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
    );

    cards.forEach(function (card, i) {
      card.dataset.index = i;
      observer.observe(card);
    });
  } else {
    // Fallback: just show all cards
    cards.forEach(function (card) {
      card.classList.add('is-visible');
    });
  }

  // ----------------------------------------------------------
  // Formspree contact form — async submit
  // ----------------------------------------------------------
  var contactForm = document.querySelector('.contact__form');
  var formSuccess = document.getElementById('form-success');

  if (contactForm && formSuccess) {
    contactForm.addEventListener('submit', function (e) {
      e.preventDefault();

      var submitBtn = contactForm.querySelector('.form__submit');
      submitBtn.textContent = 'Sending\u2026';
      submitBtn.disabled = true;

      fetch(contactForm.action, {
        method: 'POST',
        body: new FormData(contactForm),
        headers: { 'Accept': 'application/json' }
      })
        .then(function (res) {
          if (res.ok) {
            contactForm.reset();
            contactForm.hidden = true;
            formSuccess.hidden = false;
          } else {
            submitBtn.textContent = 'Something went wrong \u2014 try emailing directly.';
            submitBtn.disabled = false;
          }
        })
        .catch(function () {
          submitBtn.textContent = 'Something went wrong \u2014 try emailing directly.';
          submitBtn.disabled = false;
        });
    });
  }

  // ----------------------------------------------------------
  // Nav background on scroll
  // ----------------------------------------------------------
  const nav = document.querySelector('.nav');

  if (nav) {
    window.addEventListener('scroll', function () {
      nav.style.backgroundColor = window.scrollY > 40
        ? 'rgba(10, 18, 64, 0.98)'
        : 'rgba(10, 18, 64, 0.92)';
    }, { passive: true });
  }

})();
