export interface ConversationMessage {
  id: string;
  content: string;
  timestamp: Date;
  isUser: boolean;
}

export interface SuggestionButton {
  id: string;
  text: string;
}
