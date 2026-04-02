type SSELogViewerProps = {
  messages: string[];
};

export default function SSELogViewer({ messages }: SSELogViewerProps) {
  return (
    <div className="rounded-2xl bg-ink p-4 text-sm text-slate-100">
      {messages.map((message) => (
        <p key={message} className="border-b border-white/10 py-2 last:border-b-0">
          {message}
        </p>
      ))}
    </div>
  );
}
