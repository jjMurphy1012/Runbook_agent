import { act, renderHook } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { useSSE } from "./useSSE";

type Listener = (event: { data: string }) => void;

class MockEventSource {
  static instances: MockEventSource[] = [];
  url: string;
  closed = false;
  onopen: (() => void) | null = null;
  onerror: (() => void) | null = null;
  onmessage: ((e: { data: string }) => void) | null = null;
  private listeners: Record<string, Listener[]> = {};

  constructor(url: string) {
    this.url = url;
    MockEventSource.instances.push(this);
  }

  addEventListener(event: string, listener: Listener) {
    (this.listeners[event] ||= []).push(listener);
  }

  emit(event: string, data: string) {
    (this.listeners[event] || []).forEach((fn) => fn({ data }));
  }

  close() {
    this.closed = true;
  }
}

describe("useSSE", () => {
  beforeEach(() => {
    MockEventSource.instances = [];
    vi.stubGlobal("EventSource", MockEventSource);
  });
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test("does not open a connection when url is null", () => {
    renderHook(() => useSSE(null));
    expect(MockEventSource.instances).toHaveLength(0);
  });

  test("opens, marks connected, and accumulates stage events", () => {
    const { result } = renderHook(() => useSSE("http://x/stream/1?token=t"));
    const es = MockEventSource.instances[0];
    expect(es.url).toBe("http://x/stream/1?token=t");

    act(() => es.onopen?.());
    expect(result.current.connected).toBe(true);

    act(() => es.emit("triage", '{"severity":"HIGH"}'));
    act(() => es.emit("diagnostic", '{"root_cause":"x"}'));
    expect(result.current.messages.map((m) => m.event)).toEqual([
      "triage",
      "diagnostic",
    ]);
  });

  test("closes the source when the complete event arrives", () => {
    const { result } = renderHook(() => useSSE("http://x/stream/1"));
    const es = MockEventSource.instances[0];
    act(() => es.onopen?.());
    act(() => es.emit("complete", "{}"));
    expect(es.closed).toBe(true);
    expect(result.current.connected).toBe(false);
  });

  test("closes the source on error", () => {
    const { result } = renderHook(() => useSSE("http://x/stream/1"));
    const es = MockEventSource.instances[0];
    act(() => es.onopen?.());
    act(() => es.onerror?.());
    expect(es.closed).toBe(true);
    expect(result.current.connected).toBe(false);
  });

  test("closes the source on unmount", () => {
    const { unmount } = renderHook(() => useSSE("http://x/stream/1"));
    const es = MockEventSource.instances[0];
    unmount();
    expect(es.closed).toBe(true);
  });
});
