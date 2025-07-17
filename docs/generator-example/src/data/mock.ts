import { PowerStore, PowerLoadout, Power } from './powers';
import { Monster, MonsterStore } from './monster';

// Mock data based on generator_old.html
const mockPowers: Record<string, Power[]> = {
    'skeletal-boon': [
        {
            key: 'skeletal-reconstruction',
            name: 'Skeletal Reconstruction',
            power_category: 'healing',
            icon: 'data:image/svg+xml;base64,' + btoa(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
        <path fill="currentColor" d="m244 439.765-22.63 3 8.5-148.15a68.48 68.48 0 0 0 22.33 6.7l-7.94 138.45zm28.5 7 4.37 1.32 18.3.65v-153.58a70.07 70.07 0 0 1-22.68 6.29v145.35zm-255.26 45.6h473.52l-56.07-32.23-37.84-9.11-46.68-19.3-36.71 34.72-39.41-1.4-27.86-8.41-41.34 5.41-25-15.92-10.78-18.22L85 447.515l-55.34 20.32zm148.05-334.53c-3.757-4.877-10.72-5.866-15.686-2.227-4.966 3.638-6.122 10.575-2.604 15.627l12 16.45 16.21-16.32zm35.71 48.72-15.6-21.29-16.17 16.3 15.19 20.8 15.37-14.81a8.55 8.55 0 0 1 1.21-1zm25.67 35L211 220.285l-16.44 15.88 16.67 22.76c2.46-6.81 7.9-12.78 15.42-17.32zm-24.9-146.42c-2.193-5.775-8.606-8.733-14.422-6.651-5.817 2.081-8.897 8.436-6.928 14.291l14.23 39.78 20.64-9.62zm16.83 114.35 10.91 30.48a67.76 67.76 0 0 1 21.67-6.74l-11.43-31.86zm2.4-60.42-20.64 9.62 12.46 34.83 21.18-8.15zm30 32.69 22.62-1.87-1.72-38.52-22.64 1.26zm.75 17 1.51 34.25a83.52 83.52 0 0 1 22.72.42l-1.61-36.54zm17.36-120.58c-.433-6.13-5.672-10.8-11.812-10.53-6.14.272-10.947 5.385-10.838 11.53l2.05 46.5 22.64-1.31zm82.54 20.19c1.945-5.83-1.109-12.149-6.886-14.247-5.777-2.098-12.174.788-14.424 6.507L318 124.575l21.15 8.2zm-18.29 50.4-21.15-8.2-15.62 43 21.41 7.45zm-55 85.06a63.82 63.82 0 0 1 21.28 7.84l12.59-34.67-21.42-7.45zm106.42-21c5.037-3.722 6.102-10.823 2.38-15.86-3.722-5.037-10.823-6.102-15.86-2.38l-27.18 20.08 14.41 17.55zm-68.65 50.72 28.7-21.21-14.41-17.55-26.69 19.72c6.79 5.16 11.27 11.71 12.38 19.01zm-53 21.46c20.78 0 36.31-9.38 36.31-17.76s-15.53-17.76-36.31-17.76-36.31 9.38-36.31 17.76 15.47 17.72 36.26 17.72z"/>
      </svg>`)
        },
        {
            key: 'bone-spear',
            name: 'Bone Spear',
            power_category: 'attack',
            icon: 'data:image/svg+xml;base64,' + btoa(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
        <path fill="currentColor" d="M256 32L96 192l80 80L256 192l80 80L416 192 256 32z"/>
      </svg>`)
        },
        {
            key: 'undead-resilience',
            name: 'Undead Resilience',
            power_category: 'defense',
            icon: 'data:image/svg+xml;base64,' + btoa(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
        <path fill="currentColor" d="M256 0C114.6 0 0 114.6 0 256s114.6 256 256 256s256-114.6 256-256S397.4 0 256 0z"/>
      </svg>`)
        }
    ],
    'martial-memories': [
        {
            key: 'coordinated-strike',
            name: 'Coordinated Strike',
            power_category: 'attack',
            icon: 'data:image/svg+xml;base64,' + btoa(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
        <path fill="currentColor" d="m83.5 25-32 64v87c-.67 15.934 3.847 27.945 13.793 37.816 3.442 3.367 7.892 6.805 13.102 10.227L83.5 89l5.344 141.326c7.778 4.3 16.61 8.477 26.064 12.344.194.08.397.155.592.234V89l-32-64zm216.666 0C281.833 25 263.5 61.667 263.5 98.334c0 17.585 4.223 35.16 10.635 48.7 9.11 1.493 18.938 3.565 29.187 6.19 4.395-7.873 14.92-14.213 40.178-16.87V72.577C319.173 60.896 300.166 38.2 300.166 25zm146.668 0c0 13.2-19.007 35.896-43.334 47.576v63.78c43.31 4.554 43.334 19.928 43.334 35.31 18.333 0 36.666-36.665 36.666-73.332C483.5 61.667 465.167 25 446.834 25zM361.5 50v122.852a369.79 369.79 0 0 1 24 11.148V50h-24zm-127 72.92-58.45 61.9 58.45 58.453V208h9c34.25 0 90.23 12.187 135.408 30.67 22.59 9.24 42.344 19.89 55.385 32.646 6.52 6.38 11.518 13.45 13.514 21.65.867 3.562.914 7.297.414 11.014 7.95-19.23 4.975-35.52-5.345-51.625-11.208-17.49-31.88-33.91-56.424-47.478C337.367 177.743 272.5 162 243.5 162h-9v-39.08zm-195.72 71.1c-7.95 19.23-4.975 35.52 5.345 51.625 11.208 17.49 31.88 33.91 56.424 47.478C149.633 320.257 214.5 336 243.5 336h9v39.08l58.45-61.9-58.45-58.453V290h-9c-34.25 0-90.23-12.187-135.408-30.67-22.59-9.24-42.344-19.89-55.385-32.646-6.52-6.38-11.518-13.45-13.514-21.65-.867-3.562-.914-7.297-.414-11.014zm322.72 57.212V368h24V261.23a276.984 276.984 0 0 0-13.408-5.9c-3.446-1.41-7-2.766-10.592-4.098zm-310 29.862v41.44h23.17l.885-23.39c-8.66-5.593-16.772-11.594-24.055-18.05zm40.313 27.767.517 13.675h23.17v-1.777c-8.056-3.678-15.987-7.64-23.66-11.88l-.028-.017zM28.5 340.536V360h110v-19.465h-110zM63.5 375v80c-8 0-28 32 20 32s28-32 20-32v-80h-40zm298 11v94h24v-94h-24z"/>
      </svg>`)
        },
        {
            key: 'tactical-advance',
            name: 'Tactical Advance',
            power_category: 'movement',
            icon: 'data:image/svg+xml;base64,' + btoa(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
        <path fill="currentColor" d="M256 48L64 240l48 48 128-128v304h64V160l128 128 48-48L256 48z"/>
      </svg>`)
        },
        {
            key: 'battle-fury',
            name: 'Battle Fury',
            power_category: 'buff',
            icon: 'data:image/svg+xml;base64,' + btoa(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
        <path fill="currentColor" d="M256 16L96 176l160 160 160-160L256 16z"/>
      </svg>`)
        }
    ]
};

const mockLoadouts: PowerLoadout[] = [
    {
        key: 'skeletal-boon',
        name: 'Skeletal Boon',
        flavorText: 'Rattling bones and grinning skulls',
        powers: mockPowers['skeletal-boon'],
        selectionCount: 1,
        locked: false,
        replaceWithSpeciesPowers: false
    },
    {
        key: 'martial-memories',
        name: 'Martial Memories',
        flavorText: 'Half-remember martial prowess',
        powers: mockPowers['martial-memories'],
        selectionCount: 1,
        locked: false,
        replaceWithSpeciesPowers: false
    }
];

const mockSkeleton: Monster = {
    key: 'skeleton',
    name: 'Skeleton',
    image: '../img/monsters/skeleton.webp',
    backgroundImage: '../img/backgrounds/textures/undead-painting.webp',
    creature_type: 'Undead',
    size: 'Medium',
    cr: 'CR 1/4',
    tag_line: 'A fearsome undead warrior',
    loadouts: mockLoadouts
};

export class MockPowerStore implements PowerStore {

    getPowerLoadouts(monsterKey: string): PowerLoadout[] {
        // // Simulate async behavior
        // await new Promise(resolve => setTimeout(resolve, 100));

        // For this mock, return the same loadouts for any monster
        return mockLoadouts;
    }
}

export class MockMonsterStore implements MonsterStore {
    getMonster(key: string): Monster {
        // Simulate async behavior
        // await new Promise(resolve => setTimeout(resolve, 100));

        // For this mock, return the skeleton monster for any key
        return mockSkeleton;
    }
}

// Function to initialize the mock power store
export function initializeMockPowerStore(): MockPowerStore {
    return new MockPowerStore();
}

export function initializeMockMonsterStore(): MockMonsterStore {
    return new MockMonsterStore();
}
