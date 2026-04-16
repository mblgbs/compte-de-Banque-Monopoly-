const FIRST_NAMES = [
  'Alex',
  'Sam',
  'Lina',
  'Noah',
  'Jade',
  'Milo',
  'Nora',
  'Léo',
  'Maya',
  'Evan',
];

const LAST_NAMES = [
  'Martin',
  'Dupont',
  'Lefevre',
  'Bernard',
  'Garcia',
  'Petit',
  'Roux',
  'Meyer',
  'Nguyen',
  'Durand',
];

const ISSUERS = ['Banque Monopoly', 'Monopoly Crédit', 'Fortune Bank', 'Plateau Finance'];

const cardsContainer = document.getElementById('cards');
const playerCountInput = document.getElementById('playerCount');
const generateBtn = document.getElementById('generateBtn');
const refreshBtn = document.getElementById('refreshBtn');

function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function pick(array) {
  return array[randomInt(0, array.length - 1)];
}

function generateNumber() {
  const prefix = '53';
  let number = prefix;

  while (number.length < 16) {
    number += String(randomInt(0, 9));
  }

  return number.replace(/(\d{4})(?=\d)/g, '$1 ');
}

function generateExpiry() {
  const month = String(randomInt(1, 12)).padStart(2, '0');
  const year = String((new Date().getFullYear() + randomInt(2, 6)) % 100).padStart(2, '0');
  return `${month}/${year}`;
}

function generateCvv() {
  return String(randomInt(0, 999)).padStart(3, '0');
}

function generateHolder() {
  return `${pick(FIRST_NAMES)} ${pick(LAST_NAMES)}`.toUpperCase();
}

function createCard(playerIndex) {
  return {
    player: `Joueur ${playerIndex + 1}`,
    issuer: pick(ISSUERS),
    number: generateNumber(),
    expiry: generateExpiry(),
    cvv: generateCvv(),
    holder: generateHolder(),
  };
}

function renderCards(cards) {
  cardsContainer.innerHTML = cards
    .map(
      (card) => `
      <article class="card">
        <div class="card__top">
          <span class="card__issuer">${card.issuer}</span>
          <span class="card__player">${card.player}</span>
        </div>
        <p class="card__number">${card.number}</p>
        <div class="card__bottom">
          <span class="card__holder">${card.holder}</span>
          <span class="card__meta">
            Exp: ${card.expiry}<br />
            CVV: ${card.cvv}
          </span>
        </div>
      </article>
    `,
    )
    .join('');
}

function generateCards() {
  const playerCount = Number(playerCountInput.value);
  const safeCount = Number.isNaN(playerCount) ? 4 : Math.max(2, Math.min(8, playerCount));
  playerCountInput.value = String(safeCount);

  const cards = Array.from({ length: safeCount }, (_, index) => createCard(index));
  renderCards(cards);
}

generateBtn.addEventListener('click', generateCards);
refreshBtn.addEventListener('click', generateCards);

generateCards();
