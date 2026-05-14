import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, test, vi } from "vitest";
import { apiClient } from "../api/client";
import DashboardPage from "./DashboardPage";

vi.mock("../api/client", () => ({
  apiClient: { get: vi.fn(), post: vi.fn() },
}));

const SAMPLE_ALERTS = [
  {
    id: "11111111-1111-1111-1111-111111111111",
    fingerprint: "fp1",
    ruleName: "mysql_pool_exhausted",
    category: "database",
    severity: "HIGH",
    status: "PENDING",
    message: "Pool at 96%",
    createdAt: "2026-05-14T00:00:00Z",
  },
  {
    id: "22222222-2222-2222-2222-222222222222",
    fingerprint: "fp2",
    ruleName: "cpu_high_load",
    category: "compute",
    severity: "CRITICAL",
    status: "RESOLVED",
    message: "CPU 98%",
    createdAt: "2026-05-14T00:01:00Z",
  },
];

describe("DashboardPage", () => {
  beforeEach(() => vi.clearAllMocks());

  test("renders alert cards from the API", async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: SAMPLE_ALERTS });

    render(<DashboardPage onSelectAlert={vi.fn()} />);

    expect(await screen.findByText("mysql_pool_exhausted")).toBeInTheDocument();
    expect(screen.getByText("cpu_high_load")).toBeInTheDocument();
    expect(screen.getByText("2 alerts")).toBeInTheDocument();
    expect(apiClient.get).toHaveBeenCalledWith("/alerts");
  });

  test("renders 0 alerts when the API errors", async () => {
    vi.mocked(apiClient.get).mockRejectedValueOnce(new Error("boom"));

    render(<DashboardPage onSelectAlert={vi.fn()} />);

    await waitFor(() => expect(screen.getByText("0 alerts")).toBeInTheDocument());
  });

  test("Run Agent triggers the alert and notifies parent", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: SAMPLE_ALERTS });
    vi.mocked(apiClient.post).mockResolvedValueOnce({ data: {} });
    const onSelect = vi.fn();
    const user = userEvent.setup();

    render(<DashboardPage onSelectAlert={onSelect} />);

    const runButton = await screen.findByRole("button", { name: "Run Agent" });
    await user.click(runButton);

    await waitFor(() =>
      expect(apiClient.post).toHaveBeenCalledWith(
        "/alerts/11111111-1111-1111-1111-111111111111/trigger",
      ),
    );
    expect(onSelect).toHaveBeenCalledWith("11111111-1111-1111-1111-111111111111");
  });
});
