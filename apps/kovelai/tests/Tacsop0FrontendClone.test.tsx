import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import Tacsop0FrontendClone from '../components/Tacsop0FrontendClone';

describe('Tacsop0FrontendClone', () => {
  it('renders the component', () => {
    render(<Tacsop0FrontendClone />);
    expect(screen.getByText('TACSOP 0 Clone')).toBeDefined();
    expect(screen.getByLabelText('Email')).toBeDefined();
    expect(screen.getByLabelText('Password')).toBeDefined();
  });
});
