function createSnowflakes() {
    const snowContainer = document.getElementById('snow-container');
    if (!snowContainer) {
        console.error('Элемент #snow-container не найден.');
        return;
    }
    const numSnowflakes = 100;

    for (let i = 0; i < numSnowflakes; i++) {
      const snowflake = document.createElement('div');
      snowflake.classList.add('snowflake');
      snowflake.style.left = `${Math.random() * 100}%`;

      // Случайный боковой дрейф (от -0.2 до 0.2)
       snowflake.style.setProperty('--random-offset-x', (Math.random() - 0.5) * 0.4);

      // Случайное вращение
      snowflake.style.setProperty('--random-rotate', Math.random());
        // Случайное время анимации (от 5 до 10 секунд)
        snowflake.style.animationDuration = `${Math.random() * 5 + 5}s`;
      snowContainer.appendChild(snowflake);
    }
}


document.addEventListener('DOMContentLoaded', () => {
  createSnowflakes();
});



document.addEventListener('DOMContentLoaded', () => {
    const root = document.documentElement;
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;

    function updateThemeIcon(){
      themeToggle.textContent = body.classList.contains('light-theme') ? '🌙' : '☀️';
    }
    updateThemeIcon()

    themeToggle.addEventListener('click', () => {
           body.classList.toggle('light-theme');
        if(body.classList.contains('light-theme')){
                root.style.setProperty('--text-color-dark', '#111');
                  root.style.setProperty('--card-background-dark', '#fff');
                 body.style.backgroundColor = '#f0f0f0';
        }else{
                root.style.setProperty('--text-color-dark', '#ff8c00');
                root.style.setProperty('--card-background-dark', '#222');
                  body.style.backgroundColor = '#0a0a0a';
        }
          updateThemeIcon()
    });
});

document.addEventListener('DOMContentLoaded', () => {
    fetch('/stats')
        .then(response => response.json())
         .then(data => {
            console.log('Data from /stats:', data);
            const modelCount = document.getElementById('model-count');
            const userCount = document.getElementById('user-count');
            const messageCount = document.getElementById('message-count');

            if (modelCount) {
                modelCount.textContent = data.model_count;
            }
            if (userCount) {
                userCount.textContent = data.user_count;
            }
            if (messageCount) {
                messageCount.textContent = data.approx_message_count;
            }
        })
        .catch(error => {
            console.error('Ошибка получения статистики:', error);
              const modelCount = document.getElementById('model-count');
            const userCount = document.getElementById('user-count');
            const messageCount = document.getElementById('message-count');
             if (modelCount) {
                modelCount.textContent = 'Ошибка';
            }
            if (userCount) {
                 userCount.textContent = 'Ошибка';
            }
            if (messageCount) {
                 messageCount.textContent = 'Ошибка';
            }
        });
});
