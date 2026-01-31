async function loadPosts() {
    const response = await fetch('http://localhost:8000/posts');
    const posts = await response.json();
    
    const postsDiv = document.getElementById('posts');
    postsDiv.innerHTML = '';  // Clear current posts
    
    posts.forEach(post => {
        const postElement = document.createElement('div');
        postElement.innerHTML = `<h3>${post.title}</h3><p>${post.content}</p><a href="/posts/${post.id}">View Post</a>`;
        postsDiv.appendChild(postElement);
    });
}
