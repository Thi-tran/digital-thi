import { useRef, useState, useEffect, RefObject } from 'react';

interface UseChatScrollOptions {
  messagesLength: number;
  lastUserMessageRef: RefObject<HTMLDivElement | null>;
}

interface UseChatScrollReturn {
  scrollContainerRef: RefObject<HTMLDivElement | null>;
  showSpacer: boolean;
  triggerSpacer: () => void;
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

      // Only remove the spacer when the user has scrolled well past the real
      // content — more than double of a screen into the spacer zone.
      // This creates a buffer and avoids a sudden layout jump on small scrolls.
      const distanceFromBottom = container.scrollHeight - container.scrollTop - container.clientHeight;
      if (distanceFromBottom > container.clientHeight * 2) {
        setShowSpacer(false);
      }
    };

    container.addEventListener('scroll', handleScroll, { passive: true });
    return () => container.removeEventListener('scroll', handleScroll);
  }, []);

  // When a new message is added (not the first), show spacer and scroll the user message to the top
  useEffect(() => {
    if (messagesLength > prevMessagesLengthRef.current && lastUserMessageRef.current && scrollContainerRef.current) {
      isProgrammaticScrollRef.current = true;

      // Only show spacer from the second message onwards
      if (prevMessagesLengthRef.current > 1) {
        setShowSpacer(true);
      }

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

  return { scrollContainerRef, showSpacer, triggerSpacer: () => { if (messagesLength > 1) setShowSpacer(true); } };
}
