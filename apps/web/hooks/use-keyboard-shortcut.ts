"use client";

import { useEffect } from "react";

export function useKeyboardShortcut(
  keyCombo: string,
  callback: (e: KeyboardEvent) => void,
  options: { ctrlOrCmd?: boolean } = {}
) {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      const isCmdOrCtrl = event.metaKey || event.ctrlKey;
      if (options.ctrlOrCmd && !isCmdOrCtrl) return;

      if (event.key.toLowerCase() === keyCombo.toLowerCase()) {
        event.preventDefault();
        callback(event);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [keyCombo, callback, options]);
}
