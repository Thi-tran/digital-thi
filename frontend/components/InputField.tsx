import React from 'react';

interface InputFieldProps extends React.InputHTMLAttributes<HTMLInputElement> {
  icon?: React.ReactNode;
  onSubmit?: () => void;
  isLoading?: boolean;
}

export const InputField: React.FC<InputFieldProps> = ({
  icon,
  onSubmit,
  isLoading = false,
  className = '',
  ...props
}) => {
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !isLoading) {
      e.preventDefault();
      onSubmit?.();
    }
  };

  return (
    <div className="flex items-center gap-2 rounded-lg border border-zinc-300 bg-white px-4 py-2.5 dark:border-zinc-600 dark:bg-zinc-800">
      <input
        type="text"
        onKeyDown={handleKeyDown}
        className={`flex-1 bg-transparent outline-none text-zinc-900 placeholder-zinc-500 dark:text-zinc-100 dark:placeholder-zinc-400 ${className}`}
        {...props}
      />
      {icon && (
        <button
          onClick={onSubmit}
          disabled={isLoading}
          className="flex items-center justify-center text-zinc-500 hover:text-blue-600 disabled:opacity-50 dark:text-zinc-400 dark:hover:text-blue-400 transition-colors"
          aria-label="Send message"
        >
          {icon}
        </button>
      )}
    </div>
  );
};

export default InputField;
