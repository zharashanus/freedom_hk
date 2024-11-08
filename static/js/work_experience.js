let experienceCounter = 0;

function addWorkExperience(data = null) {
    const container = document.getElementById('work-experience-container');
    const template = document.getElementById('work-experience-template');
    const clone = template.content.cloneNode(true);
    
    const expItem = clone.querySelector('.work-experience-item');
    const inputs = expItem.querySelectorAll('input, textarea');
    
    inputs.forEach(input => {
        const fieldName = input.name.split('[')[1].split(']')[0];
        input.name = `work_experience[${experienceCounter}][${fieldName}]`;
        if (data && data[fieldName]) {
            input.value = data[fieldName];
        }
    });
    
    const removeButton = clone.querySelector('.remove-work-experience');
    removeButton.addEventListener('click', function() {
        expItem.remove();
    });
    
    container.appendChild(clone);
    experienceCounter++;
}

// Добавляем функцию для сбора данных формы
function collectWorkExperience() {
    const workExperiences = [];
    const containers = document.querySelectorAll('.work-experience-item');
    
    containers.forEach(container => {
        const exp = {};
        container.querySelectorAll('input, textarea').forEach(input => {
            const fieldName = input.name.match(/\[([^\]]+)\]$/)[1];
            exp[fieldName] = input.value;
        });
        workExperiences.push(exp);
    });
    
    console.log('Collected work experiences:', workExperiences);
    return workExperiences;
}

// Обработчик отправки формы
document.querySelector('form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const workExperiences = collectWorkExperience();
    
    // Создаем или обновляем скрытое поле для опыта работы
    let workExpInput = document.querySelector('input[name="work_experience"]');
    if (!workExpInput) {
        workExpInput = document.createElement('input');
        workExpInput.type = 'hidden';
        workExpInput.name = 'work_experience';
        this.appendChild(workExpInput);
    }
    
    // Преобразуем массив в JSON строку
    workExpInput.value = JSON.stringify(workExperiences);
    
    // Продолжаем отправку формы
    this.submit();
});

// Инициализация существующего опыта работы
window.loadExistingExperience = function(experiences) {
    if (Array.isArray(experiences)) {
        experiences.forEach(exp => addWorkExperience(exp));
    }
};

// Добавление нового опыта работы
document.getElementById('add-work-experience').addEventListener('click', () => {
    addWorkExperience();
}); 