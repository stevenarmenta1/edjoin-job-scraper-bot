// static/js/script.js
document.addEventListener('DOMContentLoaded', function () {
    console.log('Edjoin Hunter loaded!');

    // ========== DARK MODE INSIDE DROPDOWN ==========
    const dropdownMenu = document.getElementById('userDropdown');
    if (dropdownMenu) {
        // Create the dark mode menu item
        const darkModeItem = document.createElement('a');
        darkModeItem.href = '#';
        darkModeItem.className = 'dropdown-item';
        darkModeItem.innerHTML = `
            <i class="fas fa-moon"></i>
            <span>Dark Mode</span>
            <i class="fas fa-check float-end mt-1" style="opacity:0; color:#28a745;"></i>
        `;

        // Insert it right after "Refresh Data"
        const refreshItem = dropdownMenu.querySelector('a[href="/"] + a[href="/"]'); // Second <a href="/"> is Refresh
        if (refreshItem && refreshItem.nextElementSibling?.classList.contains('dropdown-divider')) {
            refreshItem.parentNode.insertBefore(darkModeItem, refreshItem.nextElementSibling);
        } else {
            dropdownMenu.appendChild(darkModeItem);
        }

        // Theme functions
        const checkIcon = darkModeItem.querySelector('.fa-check');

        function applyTheme(theme) {
            if (theme === 'dark') {
                document.body.classList.add('dark-mode');
                darkModeItem.innerHTML = `
                    <i class="fas fa-sun"></i>
                    <span>Light Mode</span>
                    <i class="fas fa-check float-end mt-1" style="opacity:1; color:#28a745;"></i>
                `;
            } else {
                document.body.classList.remove('dark-mode');
                darkModeItem.innerHTML = `
                    <i class="fas fa-moon"></i>
                    <span>Dark Mode</span>
                    <i class="fas fa-check float-end mt-1" style="opacity:0;"></i>
                `;
            }
        }

        // Load saved preference
        const saved = localStorage.getItem('edjoin-dark-mode');
        if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
            applyTheme('dark');
        }

        // Toggle on click
        darkModeItem.addEventListener('click', function (e) {
            e.preventDefault();
            const isDark = document.body.classList.contains('dark-mode');
            const newTheme = isDark ? 'light' : 'dark';
            applyTheme(newTheme);
            localStorage.setItem('edjoin-dark-mode', newTheme);
        });
    }

    // ========== YOUR EXISTING CODE (unchanged) ==========
    let currentSort = 'default';
    let jobsArray = [];

    function toggleDropdown() {
        document.getElementById('userDropdown')?.classList.toggle('show');
    }

    document.addEventListener('click', function (e) {
        const dropdown = document.getElementById('userDropdown');
        const avatar = document.getElementById('userAvatarBtn');
        if (dropdown && avatar && !dropdown.contains(e.target) && !avatar.contains(e.target)) {
            dropdown.classList.remove('show');
        }
    });

    function initializeJobs() {
        jobsArray = Array.from(document.querySelectorAll('.search-item')).map(card => ({
            element: card,
            location: card.dataset.location,
            title: card.dataset.title,
            salary: card.dataset.salary,
            deadline: card.dataset.deadline,
            district: card.dataset.district
        }));
    }

    function extractSalaryNumber(salaryStr) {
        const match = salaryStr.match(/\d+,?\d*/);
        return match ? parseInt(match[0].replace(',', '')) : 0;
    }

    function sortJobs(sortType) {
        let sorted = [...jobsArray];
        switch (sortType) {
            case 'location': sorted.sort((a, b) => a.location.localeCompare(b.location)); break;
            case 'title': sorted.sort((a, b) => a.title.localeCompare(b.title)); break;
            case 'salary': sorted.sort((a, b) => extractSalaryNumber(b.salary) - extractSalaryNumber(a.salary)); break;
            case 'deadline':
                sorted.sort((a, b) => {
                    const dateA = new Date(a.deadline) || new Date(9999, 0, 0);
                    const dateB = new Date(b.deadline) || new Date(9999, 0, 0);
                    return dateA - dateB;
                });
                break;
        }
        return sorted;
    }

    window.sortAndFilter = function (sortType) {
        currentSort = sortType;
        const sorted = sortJobs(sortType);
        const filter = document.getElementById('jobSearch').value.toLowerCase();
        const jobList = document.getElementById('jobList');

        jobList.innerHTML = '';
        let hasResults = false;

        sorted.forEach(job => {
            const text = job.element.querySelector('.search-data').innerText.toLowerCase();
            const show = text.includes(filter);
            job.element.style.display = show ? '' : 'none';
            jobList.appendChild(job.element);
            if (show) hasResults = true;
        });

        document.getElementById('noResults').style.display = hasResults ? 'none' : 'block';
        document.querySelectorAll('.sort-btn').forEach(b => b.classList.toggle('active', b.dataset.sort === sortType));
    };

    document.getElementById('jobSearch')?.addEventListener('keyup', () => sortAndFilter(currentSort));

    document.querySelectorAll('.salary-val').forEach(el => {
        const text = el.innerText;
        if ((text.includes('$1') && text.length > 8) ||
            ((text.includes('$8') || text.includes('$9')) && text.includes('Month'))) {
            el.classList.add('high-pay');
        }
    });

    window.addEventListener('load', initializeJobs);

    // Expose toggleDropdown globally for onclick
    window.toggleDropdown = toggleDropdown;
});