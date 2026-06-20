const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function connectEventStream(
  onEvent: (event: Record<string, unknown>) => void,
  onError?: (error: Event) => void
): EventSource {
  const source = new EventSource(`${API_BASE}/events/stream`);

  source.addEventListener("orqestra_event", (e: MessageEvent) => {
    try {
      const data = JSON.parse(e.data);
      onEvent(data);
    } catch {
      // ignore parse errors
    }
  });

  source.onerror = (err) => {
    if (onError) onError(err);
  };

  return source;
}
