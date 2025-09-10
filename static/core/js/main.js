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
                        li.className = 'list-group-item d-flex justify-content-between align-items-center';
                        const userLink = document.createElement('a');
                        userLink.href = `/profile/${user.username}/`;
                        userLink.textContent = user.username;
                        li.appendChild(userLink);

                        const buttonDiv = document.createElement('div');
                        if (user.is_following) {
                            const unfollowButton = document.createElement('button');
                            unfollowButton.className = 'btn btn-sm btn-danger';
                            unfollowButton.textContent = 'Unfollow';
                            unfollowButton.onclick = () => unfollow(user.id, unfollowButton);
                            buttonDiv.appendChild(unfollowButton);
                        } else {
                            const followButton = document.createElement('button');
                            followButton.className = 'btn btn-sm btn-primary';
                            followButton.textContent = 'Follow';
                            followButton.onclick = () => follow(user.id, followButton);
                            buttonDiv.appendChild(followButton);
                        }

                        const challengeButton = document.createElement('a');
                        challengeButton.className = 'btn btn-sm btn-warning ms-2'; // Added ms-2 for margin-left
                        challengeButton.textContent = 'Challenge';
                        challengeButton.href = `/duel/start/${user.id}/`;
                        buttonDiv.appendChild(challengeButton);

                        li.appendChild(buttonDiv);
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
