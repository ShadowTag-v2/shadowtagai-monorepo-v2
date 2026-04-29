import { useState } from 'react';

/**
 * PromptInput
 * Port of Claude Code's Prompt Input React component for the IDE extension.
 * Features: Multi-line support, slash command recognition, history traversal.
 */
export const PromptInput: React.FC<{ onSubmit: (text: string) => void }> = ({ onSubmit }) => {
  const [input, setInput] = useState('');
  const [history, setHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (input.trim()) {
        onSubmit(input);
        setHistory((prev) => [...prev, input]);
        setInput('');
        setHistoryIndex(-1);
      }
    } else if (e.key === 'ArrowUp') {
      if (historyIndex < history.length - 1) {
        const newIndex = historyIndex + 1;
        setHistoryIndex(newIndex);
        setInput(history[history.length - 1 - newIndex]);
      }
    } else if (e.key === 'ArrowDown') {
      if (historyIndex > 0) {
        const newIndex = historyIndex - 1;
        setHistoryIndex(newIndex);
        setInput(history[history.length - 1 - newIndex]);
      } else if (historyIndex === 0) {
        setHistoryIndex(-1);
        setInput('');
      }
    }
  };

  return (
    <div className="agnt-prompt-input-container">
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Message AGNT or type '/' for commands..."
        rows={Math.min(Math.max(input.split('\n').length, 1), 10)}
      />
      <div className="prompt-footer">
        <span className="hint">Shift + Enter for new line</span>
      </div>
    </div>
  );
};
