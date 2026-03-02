document.addEventListener("DOMContentLoaded", () => {
    // --- SIDEBAR TOGGLE LOGIC ---
    const toggleBtn = document.getElementById("toggle-sidebar");
    const sidebar = document.getElementById("sidebar");
    const mainWrapper = document.getElementById("main-wrapper");

    if (toggleBtn && sidebar && mainWrapper) {
        toggleBtn.addEventListener("click", () => {
            // Desktop behavior: Sync collapse of sidebar with expansion of main wrapper
            if (window.innerWidth > 768) {
                sidebar.classList.toggle("collapsed");
                mainWrapper.classList.toggle("full-width");
            } else {
                // Mobile behavior: Toggle overlay visibility
                sidebar.classList.toggle("active");
            }
        });
    }

    // Auto-close sidebar when clicking a link on mobile to clear the screen
    const navItems = document.querySelectorAll(".nav-item");
    navItems.forEach(item => {
        item.addEventListener("click", () => {
            if (window.innerWidth <= 768 && sidebar) {
                sidebar.classList.remove("active");
            }
        });
    });

    // --- HEART RATE WIDGET LOGIC ---
    const sidebarBpm = document.getElementById('sidebar-bpm');
    const sidebarStatus = document.getElementById('sidebar-status');
    const sidebarPulse = document.getElementById('sidebar-pulse');
    const espIp = "http://192.168.1.100";

    function updateWidget() {
        // Only run if the elements exist on the current page
        if (!sidebarBpm || !sidebarStatus || !sidebarPulse) return;

        fetch(`${espIp}/data`)
            .then(res => res.json())
            .then(data => {
                if (data.status === "Reading...") {
                    sidebarBpm.innerText = data.bpm;
                    sidebarStatus.innerText = "Live";
                    sidebarPulse.classList.add('animating-pulse');
                    sidebarPulse.style.background = "var(--success-green)";
                } else {
                    sidebarBpm.innerText = "--";
                    sidebarStatus.innerText = data.status;
                    sidebarPulse.classList.remove('animating-pulse');
                    sidebarPulse.style.background = "var(--text-muted)";
                }
            })
            .catch(() => {
                // Handle device disconnect or network failure
                sidebarBpm.innerText = "OFF";
                sidebarStatus.innerText = "Offline";
                sidebarPulse.classList.remove('animating-pulse');
                sidebarPulse.style.background = "var(--error-red)";
            });
    }

    // Poll the ESP32 every 2 seconds for the global widget
    setInterval(updateWidget, 2000); 
});