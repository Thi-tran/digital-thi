import { useRef, useState, useEffect, RefObject } from 'react';

interface UseChatScrollOptions {
  messagesLength: number;
  lastUserMessageRef: RefObject<HTMLDivElement | null>;
  lastBotMessageRef: RefObject<HTMLDivElement | null>;
}

interface UseChatScrollReturn {
  scrollContainerRef: RefObject<HTMLDivElement | null>;
  showSpacer: boolean;
  triggerSpacer: () => void;
}

export function useChatScroll({ messagesLength, lastUserMessageRef, lastBotMessageRef }: UseChatScrollOptions): UseChatScrollReturn {
  const [showSpacer, setShowSpacer] = useState(false);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const prevMessagesLengthRef = useRef(messagesLength);
  const isProgrammaticScrollRef = useRef(false);
  const scrolledToRef = useRef<number>(0);
  const lastScrollTopRef = useRef<number>(0);

  useEffect(() => {
    const container = scrollContainerRef.current;
    if (!container) return;

    const handleScroll = () => {
      if (isProgrammaticScrollRef.current) return;
      if (!showSpacer) return;

      const currentScrollTop = container.scrollTop;
      const scrollingDown = currentScrollTop > lastScrollTopRef.current;
      lastScrollTopRef.current = currentScrollTop;

      // If scrolling down, only remove spacer if the answer is taller than viewport
      if (scrollingDown) {
        if (lastBotMessageRef.current) {
          const botMsgHeight = lastBotMessageRef.current.offsetHeight;
          const viewportHeight = container.clientHeight;
          if (botMsgHeight > viewportHeight) {
            setShowSpacer(false);
          }
        }
        return;
      }

      // Scrolling up — remove spacer if past the threshold
      const threshold = scrolledToRef.current - container.clientHeight;
      if (currentScrollTop < threshold) {
        setShowSpacer(false);
      }
    };

    container.addEventListener('scroll', handleScroll, { passive: true });
    return () => container.removeEventListener('scroll', handleScroll);
  }, [showSpacer, lastBotMessageRef]);

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

      scrolledToRef.current = offset - 10;
      lastScrollTopRef.current = offset - 10;

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
