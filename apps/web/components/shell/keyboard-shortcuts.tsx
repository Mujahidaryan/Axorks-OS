"use client";

import { useKeyboardShortcut } from "@/hooks/use-keyboard-shortcut";

export function KeyboardShortcuts() {
  // Listeners for keyboard actions can be wired here
  useKeyboardShortcut("/", () => {
    // Help modal toggle
  }, { ctrlOrCmd: true });

  return null;
}
