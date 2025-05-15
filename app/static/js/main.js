document.addEventListener('DOMContentLoaded', () => {
  const factBlock = document.getElementById('fact-block');
  const newFactBtn = document.getElementById('new-fact-btn');
  const categoryLinks = document.querySelectorAll('.category-link');

  async function fetchFact(category = null) {
    try {
      let url = '/facts/api/fact';
      if (category) {
        url += '?category=' + encodeURIComponent(category);
      }
      const response = await fetch(url);
      if (!response.ok) throw new Error('Failed to fetch fact');
      const fact = await response.json();
      displayFact(fact);
    } catch (err) {
      factBlock.innerHTML = '<p class="fact-text">Ошибка при загрузке факта</p>';
      factBlock.style.opacity = 1;
    }
  }

  function displayFact(fact) {
    factBlock.style.animation = 'none'; // сброс анимации
    factBlock.offsetHeight; // триггер перерисовки

    let saveButtonHtml = '';
    if (fact.id && Number(fact.id) !== 0) {
      saveButtonHtml = `
        <form method="post" action="/facts/save">
          <input type="hidden" name="fact_id" value="${fact.id}">
          <button type="submit">Сохранить</button>
        </form>
      `;
    }

    factBlock.innerHTML = `
      <p class="fact-text"><strong>${fact.category}</strong>: ${fact.text}</p>
      ${saveButtonHtml}
    `;

    factBlock.style.animation = 'fadeInFact 0.8s ease forwards';
  }

  newFactBtn.addEventListener('click', (e) => {
    e.preventDefault();
    fetchFact();
  });

  categoryLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const category = e.target.getAttribute('data-category');
      fetchFact(category);
    });
  });
});
