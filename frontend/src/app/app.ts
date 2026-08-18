import {
  Component,
  ElementRef,
  inject,
  ViewChild,
} from '@angular/core';
import {
  FormsModule,
} from '@angular/forms';
import {
  HttpErrorResponse,
} from '@angular/common/http';
import { marked } from 'marked';

import {
  ChatService,
} from './chat/chat.service';
import {
  ChatMessage,
} from './chat/chat.types';


@Component({
  selector: 'app-root',
  imports: [
    FormsModule,
  ],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  private readonly chatService = inject(ChatService);

  @ViewChild('messagesContainer')
  private messagesContainer?: ElementRef<HTMLDivElement>;

  input = '';

  messages: ChatMessage[] = [];

  conversationId: string | null = null;

  isSending = false;

  errorMessage = '';

  readonly suggestions = [
    'What services can Neura Solutions help with?',
    'How can ERP improve business operations?',
    'What business processes can be automated?',
  ];

  renderMarkdown(content: string): string {
    return marked.parse(content, { async: false }) as string;
  }

  useSuggestion(
    suggestion: string,
  ): void {
    this.input = suggestion;
  }

  sendMessage(): void {
    const message = this.input.trim();

    if (
      !message
      || this.isSending
    ) {
      return;
    }

    this.errorMessage = '';

    this.messages.push({
      role: 'user',
      content: message,
    });

    this.input = '';
    this.isSending = true;

    this.scrollToBottom();

    this.chatService.sendMessage(
      message,
      this.conversationId,
    ).subscribe({
      next: (response) => {
        this.conversationId = (
          response.conversation_id
        );

        this.messages.push({
          role: 'assistant',
          content: response.message,
        });

        this.isSending = false;

        this.scrollToBottom();
      },

      error: (
        error: HttpErrorResponse,
      ) => {
        this.isSending = false;

        if (error.status === 429) {
          this.errorMessage = (
            'Too many messages were sent. '
            + 'Please wait a moment and try again.'
          );

          return;
        }

        if (error.status === 404) {
          this.conversationId = null;

          this.errorMessage = (
            'This chat session has expired. '
            + 'Please start a new chat.'
          );

          return;
        }

        if (error.status === 503) {
          this.errorMessage = (
            'Neura AI is temporarily unavailable. '
            + 'Please try again shortly.'
          );

          return;
        }

        this.errorMessage = (
          'Something went wrong. '
          + 'Please try again.'
        );
      },
    });
  }

  handleKeydown(
    event: KeyboardEvent,
  ): void {
    if (
      event.key === 'Enter'
      && !event.shiftKey
    ) {
      event.preventDefault();

      this.sendMessage();
    }
  }

  newChat(): void {
    this.messages = [];
    this.conversationId = null;
    this.input = '';
    this.errorMessage = '';
    this.isSending = false;
  }

  private scrollToBottom(): void {
    setTimeout(() => {
      const element = (
        this.messagesContainer?.nativeElement
      );

      if (!element) {
        return;
      }

      element.scrollTop = (
        element.scrollHeight
      );
    });
  }
}
