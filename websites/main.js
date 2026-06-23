let allItems = [];

// Source - https://stackoverflow.com/a/12646864
// Posted by Laurens Holst, modified by community. See post 'Timeline' for change history
// Retrieved 2026-06-23, License - CC BY-SA 4.0
function shuffleItemsAndRender() {
    for (let i = allItems.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [allItems[i], allItems[j]] = [allItems[j], allItems[i]];
    }
    renderItems();
}

async function loadData() {
    try {
        const response = await fetch('./data.json');
        allItems = await response.json();

        populateCategories();
        shuffleItemsAndRender();
    } catch (error) {
        document.getElementById('itemsContainer').innerHTML =
            '<p>Failed to load ./data.json'+
            '</br>If you are working locally, remember to'+
            '</br>run a server with: python3 -m http.server 8000'+
            '</br>and visit: http://localhost:8000/path-to-.html</p>';
        console.error(error);
    }
}

function populateCategories() {
    const select = document.getElementById('categoryFilter');

    const categories = [
        ...new Set(
            allItems.flatMap(item => item.tags || [])
        )
    ].sort();

    categories.forEach(category => {
        const option = document.createElement('option');
        option.value = category;
        option.textContent = category;
        select.appendChild(option);
    });
}

function renderItems() {
    const selectedCategory =
        document.getElementById('categoryFilter').value;

    const container =
        document.getElementById('itemsContainer');

    const filteredItems = allItems.filter(item => {
        if (!selectedCategory) return true;
        return (item.tags || []).includes(selectedCategory);
    });

    document.getElementById('itemCount').textContent =
        `${filteredItems.length} item(s) found`;

    if (filteredItems.length === 0) {
        container.innerHTML = '<p>No items found.</p>';
        return;
    }

    container.innerHTML = filteredItems.map(item => `
        <div class="websites-item">
            <h4><a href="https://www.${escapeHtml(item.name)}">${escapeHtml(item.name)}</a></h4>
            <p>${escapeHtml(item.description)}</p>

            <div class="websites-tags">
                ${(item.tags || []).map(tag => `
                    <span class="websites-tag">
                        ${escapeHtml(tag)}
                    </span>
                `).join('')}
            </div>
        </div>
    `).join('');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text || '';
    return div.innerHTML;
}

// Interaction with selections and buttons
document
    .getElementById('categoryFilter')
    .addEventListener('change', renderItems);

document
    .getElementById("shuffleButton")
    .onclick = shuffleItemsAndRender;

loadData();
