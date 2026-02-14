import React from 'react';

type ButtonVariant = 'primary' | 'secondary' | 'suggestion';
type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  children: React.ReactNode;
  isLoading?: boolean;
}

const variantStyles = {
  primary:
    'bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800 transition-colors',
  secondary:
    'bg-zinc-200 text-zinc-900 hover:bg-zinc-300 active:bg-zinc-400 transition-colors dark:bg-zinc-700 dark:text-zinc-100 dark:hover:bg-zinc-600',
  suggestion:
    'bg-zinc-800 text-zinc-100 hover:bg-zinc-700 active:bg-zinc-600 transition-colors text-sm font-medium',
};

const sizeStyles = {
  sm: 'px-3 py-2 text-sm',
  md: 'px-4 py-2.5 text-base',
  lg: 'px-6 py-3 text-lg',
};

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  children,
  isLoading = false,
  disabled = false,
  className = '',
  ...props
}) => {
  return (
    <button
      className={`rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? 'Loading...' : children}
    </button>
  );
};

export default Button;
