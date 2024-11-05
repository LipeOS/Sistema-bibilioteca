document.getElementById('search-btn').addEventListener('click', function() {
    const query = document.getElementById('search-query').value;
    fetch(`/search_books?query=${query}`)
        .then(response => response.json())
        .then(data => {
            const resultsContainer = document.getElementById('search-results');
            resultsContainer.innerHTML = ''; // Limpar resultados anteriores
            data.forEach(book => {
                const bookElement = document.createElement('div');
                bookElement.classList.add('book');
                bookElement.innerHTML = `
                    <h3>${book[1]}</h3>
                    <p>Autor: ${book[2]}</p>
                    <p>Gênero: ${book[3]}</p>
                    <p>Editora: ${book[4]}</p>
                    <p>Ano: ${book[5]}</p>
                    <p>Quantidade: ${book[6]}</p>
                    <form action="/escolher_livro/${book[0]}" method="GET">
                        <button type="submit" class="btn">Retirar Livro</button>
                    </form>
                `;
                resultsContainer.appendChild(bookElement);
            });
        });
});
