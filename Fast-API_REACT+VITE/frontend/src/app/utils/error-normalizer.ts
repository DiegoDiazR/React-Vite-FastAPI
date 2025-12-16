import { AxiosError } from 'axios';

export interface NormalizedError {
    message: string;
    code: string;
    type: 'network' | 'validation' | 'auth' | 'server' | 'unknown';
    details?: any;
}

/**
 * Normalizes errors from different sources into a consistent format
 * Maps HTTP status codes to i18n keys
 */
export const normalizeError = (error: unknown): NormalizedError => {
    // Network errors (no response from server)
    if (error instanceof AxiosError && !error.response) {
        return {
            message: 'errors.network',
            code: 'NETWORK_ERROR',
            type: 'network',
        };
    }

    // HTTP errors with response
    if (error instanceof AxiosError && error.response) {
        const status = error.response.status;
        const data = error.response.data;

        switch (status) {
            case 401:
                return {
                    message: 'errors.unauthorized',
                    code: 'UNAUTHORIZED',
                    type: 'auth',
                };

            case 403:
                return {
                    message: 'errors.forbidden',
                    code: 'FORBIDDEN',
                    type: 'auth',
                };

            case 422:
                return {
                    message: data?.message || 'errors.validation',
                    code: 'VALIDATION_ERROR',
                    type: 'validation',
                    details: data?.errors || data?.detail,
                };

            case 500:
            case 502:
            case 503:
                return {
                    message: 'errors.server',
                    code: 'SERVER_ERROR',
                    type: 'server',
                };

            default:
                return {
                    message: data?.message || 'errors.unknown',
                    code: `HTTP_${status}`,
                    type: 'unknown',
                    details: data,
                };
        }
    }

    // Unknown errors
    return {
        message: 'errors.unknown',
        code: 'UNKNOWN_ERROR',
        type: 'unknown',
        details: error,
    };
};
