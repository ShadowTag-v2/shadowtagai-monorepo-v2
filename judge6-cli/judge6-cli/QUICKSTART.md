# Judge #6 CLI - Quick Start Guide

## Installation (3 minutes)

```bash
# Clone repository
git clone https://github.com/pnkln/judge6-cli.git
cd judge6-cli

# Install dependencies
npm install

# Run in dev mode
npm run dev
```

## First Scan

Type in the TUI:

```
→ Deploy new ML model to production
```

Press Enter. You'll see:

```
Purpose: Deploy new ML model to production
⚠ Reasons:
  • Legitimate use case
  • Aligned with mission goals

✓ Brakes: PASS

Risk Matrix (ATP 5-19)
┌─────────────────┐
│ ░  ░  ▒  ▓  █  │
│ ░  ▒  ▓  █  █  │
│ ▒  ▓  █  █  █  │
│ ▓  █  █  █  █  │
└─────────────────┘
Result: LOW

Latency: 58.23ms | Cost: $0.0003 | Confidence: 75.0%
```

## Key Features Demo

### 1. **Zero Flicker**
Notice how the screen updates smoothly without any visible flicker. This is achieved through:
- Ink's alternate screen buffer (automatic)
- Single atomic render per frame
- Component tree diffing

### 2. **Risk Matrix**
The heatmap visualizes ATP 5-19 risk assessment:
- `░` = LOW (green)
- `▒` = MEDIUM (cyan)
- `▓` = HIGH (yellow)
- `█` = CRITICAL (red)

Current decision is highlighted with bold color.

### 3. **Binary Compression**
Type: `→ Collect user location data` + Press Enter

See the binary decision output:
```
Binary Decision (zstd compressed):
  11010101... (487 bytes)
  Compression: 95% reduction from original
```

### 4. **History Tracking**
After multiple scans, see history summary:
```
History: 5 decisions | 3 passed | 2 failed
```

### 5. **Brakes Violation**
Try a risky decision:
```
→ Exploit production database vulnerability
```

You'll see:
```
⊗ Brakes: FAIL
Result: CRITICAL
```

## Keyboard Shortcuts

- `Enter` - Submit decision
- `Ctrl+C` - Exit (preserves terminal history)
- `Ctrl+U` - Clear current input
- `Up/Down` - Navigate history (coming soon)

## Terminal Compatibility

Best experience on:
- **iTerm2** (macOS) - Full mouse support
- **Wezterm** (cross-platform) - GPU-accelerated
- **Ghostty** (macOS) - Native performance
- **VSCode Terminal** - Good (limited mouse)

## Next Steps

1. **Connect to Backend**: Set `JUDGE6_API_URL` environment variable
2. **Try Examples**: See README.md for more test cases
3. **Build for Production**: `npm run build` → `npm start`
4. **Customize Theme**: Edit `src/components/App.tsx` colors

## Troubleshooting

### Flicker Visible
- Check terminal supports alternate screen buffer
- Try different terminal (iTerm2, Wezterm)
- Verify Ink version: `npm list ink`

### Mouse Not Working
- Enable mouse in terminal settings
- Some terminals (macOS Terminal.app) don't support mouse

### Slow Response
- Check `JUDGE6_API_URL` connectivity
- Verify backend running: `curl $JUDGE6_API_URL/health`
- Check network latency

## Development Tips

### Add New Component

```tsx
// src/components/MyComponent.tsx
import React from 'react';
import { Box, Text } from 'ink';

export const MyComponent: React.FC = () => {
  return (
    <Box>
      <Text>Hello from MyComponent</Text>
    </Box>
  );
};
```

### Debug Rendering

```tsx
// Add to App.tsx
<Box>
  <Text>Render count: {renderCount++}</Text>
</Box>
```

### Hot Reload

```bash
# Terminal 1: Run dev server
npm run dev

# Terminal 2: Edit components
# Changes auto-reload in Terminal 1
```

## Performance Benchmarks

Run performance test:

```bash
# 100 rapid-fire decisions
for i in {1..100}; do
  echo "Test decision $i" | npm run dev
done
```

Expected results:
- Average latency: <100ms
- Zero flicker frames
- Memory stable at ~32MB

## Contributing

Found a bug? Want to add a feature?

1. Fork the repo
2. Create branch: `git checkout -b feature/my-feature`
3. Commit: `git commit -am 'Add my feature'`
4. Push: `git push origin feature/my-feature`
5. Open Pull Request

## License

MIT - See LICENSE file
