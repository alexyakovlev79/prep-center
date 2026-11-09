(() => {
  const calculator = document.getElementById('calc');
  const form = calculator.querySelector('form');
  const steps = [...form.querySelectorAll('[data-step]')];
  const field = (id) => form.querySelector(`#${id}`);
  const value = (id) => field(id).value.trim();
  const selected = (name) => [...form.querySelectorAll(`[name="${name}"]:checked`)]
    .map((input) => input.value);
  const format = new Intl.NumberFormat('ru-RU');
  let currentStep = 0;

  const rates = {
    defect: 5,
    bag: 5,
    barcode: 5,
    kiz: 7,
    kit: 5,
    bubble: 10,
    shrink: 5,
  };

  function showStep(index) {
    steps[currentStep].hidden = true;
    currentStep = index;
    steps[currentStep].hidden = false;
    steps[currentStep].querySelector('[data-step-title]').focus();
  }

  function showError(id, invalid) {
    const error = field(id);
    error.hidden = !invalid;
    if (invalid) error.focus();
    return !invalid;
  }

  const sizeFields = ['calc-length', 'calc-width', 'calc-height'].map(field);

  function validateStep() {
    if (currentStep === 0) {
      return showError('calc-category-error', !selected('category').length && !value('calc-category-other'));
    }
    if (currentStep === 1) {
      return showError('calc-operation-error', !selected('operation').length && !value('calc-operation-other'));
    }
    if (currentStep === 2) {
      const count = Number(value('calc-count'));
      const sizes = sizeFields.map((input) => input.value);
      if (!showError('calc-count-error', !Number.isSafeInteger(count) || count < 100)) return false;
      const incomplete = sizes.some(Boolean) && !sizes.every((size) => Number(size) > 0);
      return showError('calc-size-error', incomplete || sizeFields.some((input) => input.validity.badInput));
    }
    return true;
  }

  function summarizeOptions(name, other, replaceSelection = false) {
    const entered = value(other);
    return [...(entered && replaceSelection ? [] : selected(name)), entered].filter(Boolean).join(', ');
  }

  function showResult() {
    const count = Number(value('calc-count'));
    const sizes = sizeFields.map((input) => input.value);
    const [length, width, height] = sizes.map(Number);
    const liters = Math.max(length * width * height / 1000, 1);
    const operations = selected('operation');
    // Preserve the flat rates, minimum volume and rounding from the 26 October snapshot.
    const total = operations.reduce((price, operation) => {
      const multiplier = operation === 'bubble' || operation === 'shrink' ? liters : 1;
      return price + rates[operation] * multiplier * count;
    }, 10 * count);
    const manual = Boolean(value('calc-operation-other')) || !Number.isFinite(total);

    field('calc-prices').hidden = manual;
    field('calc-manual').hidden = !manual;
    field('calc-total').textContent = manual ? '' : format.format(Math.ceil(total));
    field('calc-unit').textContent = manual ? '' : format.format(Math.ceil(total / count));

    const operationNames = [...form.querySelectorAll('[name="operation"]:checked')]
      .map((input) => input.closest('label').querySelector('.calculator-card-name').textContent);
    const lines = [
      'Здравствуйте! Хочу уточнить расчёт на сайте Преп-Центра.',
      `Категории: ${summarizeOptions('category', 'calc-category-other')}`,
      `Операции: ${[...operationNames, value('calc-operation-other')].filter(Boolean).join(', ')}`,
      `Количество: ${format.format(count)} ед.`,
      sizes.every(Boolean) ? `Габариты: ${sizes.join(' × ')} см` : '',
      `Доставка на склад: ${summarizeOptions('delivery', 'calc-delivery-other', true)}`,
      summarizeOptions('market', 'calc-market-other') ? `Куда отгружаем: ${summarizeOptions('market', 'calc-market-other')}` : '',
      `Когда отгружаем: ${summarizeOptions('when', 'calc-when-other', true)}`,
      manual ? 'Нужен индивидуальный расчёт.' :
        `Предварительный расчёт: ${field('calc-total').textContent} ₽ за партию, ${field('calc-unit').textContent} ₽ за единицу.`,
    ];
    const chat = new URL('https://t.me/prepmanager2');
    chat.searchParams.set('text', lines.filter(Boolean).join('\n'));
    field('calc-telegram').href = chat.href;
  }

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    if (currentStep >= steps.length - 1 || !validateStep()) return;
    if (currentStep === steps.length - 2) showResult();
    showStep(currentStep + 1);
  });

  for (const back of form.querySelectorAll('[data-back]')) {
    back.addEventListener('click', () => showStep(currentStep - 1));
  }
  form.hidden = false;
})();
