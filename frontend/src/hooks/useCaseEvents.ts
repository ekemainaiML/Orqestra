"use client";
import { useEffect, useRef, useState } from "react";
import { connectEventStream } from "@/lib/sse";
import type { WorkflowEvent } from "@/lib/types";

export function useCaseEvents(caseId: string) {
  const [events, setEvents] = useState<WorkflowEvent[]>([]);
  const sourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    sourceRef.current = connectEventStream((event) => {
      if (event.case_id === caseId) {
        setEvents((prev) => [...prev, event as unknown as WorkflowEvent]);
      }
    });

    return () => {
      sourceRef.current?.close();
    };
  }, [caseId]);

  return events;
}
