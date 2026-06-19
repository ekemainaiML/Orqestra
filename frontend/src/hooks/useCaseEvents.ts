"use client";
import { useEffect, useRef, useState } from "react";
import { connectEventStream } from "@/lib/sse";

export function useCaseEvents(caseId: string) {
  const [events, setEvents] = useState<Record<string, unknown>[]>([]);
  const sourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    sourceRef.current = connectEventStream((event) => {
      if (event.case_id === caseId) {
        setEvents((prev) => [...prev, event]);
      }
    });

    return () => {
      sourceRef.current?.close();
    };
  }, [caseId]);

  return events;
}
