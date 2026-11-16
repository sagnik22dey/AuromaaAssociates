let currentSlide = 0;
let slideInterval = null;
const SLIDE_DURATION = 6000;

function updateSlide(index) {
  const slides = document.querySelectorAll(".hero-slide");
  const dots = document.querySelectorAll(".hero-dot");
  const slideTexts = document.querySelectorAll(".hero-slide-text");

  if (!slides.length) return;

  slides.forEach((slide, i) => {
    slide.classList.toggle("active", i === index);
  });

  dots.forEach((dot, i) => {
    dot.classList.toggle("active", i === index);
  });

  slideTexts.forEach((text, i) => {
    if (i === index) {
      text.classList.remove("hidden");
    } else {
      text.classList.add("hidden");
    }
  });

  currentSlide = index;
}

function nextSlide() {
  const slides = document.querySelectorAll(".hero-slide");
  const total = slides.length || 4;
  const next = (currentSlide + 1) % total;
  updateSlide(next);
}

function startSlider() {
  if (slideInterval) clearInterval(slideInterval);
  slideInterval = setInterval(nextSlide, SLIDE_DURATION);
}

function stopSlider() {
  if (slideInterval) {
    clearInterval(slideInterval);
    slideInterval = null;
  }
}

function initSlider() {
  const heroSection = document.getElementById("hero");
  const dots = document.querySelectorAll(".hero-dot");

  if (!heroSection) return;

  dots.forEach((dot, index) => {
    dot.addEventListener("click", () => {
      updateSlide(index);
      startSlider();
    });
  });

  heroSection.addEventListener("mouseenter", stopSlider);
  heroSection.addEventListener("mouseleave", startSlider);

  let touchStartX = 0;
  let touchEndX = 0;

  heroSection.addEventListener("touchstart", (e) => {
    touchStartX = e.changedTouches[0].screenX;
  }, { passive: true });

  heroSection.addEventListener("touchend", (e) => {
    touchEndX = e.changedTouches[0].screenX;
    const slides = document.querySelectorAll(".hero-slide");
    const total = slides.length || 4;
    if (touchEndX < touchStartX - 50) {
      nextSlide();
      startSlider();
    } else if (touchEndX > touchStartX + 50) {
      const prev = (currentSlide - 1 + total) % total;
      updateSlide(prev);
      startSlider();
    }
  }, { passive: true });

  updateSlide(0);
  startSlider();
}

function setCookie(name, value, days) {
  const d = new Date();
  d.setTime(d.getTime() + (days * 24 * 60 * 60 * 1000));
  const expires = "expires=" + d.toUTCString();
  document.cookie = name + "=" + value + ";" + expires + ";path=/;SameSite=Lax";
}

function getCookie(name) {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? match[2] : null;
}

function hasAgreedDisclaimer() {
  const cookieVal = getCookie("auromaa_disclaimer_agreed");
  const localVal = localStorage.getItem("auromaa_disclaimer_agreed");
  return cookieVal === "true" || localVal === "true";
}

function revealSiteUI() {
  const floating = document.getElementById("floating-elements");
  if (floating) floating.classList.remove("hidden");
}

function initDisclaimer() {
  const overlay = document.getElementById("disclaimer-overlay");
  const agreeBtn = document.getElementById("disclaimer-agree");
  const exitBtn = document.getElementById("disclaimer-exit");
  const isHomePage = window.location.pathname === "/" || window.location.pathname === "";

  if (hasAgreedDisclaimer()) {
    document.documentElement.classList.add("disclaimer-agreed");
    if (getCookie("auromaa_disclaimer_agreed") !== "true") {
      setCookie("auromaa_disclaimer_agreed", "true", 365);
    }
    if (overlay) {
      overlay.classList.add("hidden");
      overlay.style.display = "none";
    }
    revealSiteUI();
  } else if (!isHomePage) {
    if (overlay) {
      overlay.classList.add("hidden");
      overlay.style.display = "none";
    }
    revealSiteUI();
  } else {
    document.documentElement.classList.remove("disclaimer-agreed");
    if (overlay) {
      overlay.classList.remove("hidden");
      overlay.style.display = "flex";
    }
  }

  if (agreeBtn) {
    agreeBtn.addEventListener("click", () => {
      setCookie("auromaa_disclaimer_agreed", "true", 365);
      localStorage.setItem("auromaa_disclaimer_agreed", "true");
      document.documentElement.classList.add("disclaimer-agreed");

      fetch("/api/accept-disclaimer", { method: "POST" }).catch(() => {});

      if (overlay) {
        overlay.classList.add("hidden");
        overlay.style.display = "none";
      }
      revealSiteUI();
    });
  }

  if (exitBtn) {
    exitBtn.addEventListener("click", () => {
      if (window.history.length > 1) {
        window.history.back();
      } else {
        window.close();
      }
    });
  }
}

function initCallbackModal() {
  const modal = document.getElementById("callback-modal");
  const openBtn = document.getElementById("bottom-callback-btn");
  const closeBtn = document.getElementById("callback-close");
  const form = document.getElementById("callback-form");
  const successMsg = document.getElementById("callback-success");
  const errorMsg = document.getElementById("callback-error");

  function openModal() {
    if (modal) {
      modal.classList.remove("hidden");
      modal.classList.add("flex");
    }
  }

  function closeModal() {
    if (modal) {
      modal.classList.add("hidden");
      modal.classList.remove("flex");
    }
  }

  if (openBtn) openBtn.addEventListener("click", openModal);
  if (closeBtn) closeBtn.addEventListener("click", closeModal);

  if (modal) {
    modal.addEventListener("click", (e) => {
      if (e.target === modal) closeModal();
    });
  }

  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const name = document.getElementById("cb-name")?.value;
      const phone = document.getElementById("cb-phone")?.value;
      const area = document.getElementById("cb-area")?.value;
      const consent = document.getElementById("cb-consent")?.checked;

      const formData = new FormData();
      formData.append("name", name);
      formData.append("phone", phone);
      formData.append("area_of_interest", area);
      formData.append("consent", consent ? "true" : "false");

      try {
        const res = await fetch("/api/callback", {
          method: "POST",
          body: formData
        });
        const data = await res.json();
        if (data.success) {
          if (successMsg) successMsg.classList.remove("hidden");
          if (errorMsg) errorMsg.classList.add("hidden");
          form.reset();
          setTimeout(() => {
            closeModal();
            if (successMsg) successMsg.classList.add("hidden");
          }, 2500);
        } else {
          if (errorMsg) {
            errorMsg.textContent = data.message || "An error occurred.";
            errorMsg.classList.remove("hidden");
          }
        }
      } catch (err) {
        if (errorMsg) {
          errorMsg.textContent = "Failed to submit request. Please call us directly.";
          errorMsg.classList.remove("hidden");
        }
      }
    });
  }
}

function initEnquiryForm() {
  const form = document.getElementById("enquiry-form");
  const successMsg = document.getElementById("enquiry-success");
  const errorMsg = document.getElementById("enquiry-error");

  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(form);

    try {
      const res = await fetch("/api/enquiry", {
        method: "POST",
        body: formData
      });
      const data = await res.json();
      if (data.success) {
        if (successMsg) successMsg.classList.remove("hidden");
        if (errorMsg) errorMsg.classList.add("hidden");
        form.reset();
      } else {
        if (errorMsg) {
          errorMsg.textContent = data.message || "An error occurred.";
          errorMsg.classList.remove("hidden");
        }
      }
    } catch (err) {
      if (errorMsg) {
        errorMsg.textContent = "Network error. Please try calling or emailing us.";
        errorMsg.classList.remove("hidden");
      }
    }
  });
}

function initMobileMenu() {
  const btn = document.getElementById("mobile-menu-btn");
  const menu = document.getElementById("mobile-menu");
  if (!btn || !menu) return;

  btn.addEventListener("click", () => {
    menu.classList.toggle("hidden");
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initDisclaimer();
  initSlider();
  initCallbackModal();
  initEnquiryForm();
  initMobileMenu();
});