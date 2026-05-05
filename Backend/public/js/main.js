// ========================================
// DualCrop Smart Advisory System
// Main JavaScript File
// ========================================

// DOM Ready
document.addEventListener("DOMContentLoaded", function () {
    // Initialize tooltips
    initializeTooltips();

    // Initialize popovers
    initializePopovers();

    // Set active navbar link
    setActiveNavLink();
});

// ========== TOOLTIP INITIALIZATION ==========
function initializeTooltips() {
    // Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(
        document.querySelectorAll('[data-bs-toggle="tooltip"]')
    );
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// ========== POPOVER INITIALIZATION ==========
function initializePopovers() {
    // Bootstrap popovers
    const popoverTriggerList = [].slice.call(
        document.querySelectorAll('[data-bs-toggle="popover"]')
    );
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// ========== ACTIVE NAVBAR LINK ==========
function setActiveNavLink() {
    const currentLocation = location.pathname;
    const menuItems = document.querySelectorAll(".nav-link");

    menuItems.forEach((item) => {
        if (item.getAttribute("href") === currentLocation) {
            item.classList.add("active");
        } else {
            item.classList.remove("active");
        }
    });
}

// ========== UTILITY FUNCTIONS ==========

// Format date
function formatDate(date) {
    return new Date(date).toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
    });
}

// Format time
function formatTime(date) {
    return new Date(date).toLocaleTimeString("en-US", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
    });
}

// Show toast notification
function showToast(message, type = "info", duration = 5000) {
    const toastHTML = `
        <div class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header bg-${type} text-white">
                <strong class="me-auto">Notification</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;

    const toastContainer = document.createElement("div");
    toastContainer.classList.add("toast-container", "position-fixed", "bottom-0", "end-0", "p-3");
    toastContainer.innerHTML = toastHTML;

    document.body.appendChild(toastContainer);

    const toast = new bootstrap.Toast(toastContainer.querySelector(".toast"));
    toast.show();

    setTimeout(() => {
        toastContainer.remove();
    }, duration + 500);
}

// Validate email
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Show loading spinner
function showLoadingSpinner(selector, show = true) {
    const spinner = document.querySelector(selector);
    if (spinner) {
        spinner.style.display = show ? "block" : "none";
    }
}

// API call helper
async function apiCall(url, method = "GET", data = null) {
    const options = {
        method: method,
        headers: {
            "Content-Type": "application/json",
        },
    };

    if (data && (method === "POST" || method === "PUT" || method === "PATCH")) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(url, options);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error("API Error:", error);
        showToast("An error occurred. Please try again.", "danger");
        throw error;
    }
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Throttle function
function throttle(func, limit) {
    let inThrottle;
    return function (...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => (inThrottle = false), limit);
        }
    };
}

// Local storage helper
const Storage = {
    set: (key, value) => {
        localStorage.setItem(key, JSON.stringify(value));
    },
    get: (key) => {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : null;
    },
    remove: (key) => {
        localStorage.removeItem(key);
    },
    clear: () => {
        localStorage.clear();
    },
};

// Session storage helper
const SessionStorage = {
    set: (key, value) => {
        sessionStorage.setItem(key, JSON.stringify(value));
    },
    get: (key) => {
        const item = sessionStorage.getItem(key);
        return item ? JSON.parse(item) : null;
    },
    remove: (key) => {
        sessionStorage.removeItem(key);
    },
    clear: () => {
        sessionStorage.clear();
    },
};

// ========== CONSOLE MESSAGE ==========
console.log(
    "%c 🌾 DualCrop Smart Advisory System",
    "font-size: 20px; font-weight: bold; color: #28a745;"
);
console.log("Welcome to the DualCrop Advisory Platform!");
console.log("Version: 1.0.0");
console.log("© 2024 DualCrop Team");
