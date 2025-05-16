document.addEventListener('DOMContentLoaded', () => {
  const factBlock = document.getElementById('fact-block');
  const saveBtnContainer = document.getElementById('save-button-container');
  const newFactBtn = document.getElementById('new-fact-btn');
  const categoryLinks = document.querySelectorAll('.category-link');

  // Показываем факт с анимацией и кнопкой "Сохранить"
  function displayFact(fact) {
    factBlock.style.opacity = 0;
    factBlock.style.animation = 'none';
    void factBlock.offsetWidth; // перезапуск анимации

    factBlock.innerHTML = `<p><strong>${fact.category}</strong>: ${fact.text}</p>`;
    factBlock.style.animation = 'fadeInFact 0.8s ease forwards';

    if (fact.id && fact.id !== 0) {
      saveBtnContainer.innerHTML = `
        <form id="save-fact-form" method="post" action="/facts/save">
          <input type="hidden" name="fact_id" value="${fact.id}">
          <button type="submit" class="button save-button">Сохранить</button>
        </form>
      `;
      // Обратите внимание: здесь больше нет привязки обработчика saveFact
    } else {
      saveBtnContainer.innerHTML = '';
    }
  }

  // Получение факта с сервера (по категории или случайный)
  async function fetchFact(category = null) {
    try {
      let url = '/facts/api/fact';
      if (category) {
        url += '?category=' + encodeURIComponent(category);
      }
      const response = await fetch(url);
      if (!response.ok) throw new Error('Не удалось загрузить факт');
      const fact = await response.json();
      displayFact(fact);
    } catch (err) {
      factBlock.innerHTML = '<p class="fact-text">Ошибка при загрузке факта</p>';
      factBlock.style.opacity = 1;
      saveBtnContainer.innerHTML = '';
    }
  }

  // Обработка клика "Новый факт"
  newFactBtn.addEventListener('click', (e) => {
    e.preventDefault();
    fetchFact();
    history.pushState(null, '', '/facts/');
  });

  // Обработка кликов по категориям
  categoryLinks.forEach(link => {
    link.addEventListener('click', (event) => {
      event.preventDefault();
      const category = event.target.getAttribute('data-category');
      fetchFact(category);
      history.pushState(null, '', event.target.href);
    });
  });
});
