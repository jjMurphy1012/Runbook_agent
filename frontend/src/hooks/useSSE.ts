import { useEffect, useState } from "react";

export function useSSE(url: string) {
  const [messages, setMessages] = useState<string[]>([]);

  useEffect(() => {
    const eventSource = new EventSource(url);
    eventSource.onmessage = (event) => {
      setMessages((current) => [...current, event.data]);
    };

    eventSource.onerror = () => {
      eventSource.close();
    };

    return () => eventSource.close();
  }, [url]);

  return messages;
}
