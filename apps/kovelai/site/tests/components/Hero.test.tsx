import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

// Mock next/image since jsdom can't handle it
vi.mock('next/image', () => ({
  default: (props: Record<string, unknown>) => {
    // biome-ignore lint/performance/noImgElement: Test mock for next/image — native img is intentional
    // biome-ignore lint/a11y/useAltText: Props spread includes alt from the component under test
    return <img {...props} />;
  },
}));

// Mock next/link
vi.mock('next/link', () => ({
  default: ({ children, ...props }: { children: React.ReactNode; [key: string]: unknown }) => {
    return <a {...props}>{children}</a>;
  },
}));

import Hero from '@/components/shared/Hero';

describe('Hero', () => {
  it('renders without crashing', () => {
    render(<Hero />);
    const heading = screen.getByRole('heading', { level: 1 });
    expect(heading).toBeInTheDocument();
  });

  it('contains call-to-action elements', () => {
    render(<Hero />);
    // Hero should have at least one interactive link or button
    const links = screen.getAllByRole('link');
    expect(links.length).toBeGreaterThan(0);
  });
});
