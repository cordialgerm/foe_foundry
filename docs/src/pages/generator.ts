import '../components/SvgIcon';
import '../components/MonsterRating';
import '../components/MonsterArt';
import '../components/PowerLoadout';
import '../components/MonsterInfo';
import '../components/MonsterCard';
import { initializeMonsterStore } from '../data/api';
import { StatblockChange, StatblockChangeType } from '../data/monster';


window.addEventListener('DOMContentLoaded', () => {
    const statblockHolder = document.getElementById('statblock-holder');
    const monsters = initializeMonsterStore();

    document.querySelectorAll('monster-card').forEach(card => {
        card.addEventListener('monster-changed', async (event: any) => {
            const monsterCard = event.detail.monsterCard;
            if (!monsterCard) return;

            if (statblockHolder) statblockHolder.innerHTML = '';

            // Get selected powers
            const selectedPowers = monsterCard.getSelectedPowers().map((p: any) => p?.key).filter(Boolean);

            const request = {
                monsterKey: monsterCard.monsterKey,
                powers: selectedPowers,
                hpMultiplier: monsterCard.hpMultiplier,
                damageMultiplier: monsterCard.damageMultiplier,
            };

            // Highlight changed powers if present in event.detail.power
            let change: StatblockChange | null = null;
            if (event.detail.power && event.detail.power.key) {
                change = {
                    type: StatblockChangeType.PowerChanged,
                    changedPower: event.detail.power
                };
            }
            else if (event.detail.changeType === 'damage-changed') {
                change = {
                    type: StatblockChangeType.DamageChanged,
                    changedPower: null
                };
            }
            else if (event.detail.changeType === 'hp-changed') {
                change = {
                    type: StatblockChangeType.HpChanged,
                    changedPower: null
                };
            }

            const statblockElement = await monsters.getStatblock(request, change);
            if (statblockHolder && statblockElement) {
                statblockHolder.appendChild(statblockElement);
            }
        });
    });
});