import Raty from './raty.js';

const heartHints = ['Vulnerable', 'Frail', 'Normal', 'Tough', 'Resilient'];
const skullHints = ['Feeble', 'Weak', 'Normal', 'Savage', 'Brutal'];
const heartLabel = document.querySelector('#hp-raty-label') as HTMLElement;
const damageLabel = document.querySelector('#damage-raty-label') as HTMLElement;

const heartElement = document.querySelector('#hp-raty') as HTMLElement;
const damageElement = document.querySelector('#damage-raty') as HTMLElement;

if (heartElement) {
    const ratyHeart = new Raty(heartElement, {
        number: 5,
        starType: 'i',
        score: 3,
        starOn: 'rating-on',
        starOff: 'rating-off',
        hints: [...heartHints],  // copy so original array is not modified
        click: (score: number) => {
            if (heartLabel) {
                heartLabel.textContent = heartHints[score - 1];
            }
        }
    });
    ratyHeart.init();
}

if (damageElement) {
    const ratyDamage = new Raty(damageElement, {
        number: 5,
        starType: 'i',
        score: 3,
        starOn: 'rating-on',
        starOff: 'rating-off',
        hints: [...skullHints],  // copy so original array is not modified
        click: (score: number) => {
            if (damageLabel) {
                damageLabel.textContent = skullHints[score - 1];
            }
        }
    });
    ratyDamage.init();
}