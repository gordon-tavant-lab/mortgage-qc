import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { Modal } from "../Modal";

describe("Modal", () => {
  it("renders children when open", () => {
    render(
      <Modal open onClose={vi.fn()} title="Test Modal">
        <div>child content</div>
      </Modal>
    );
    expect(screen.getByText("child content")).toBeInTheDocument();
    expect(screen.getByText("Test Modal")).toBeInTheDocument();
  });

  it("renders nothing when closed", () => {
    render(
      <Modal open={false} onClose={vi.fn()}>
        <div>child content</div>
      </Modal>
    );
    expect(screen.queryByText("child content")).not.toBeInTheDocument();
  });

  it("calls onClose on scrim click", () => {
    const onClose = vi.fn();
    const { container } = render(
      <Modal open onClose={onClose}>
        <div>child content</div>
      </Modal>
    );
    fireEvent.click(container.firstChild as Element);
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("does not call onClose on inner-panel click", () => {
    const onClose = vi.fn();
    render(
      <Modal open onClose={onClose}>
        <div>child content</div>
      </Modal>
    );
    fireEvent.click(screen.getByText("child content"));
    expect(onClose).not.toHaveBeenCalled();
  });

  it("calls onClose on Escape key", () => {
    const onClose = vi.fn();
    render(
      <Modal open onClose={onClose}>
        <div>child content</div>
      </Modal>
    );
    fireEvent.keyDown(window, { key: "Escape" });
    expect(onClose).toHaveBeenCalledTimes(1);
  });
});
