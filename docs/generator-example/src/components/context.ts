
import { createContext } from '@lit/context';
import { PowerStore } from './powers';

export const powerContext = createContext<PowerStore>('powers');