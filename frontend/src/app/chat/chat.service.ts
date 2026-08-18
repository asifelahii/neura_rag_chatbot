import {
  inject,
  Injectable,
} from '@angular/core';
import {
  HttpClient,
} from '@angular/common/http';

import {
  ChatRequest,
  ChatResponse,
} from './chat.types';


@Injectable({
  providedIn: 'root',
})
export class ChatService {
  private readonly http = inject(HttpClient);

  sendMessage(
    message: string,
    conversationId: string | null,
  ) {
    const request: ChatRequest = {
      message,
      conversation_id: conversationId,
    };

    return this.http.post<ChatResponse>(
      '/api/v1/chat',
      request,
    );
  }
}
