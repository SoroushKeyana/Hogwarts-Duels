document.addEventListener('DOMContentLoaded', () => {
    const searchBox = document.getElementById('searchBox');
    const results = document.getElementById('searchResults');

    if (searchBox && results) {
        searchBox.addEventListener('keyup', () => {
            const query = searchBox.value;
            fetch(`/search/?q=${query}`)
                .then(res => res.json())
                .then(data => {
                    results.innerHTML = '';
                    data.forEach(user => {
                        const li = document.createElement('li');
                        if (user.is_following) {
                            li.innerHTML = `${user.username} <button onclick="unfollow(${user.id}, this)">Unfollow</button>`;
                        } else {
                            li.innerHTML = `${user.username} <button onclick="follow(${user.id}, this)">Follow</button>`;
                        }
                        results.appendChild(li);
                    });
                });
        });
    }

    window.follow = function (userId, button) {
        fetch(`/follow/${userId}/`, {
            method: "POST",
            headers: { "X-CSRFToken": csrfToken },
        }).then(res => {
            if (res.ok) {
                button.textContent = "Unfollow";
                button.setAttribute("onclick", `unfollow(${userId}, this)`);
            }
        });
    };

    window.unfollow = function (userId, button) {
        fetch(`/unfollow/${userId}/`, {
            method: "POST",
            headers: { "X-CSRFToken": csrfToken },
        }).then(res => {
            if (res.ok) {
                button.textContent = "Follow";
                button.setAttribute("onclick", `follow(${userId}, this)`);
            }
        });
    };
});
