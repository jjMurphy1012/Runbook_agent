import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, test, vi } from "vitest";
import { apiClient } from "../api/client";
import LoginPage from "./LoginPage";

vi.mock("../api/client", () => ({
  apiClient: { post: vi.fn() },
}));

describe("LoginPage", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  test("submits credentials, stores token, calls onLogin", async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { token: "tok-123", username: "alice" },
    });
    const onLogin = vi.fn();
    const user = userEvent.setup();

    render(<LoginPage onLogin={onLogin} />);

    await user.type(screen.getByPlaceholderText("Username"), "alice");
    await user.type(screen.getByPlaceholderText("Password"), "pw");
    await user.click(screen.getByRole("button", { name: "Login" }));

    await waitFor(() => expect(onLogin).toHaveBeenCalledWith("tok-123", "alice"));
    expect(apiClient.post).toHaveBeenCalledWith("/auth/login", {
      username: "alice",
      password: "pw",
    });
    expect(localStorage.getItem("token")).toBe("tok-123");
  });

  test("shows error message on failed authentication", async () => {
    vi.mocked(apiClient.post).mockRejectedValueOnce({
      response: { data: { message: "Bad credentials" } },
    });
    const user = userEvent.setup();

    render(<LoginPage onLogin={vi.fn()} />);

    await user.type(screen.getByPlaceholderText("Username"), "alice");
    await user.type(screen.getByPlaceholderText("Password"), "wrong");
    await user.click(screen.getByRole("button", { name: "Login" }));

    expect(await screen.findByText("Bad credentials")).toBeInTheDocument();
    expect(localStorage.getItem("token")).toBeNull();
  });

  test("toggles to register mode and hits /auth/register", async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { token: "tok-new", username: "bob" },
    });
    const user = userEvent.setup();

    render(<LoginPage onLogin={vi.fn()} />);

    await user.click(screen.getByRole("button", { name: /Need an account/ }));
    await user.type(screen.getByPlaceholderText("Username"), "bob");
    await user.type(screen.getByPlaceholderText("Password"), "pw");
    await user.click(screen.getByRole("button", { name: "Register" }));

    await waitFor(() =>
      expect(apiClient.post).toHaveBeenCalledWith("/auth/register", {
        username: "bob",
        password: "pw",
      }),
    );
  });
});
