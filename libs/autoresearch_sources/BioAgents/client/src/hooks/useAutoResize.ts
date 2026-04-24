import { useEffect, useRef } from 'preact/hooks';

/**
 * Custom hook for auto-resizing textarea
 * Automatically adjusts height based on content
 */
export function useAutoResize(_value: string, minRows = 1, maxRows = 10) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    // Reset height to recalculate
    textarea.style.height = 'auto';

    // Calculate the height
    const lineHeight = parseInt(getComputedStyle(textarea).lineHeight, 10) || 24;
    const minHeight = lineHeight * minRows;
    const maxHeight = lineHeight * maxRows;

    let newHeight = textarea.scrollHeight;

    // Apply min and max constraints
    newHeight = Math.max(newHeight, minHeight);
    newHeight = Math.min(newHeight, maxHeight);

    textarea.style.height = `${newHeight}px`;

    // Show scrollbar if content exceeds maxHeight
    if (textarea.scrollHeight > maxHeight) {
      textarea.style.overflowY = 'auto';
    } else {
      textarea.style.overflowY = 'hidden';
    }
  }, [minRows, maxRows]);

  return textareaRef;
}
