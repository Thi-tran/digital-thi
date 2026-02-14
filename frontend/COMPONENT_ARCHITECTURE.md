# Digital Thi Frontend - Component Architecture

This project follows **Airbnb JavaScript/React Guidelines** for frontend development with a focus on reusable components and clean architecture.

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Home page (uses ChatPage component)
│   ├── chat-page.tsx       # Main chat page component
│   └── globals.css         # Global styles
├── components/
│   ├── Avatar.tsx          # Avatar component
│   ├── Button.tsx          # Button component (variants: primary, secondary, suggestion)
│   ├── Header.tsx          # Header component
│   ├── Message.tsx         # Chat message component
│   ├── InputField.tsx      # Text input with icon support
│   ├── SuggestionGrid.tsx  # Grid of suggestion buttons
│   ├── ChatSection.tsx     # Wrapper for chat content sections
│   └── index.ts            # Barrel export for components
├── hooks/
│   ├── useConversation.ts  # Conversation state management hook
│   └── index.ts            # Barrel export for hooks
├── constants/
│   └── suggestions.ts      # App constants and initial suggestions
├── types/
│   └── index.ts            # TypeScript type definitions
```

## Development Practices

### 1. **Component Design Principles**

- **Single Responsibility**: Each component has one clear purpose
- **Reusability**: Components are designed to be used in multiple contexts
- **Composability**: Components can be easily combined
- **Prop-based Configuration**: Components accept props for customization

### 2. **Naming Conventions**

- **Components**: PascalCase (e.g., `Button.tsx`, `ChatPage.tsx`)
- **Hooks**: camelCase with `use` prefix (e.g., `useConversation.ts`)
- **Types**: PascalCase with `Interface` suffix (e.g., `ButtonProps`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `INITIAL_SUGGESTIONS`)

### 3. **File Organization**

```
component-name/
├── component.tsx       # Component implementation
├── component.types.ts  # Component-specific types
├── component.test.tsx  # Component tests (future)
└── index.ts           # Barrel export
```

### 4. **Type Safety**

- All components are fully typed with TypeScript
- Props interfaces are defined for each component
- Type definitions are centralized in `types/index.ts`

### 5. **Component Standards**

Every component follows this pattern:

```typescript
import React from 'react';

interface ComponentProps {
  // Required props
  children?: React.ReactNode;
  className?: string;
  // Custom props
}

export const ComponentName: React.FC<ComponentProps> = ({
  children,
  className = '',
  ...props
}) => {
  return (
    // JSX
  );
};

export default ComponentName;
```

## Components

### Avatar
Displays a circular image avatar.
- **Props**: `src`, `alt`, `size` ('sm', 'md', 'lg'), `className`

### Button
Reusable button with multiple variants.
- **Variants**: `primary`, `secondary`, `suggestion`
- **Sizes**: `sm`, `md`, `lg`
- **Props**: `variant`, `size`, `isLoading`, standard HTML button attributes

### Header
Application header with avatar and title.
- **Props**: `title`, `avatarSrc`, `avatarAlt`

### Message
Chat message component with avatar support.
- **Props**: `content`, `isUser`, `avatarSrc`, `avatarAlt`, `timestamp`

### InputField
Text input with optional icon/button support.
- **Props**: `icon`, `onSubmit`, `isLoading`, standard HTML input attributes
- **Keyboard**: Submits on Enter key

### SuggestionGrid
Grid layout for suggestion buttons.
- **Props**: `suggestions`, `onSelect`, `isLoading`
- **Responsive**: 1 column on mobile, 2 columns on tablet+

### ChatSection
Wrapper component for chat content sections.
- **Props**: `title`, `subtitle`, `children`

## Hooks

### useConversation
Manages conversation state and history.

```typescript
const { messages, addMessage, isLoading, setIsLoading } = useConversation();
```

## Styling

- **Framework**: Tailwind CSS v4
- **Design System**: Dark mode supported via `dark:` prefix
- **Colors**: Zinc palette for primary, Blue for actions
- **Spacing**: 4px base unit with Tailwind spacing scale
- **Animations**: Custom animations for loading states

## Best Practices

1. **Props Destructuring**: Always destructure props for clarity
2. **Default Props**: Use default values in destructuring
3. **Component Composition**: Build complex UIs from simple components
4. **Accessibility**: Use semantic HTML and ARIA labels
5. **Responsiveness**: Design mobile-first with Tailwind breakpoints
6. **Performance**: Use `React.memo` for expensive re-renders (as needed)
7. **Error Handling**: Validate props and handle edge cases
8. **Dark Mode**: Utilize Tailwind's dark mode utilities

## Getting Started

### Install Dependencies
```bash
cd frontend
pnpm install
```

### Run Development Server
```bash
pnpm dev
```

Visit `http://localhost:3000` to see the application.

### Build for Production
```bash
pnpm build
pnpm start
```

## Future Enhancements

- [ ] Component tests with Jest/React Testing Library
- [ ] Storybook for component documentation
- [ ] Component variants and compositions
- [ ] Performance optimization with React.memo
- [ ] Error boundary implementation
- [ ] Accessibility audit and improvements
- [ ] Backend API integration
