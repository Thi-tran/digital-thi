import { useRef, useState, useEffect, RefObject } from 'react';

interface UseChatScrollOptions {
  messagesLength: number;
  lastUserMessageRef: RefObject<HTMLDivElement | null>;
}

interface UseChatScrollReturn {
  scrollContainerRef: RefObject<HTMLDivElement | null>;
  showSpacer: boolean;
}

export function useChatScroll({ messagesLength, lastUserMessageRef }: UseChatScrollOptions): UseChatScrollReturn {
  // Spacer is hidden on first load — only shown after user sends a message
  const [showSpacer, setShowSpacer] = useState(false);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const prevMessagesLengthRef = useRef(messagesLength);
  const isProgrammaticScrollRef = useRef(false);

  // Remove the spacer once the user manually scrolls up
  useEffect(() => {
    const container = scrollContainerRef.current;
    if (!container) return;

    const handleScroll = () => {
      if (isProgrammaticScrollRef.current) return;
      const atBottom = container.scrollHeight - container.scrollTop - container.clientHeight < 10;
      if (!atBottom) {
        setShowSpacer(false);
      }
    };

    container.addEventListener('scroll', handleScroll, { passive: true });
    return () => container.removeEventListener('scroll', handleScroll);
  }, []);

  // When a new message is added, show spacer and scroll the user message to the top
  useEffect(() => {
    if (messagesLength > prevMessagesLengthRef.current && lastUserMessageRef.current && scrollContainerRef.current) {
      setShowSpacer(true);
      isProgrammaticScrollRef.current = true;

      const container = scrollContainerRef.current;
      const msgEl = lastUserMessageRef.current;
      const containerTop = container.getBoundingClientRect().top;
      const msgTop = msgEl.getBoundingClientRect().top;
      const offset = msgTop - containerTop + container.scrollTop;
      container.scrollTo({ top: offset - 10, behavior: 'smooth' });

      // Release the lock after the smooth scroll animation
      setTimeout(() => { isProgrammaticScrollRef.current = false; }, 2000);
    }
    prevMessagesLengthRef.current = messagesLength;
  }, [messagesLength, lastUserMessageRef]);

  return { scrollContainerRef, showSpacer };
}
