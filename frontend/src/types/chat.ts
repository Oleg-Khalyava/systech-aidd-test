/**
 * Типы для Chat API
 */

export type ChatMode = 'normal' | 'admin';
export type MessageRole = 'user' | 'assistant';

export interface ChatMessage {
    id: string;
    role: MessageRole;
    content: string;
    timestamp: string;
    sql?: string; // для admin режима
}

export interface ChatRequest {
    user_id: number;
    message: string;
    mode: ChatMode;
}

export interface ChatResponse {
    message: string;
    sql?: string;
}

export interface ChatHistoryMessage {
    id: number;
    role: MessageRole;
    content: string;
    created_at: string;
}

export interface ChatHistoryResponse {
    messages: ChatHistoryMessage[];
}

