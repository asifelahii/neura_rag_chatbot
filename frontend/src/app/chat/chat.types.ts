export interface ChatRequest {
  message: string;
  conversation_id: string | null;
}


export interface ChatResponse {
  success: boolean;
  conversation_id: string;
  message: string;
  mode: string;
}


export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}
