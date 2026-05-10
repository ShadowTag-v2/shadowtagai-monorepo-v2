# TACSOP 0 Frontend Spec

## Overview
This component specification details the Shadcn UI implementation for the TACSOP 0 frontend clone.

## Components

### Card
Used for displaying individual pieces of content or features.
- Uses `shadcn/ui` Card components (`Card`, `CardHeader`, `CardTitle`, `CardDescription`, `CardContent`, `CardFooter`).

### Button
Standard buttons for actions.
- Uses `shadcn/ui` Button component with various variants (`default`, `outline`, `ghost`).

### Input
Standard text input fields for forms.
- Uses `shadcn/ui` Input component.

### Layout
The overall layout follows a clean, minimalist design with a centered container, responsive grid, and clear typography.

## Styling
- Tailwind CSS for utility-first styling.
- Custom colors and theme configured in `tailwind.config.ts`.
- `lucide-react` for iconography.
