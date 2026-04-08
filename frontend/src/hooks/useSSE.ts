import { useEffect, useRef, useState } from "react";

export type SSEMessage = {
  event: string;
  data: string;
  timestamp: number;
};

export function useSSE(url: string | null) {
  const [messages, setMessages] = useState<SSEMessage[]>([]);
  const [connected, setConnected] = useState(false);
  const sourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!url) return;

    const eventSource = new EventSource(url);
    sourceRef.current = eventSource;

    eventSource.onopen = () => setConnected(true);

    eventSource.onmessage = (event) => {
      setMessages((prev) => [
        ...prev,
        { event: "message", data: event.data, timestamp: Date.now() },
      ]);
    };

    const stages = ["triage", "evidence_collection", "diagnostic", "diagnostic_reflection", "remediation", "postmortem", "complete"];
    for (const stage of stages) {
      eventSource.addEventListener(stage, (event: MessageEvent) => {
        setMessages((prev) => [
          ...prev,
          { event: stage, data: event.data, timestamp: Date.now() },
        ]);
        if (stage === "complete") {
          eventSource.close();
          setConnected(false);
        }
      });
    }

    eventSource.onerror = () => {
      eventSource.close();
      setConnected(false);
    };

    return () => {
      eventSource.close();
      setConnected(false);
    };
  }, [url]);

  const clear = () => setMessages([]);

  return { messages, connected, clear };
}
