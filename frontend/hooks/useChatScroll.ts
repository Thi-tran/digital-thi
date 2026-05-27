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
  const [showSpacer, setShowSpacer] = useState(false);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const prevMessagesLengthRef = useRef(messagesLength);
  const isProgrammaticScrollRef = useRef(false);
  // The scrollTop at the time we scrolled the question to the top
  const scrolledToRef = useRef<number>(0);

  useEffect(() => {
    const container = scrollContainerRef.current;
    if (!container) return;

    const handleScroll = () => {
      if (isProgrammaticScrollRef.current) return;
      if (!showSpacer) return;

      // Remove spacer once user scrolls back up past the question position,
      // with a minimum buffer of one screen height for short answers.
      const threshold = scrolledToRef.current - container.clientHeight;
      if (container.scrollTop < threshold) {
        setShowSpacer(false);
      }
    };

    container.addEventListener('scroll', handleScroll, { passive: true });
    return () => container.removeEventListener('scroll', handleScroll);
  }, [showSpacer]);

  // When a new message is added, show spacer and scroll user message to top
  useEffect(() => {
    if (messagesLength > prevMessagesLengthRef.current && lastUserMessageRef.current && scrollContainerRef.current) {
      isProgrammaticScrollRef.current = true;

      if (prevMessagesLengthRef.current > 1) {
        setShowSpacer(true);
      }

      const container = scrollContainerRef.current;
      const msgEl = lastUserMessageRef.current;
      const containerTop = container.getBoundingClientRect().top;
      const msgTop = msgEl.getBoundingClientRect().top;
      const offset = msgTop - containerTop + container.scrollTop;
      container.scrollTo({ top: offset - 10, behavior: 'smooth' });

      // Record where we scrolled to — removing spacer triggers when user scrolls above this
      scrolledToRef.current = offset - 10;

      setTimeout(() => { isProgrammaticScrollRef.current = false; }, 2000);
    }
    prevMessagesLengthRef.current = messagesLength;
  }, [messagesLength, lastUserMessageRef]);

  return {
    scrollContainerRef,
    showSpacer,
    triggerSpacer: () => { if (messagesLength > 1) setShowSpacer(true); },
  };
}
