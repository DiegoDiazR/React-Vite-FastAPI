import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { jwtDecode } from 'jwt-decode';
import { User } from '../models/auth.model';

interface AuthState {
    token: string | null;
    user: User | null;
    isAuthenticated: boolean;
    login: (data: { user: User; token: string }) => void;
    logout: () => void;
    hasPermission: (permission: string) => boolean;
    checkTokenExpiration: () => void;
}

interface JwtPayload {
    exp?: number;
}

const isTokenExpired = (token: string): boolean => {
    try {
        const decoded = jwtDecode<JwtPayload>(token);
        if (!decoded.exp) return false;                    //validacion de expiracion del token jwt

        const currentTime = Date.now() / 1000;
        return decoded.exp < currentTime;
    } catch (error) {
        return true;
    }
};

export const useAuthStore = create<AuthState>()(
    persist(
        (set, get) => ({
            token: null,
            user: null,
            isAuthenticated: false,

            login: ({ user, token }) => {
                if (isTokenExpired(token)) {
                    console.error('Attempted to login with expired token');
                    return;
                }
                set({ token, user, isAuthenticated: true });
            },

            logout: () => {
                set({ token: null, user: null, isAuthenticated: false });
            },

            hasPermission: (permission: string) => {
                const { user } = get();
                return user?.permissions?.includes(permission) ?? false;
            },

            checkTokenExpiration: () => {
                const { token, logout } = get();
                if (token && isTokenExpired(token)) {
                    console.warn('Token expired, logging out.');
                    logout();
                }
            }
        }),
        {
            name: 'auth-storage',
            version: 1, // Versioning state to prevent hydration errors
            storage: createJSONStorage(() => localStorage),
            onRehydrateStorage: () => (state) => {
                if (state?.token && isTokenExpired(state.token)) {
                    console.warn('Hydrated token is expired, clearing session.');
                    state.logout();
                }
            }
        }
    )
);
